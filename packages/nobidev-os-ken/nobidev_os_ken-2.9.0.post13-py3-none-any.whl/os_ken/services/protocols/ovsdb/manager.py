import socket
import ssl

from os_ken import cfg
from os_ken.base import app_manager
from os_ken.controller import handler
from os_ken.lib import hub
from os_ken.lib import ip
from .client import RemoteOvsdb
from .event import (
    EventNewOVSDBConnection,
    EventReadRequest, EventReadReply,
    EventModifyRequest, EventModifyReply,
)

opts = (
    cfg.StrOpt('schema', default='ptcp', help='OVSDB schema'),
    cfg.StrOpt('address', default='0.0.0.0', help='OVSDB address'),
    cfg.IntOpt('port', default=6640, help='OVSDB port'),
    cfg.IntOpt('probe-interval', help='OVSDB reconnect probe interval'),
    cfg.IntOpt('min-backoff', help='OVSDB reconnect minimum milliseconds between connection attempts'),
    cfg.IntOpt('max-backoff', help='OVSDB reconnect maximum milliseconds between connection attempts'),
    cfg.StrOpt('mngr-privkey', default=None, help='manager private key'),
    cfg.StrOpt('mngr-cert', default=None, help='manager certificate'),
    cfg.ListOpt('whitelist', default=[], help='Whitelist of address to allow to connect'),
    cfg.ListOpt('schema-tables', default=[], help='Tables in the OVSDB schema to configure'),
    cfg.ListOpt('schema-exclude-columns', default=[], help='Table columns in the OVSDB schema to filter out. Values should be in the format: <table>.<column>. Ex: Bridge.netflow,Interface.statistics')
)

cfg.CONF.register_opts(opts, 'ovsdb')


class OVSDB(app_manager.OSKenApp):
    _EVENTS = [EventNewOVSDBConnection, EventModifyRequest, EventReadRequest]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._address = self.CONF.ovsdb.address
        self._port = self.CONF.ovsdb.port
        self._probe_interval = self.CONF.ovsdb.probe_interval
        self._min_backoff = self.CONF.ovsdb.min_backoff
        self._max_backoff = self.CONF.ovsdb.max_backoff
        self._clients = {}

    def _accept(self, server):
        if self.CONF.ovsdb.whitelist:
            def check(address):
                if address in self.CONF.ovsdb.whitelist:
                    return True

                self.logger.debug('Connection from non-whitelist client '
                                  '(%s:%s)' % address)
                return False

        else:
            # noinspection PyUnusedLocal
            def check(address):
                return True

        while self.is_active:
            try:
                sock, client_address = server.accept()

            except Exception as ex:
                if self.is_active:
                    self.logger.exception('Error accepting connection: %s' % ex)
                    continue
                else:
                    break

            if not check(client_address[0]):
                sock.shutdown(socket.SHUT_RDWR)
                sock.close()
                continue

            if ip.valid_ipv6(client_address[0]):
                self.logger.debug(
                    'New connection from [%s]:%s' % client_address[:2])
            else:
                self.logger.debug(
                    'New connection from %s:%s' % client_address[:2])
            t = hub.spawn(self._start_remote, sock, client_address)
            self.threads.append(t)

    def _bulk_read_handler(self, ev):
        results = []

        # noinspection PyUnusedLocal
        def done(ctx, *args, **kwargs):
            if ctx in self.threads:
                self.threads.remove(ctx)
            results.append(ctx.wait())

        threads = []
        for c in self._clients.values():
            gt = hub.spawn(c.read_request_handler, ev, bulk=True)
            threads.append(gt)
            self.threads.append(gt)
            gt.link(done)

        hub.joinall(threads)
        rep = EventReadReply(None, results)
        self.reply_to_request(ev, rep)

    def _proxy_event(self, ev):
        system_id = ev.system_id
        client_name = RemoteOvsdb.instance_name(system_id)

        if client_name not in self._clients:
            self.logger.info('Unknown remote system_id %s' % system_id)
            return

        return self.send_event(client_name, ev)

    def _start_remote(self, sock, client_address, passive=True):
        schema_tables = cfg.CONF.ovsdb.schema_tables
        schema_ex_col = {}
        if cfg.CONF.ovsdb.schema_exclude_columns:
            for c in cfg.CONF.ovsdb.schema_exclude_columns:
                tbl, col = c.split('.')
                if tbl in schema_ex_col:
                    schema_ex_col[tbl].append(col)
                else:
                    schema_ex_col[tbl] = [col]

        app = RemoteOvsdb.factory(sock, client_address,
                                  probe_interval=self._probe_interval,
                                  min_backoff=self._min_backoff,
                                  max_backoff=self._max_backoff,
                                  schema_tables=schema_tables,
                                  schema_exclude_columns=schema_ex_col,
                                  passive=passive)

        if app:
            self._clients[app.name] = app
            app.start()
            ev = EventNewOVSDBConnection(app)
            self.send_event_to_observers(ev)

        else:
            try:
                sock.shutdown(socket.SHUT_RDWR)
            except Exception as ex:
                self.logger.exception('Error shutdown: %s' % ex)

            sock.close()

    def _listen(self):
        if ip.valid_ipv6(self._address):
            server = hub.listen(
                (self._address, self._port), family=socket.AF_INET6)
        else:
            server = hub.listen((self._address, self._port))
        key = self.CONF.ovsdb.mngr_privkey or self.CONF.ctl_privkey
        cert = self.CONF.ovsdb.mngr_cert or self.CONF.ctl_cert

        if key is not None and cert is not None:
            ssl_kwargs = dict(keyfile=key, certfile=cert, server_side=True)

            if self.CONF.ca_certs is not None:
                ssl_kwargs['cert_reqs'] = ssl.CERT_REQUIRED
                ssl_kwargs['ca_certs'] = self.CONF.ca_certs

            server = ssl.wrap_socket(server, **ssl_kwargs)

        self._server = server

        if ip.valid_ipv6(self._address):
            self.logger.info(
                'Listening on [%s]:%s for clients', self._address, self._port)
        else:
            self.logger.info(
                'Listening on %s:%s for clients', self._address, self._port)
        t = hub.spawn(self._accept, self._server)
        return t

    def _connect(self, retry=10):
        try:
            if ip.valid_ipv6(self._address):
                client = hub.connect(
                    (self._address, self._port), family=socket.AF_INET6)
            else:
                client = hub.connect((self._address, self._port))
        except ConnectionRefusedError as ex:
            if retry > 0:
                hub.sleep(1)
                return self._connect(retry=retry - 1)
            raise ex

        key = self.CONF.ovsdb.mngr_privkey or self.CONF.ctl_privkey
        cert = self.CONF.ovsdb.mngr_cert or self.CONF.ctl_cert

        if key is not None and cert is not None:
            ssl_kwargs = dict(keyfile=key, certfile=cert, server_side=True)

            if self.CONF.ca_certs is not None:
                ssl_kwargs['cert_reqs'] = ssl.CERT_REQUIRED
                ssl_kwargs['ca_certs'] = self.CONF.ca_certs

            client = ssl.wrap_socket(client, **ssl_kwargs)

        self._client = client

        if ip.valid_ipv6(self._address):
            self.logger.info(
                'Connecting to [%s]:%s', self._address, self._port)
        else:
            self.logger.info(
                'Connecting to %s:%s', self._address, self._port)
        t = hub.spawn(self._start_remote, client, client.getpeername(), passive=False)
        self.threads.append(t)
        return t

    def start(self):
        if cfg.CONF.ovsdb.schema == 'ptcp':
            t = self._listen()
        elif cfg.CONF.ovsdb.schema == 'tcp':
            t = self._connect()
        else:
            raise ValueError(cfg.CONF.ovsdb.schema)
        super().start()
        return t

    def stop(self):
        self.is_active = False

        if self.main_thread:
            hub.kill(self.main_thread)
            self.main_thread = None

        for c in self._clients.values():
            c.stop()

        super().stop()

    @handler.set_ev_cls(EventModifyRequest)
    def modify_request_handler(self, ev):

        system_id = ev.system_id
        client_name = RemoteOvsdb.instance_name(system_id)
        remote = self._clients.get(client_name)

        if not remote:
            msg = 'Unknown remote system_id %s' % system_id
            self.logger.info(msg)
            rep = EventModifyReply(system_id, None, None, msg)
            return self.reply_to_request(ev, rep)

        return remote.modify_request_handler(ev)

    @handler.set_ev_cls(EventReadRequest)
    def read_request_handler(self, ev):
        system_id = ev.system_id

        if system_id is None:
            # noinspection PyUnusedLocal
            def done(ctx, *args, **kwargs):
                if ctx in self.threads:
                    self.threads.remove(ctx)

            thread = hub.spawn(self._bulk_read_handler, ev)
            self.threads.append(thread)
            return thread.link(done)

        client_name = RemoteOvsdb.instance_name(system_id)
        remote = self._clients.get(client_name)

        if not remote:
            msg = 'Unknown remote system_id %s' % system_id
            self.logger.info(msg)
            rep = EventReadReply(system_id, None, msg)
            return self.reply_to_request(ev, rep)

        return remote.read_request_handler(ev)
