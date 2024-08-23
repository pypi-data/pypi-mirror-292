from uuid import UUID, uuid4

from os_ken.lib.dpid import str_to_dpid
from .event import EventReadRequest, EventModifyRequest


def _get_table_row(table, attr_name, attr_value, tables, many=False):
    sentinel = object()

    rows = get_table(table)(tables).rows.values()
    if attr_name is None:
        if not many:
            return list(rows)[:1].pop()
        return list(rows)

    items = []
    for row in rows:
        if attr_name is None:
            items.append(row)
        if getattr(row, attr_name, sentinel) == attr_value:
            items.append(row)
            if not many:
                return row
    if many:
        return items
    return None


def to_uuid(item):
    if isinstance(item, str):
        return item
    if isinstance(item, UUID):
        return str(item)
    if hasattr(item, 'uuid'):
        return to_uuid(item.uuid)
    raise ValueError


def to_uuids(items):
    if not isinstance(items, list):
        return to_uuids([items])
    return list(map(to_uuid, items))


def get_controller(attr_val=None, *, attr_name='target', **kwargs):
    def _reader_(tables):
        return _get_table_row('Controller', attr_name, attr_val, tables=tables, **kwargs)

    return _reader_


def get_bridge(attr_val=None, *, attr_name='name', **kwargs):
    def _reader_(tables):
        return _get_table_row('Bridge', attr_name, attr_val, tables=tables, **kwargs)

    return _reader_


def get_bridge_by_uuid(bridge_uuid):
    return get_bridge(bridge_uuid, attr_name='uuid')


def get_bridges(*args, attr_name=None, **kwargs):
    return get_bridge(*args, attr_name=attr_name, **kwargs, many=True)


def get_port(attr_val=None, *, attr_name='name', **kwargs):
    def _reader_(tables):
        return _get_table_row('Port', attr_name, attr_val, tables=tables, **kwargs)

    return _reader_


def get_iface(attr_val=None, *, attr_name='name', **kwargs):
    def _reader_(tables):
        return _get_table_row('Interface', attr_name, attr_val, tables=tables, **kwargs)

    return _reader_


def match_row(table, fn):
    def _reader_(tables):
        return next((r for r in get_table(table)(tables).rows.values() if fn(r)), None)

    return _reader_


def match_rows(table, fn):
    def _reader_(tables):
        return (r for r in get_table(table)(tables).rows.values() if fn(r))

    return _reader_


def row_by_name(name, table):
    return match_row(table, lambda row: row.name == name)


def row_by_uuid(uuid, table):
    return match_row(table, lambda row: row.uuid == uuid or str(row.uuid) == str(uuid))


def rows_by_external_id(key, value, table):
    return match_rows(table, lambda r: (key in r.external_ids and r.external_ids.get(key) == value))


def rows_by_other_config(key, value, table):
    return match_rows(table, lambda r: (key in r.other_config and r.other_config.get(key) == value))


def get_column_value(table, record, column):
    row = row_by_name(record, table)
    value = getattr(row, column, "")

    if isinstance(value, list) and len(value) == 1:
        value = value[0]

    return str(value)


def get_iface_by_name(name):
    return row_by_name(name, 'Interface')


def get_ifaces_by_external_id(key, value):
    return rows_by_external_id(key, value, 'Interface')


def get_ifaces_by_other_config(key, value):
    return rows_by_other_config(key, value, 'Interface')


def get_port_by_name(name):
    return row_by_name(name, 'Port')


def get_port_by_uuid(uuid):
    return row_by_uuid(uuid, 'Port')


def get_bridge_for_iface_name(iface_name):
    iface = row_by_name(iface_name, 'Interface')
    if iface:
        port = match_row('Port', lambda x: iface in x.interfaces)
        if port:
            return match_row('Bridge', lambda x: port in x.ports)


def get_table(name):
    def _reader_(tables):
        return tables[name]

    return _reader_


def get_switch():
    def _reader_(tables):
        rows = get_table('Open_vSwitch')(tables).rows

        if rows:
            return rows.get(list(rows.keys())[0])

        return None

    return _reader_


def get_bridge_by_datapath_id(datapath_id):
    def _match_fn(row):
        row_dpid = str_to_dpid(str(row.datapath_id[0]))
        return row_dpid == datapath_id

    return match_row('Bridge', _match_fn)


def get_datapath_ids_for_systemd_id(manager, system_id):
    def _get_dp_ids(tables):
        dp_ids = []

        bridges = tables.get('Bridge')

        if not bridges:
            return dp_ids

        for bridge in bridges.rows.values():
            datapath_ids = bridge.datapath_id
            dp_ids.extend(str_to_dpid(dp_id) for dp_id in datapath_ids)

        return dp_ids

    request = EventReadRequest(system_id, _get_dp_ids)
    reply = manager.send_request(request)
    return reply.result


def get_system_id_for_datapath_id(manager, datapath_id):
    def _get_dp_ids(tables):
        bridges = tables.get('Bridge')

        if not bridges:
            return None

        for bridge in bridges.rows.values():
            datapath_ids = [str_to_dpid(dp_id) for dp_id in bridge.datapath_id]

            if datapath_id in datapath_ids:
                row = get_switch()(tables)
                if row:
                    return row.external_ids.get('system-id')

        return None

    request = EventReadRequest(None, _get_dp_ids)
    reply = manager.send_request(request)

    for result in reply.result:
        if result[1]:
            return result[0]

    return None


def set_external_id(key, val, fn):
    val = str(val)

    def _modifier_(tables, *_):
        row = fn(tables)

        if not row:
            return None

        external_ids = row.external_ids
        external_ids[key] = val
        row.external_ids = external_ids

    return _modifier_


def set_iface_external_id(iface_name, key, val):
    return set_external_id(key, val, get_iface(iface_name))


def set_other_config(key, val, fn):
    val = str(val)

    def _modifier_(tables, *_):
        row = fn(tables)

        if not row:
            return None

        other_config = row.other_config
        other_config[key] = val
        row.other_config = other_config

    return _modifier_


def set_iface_other_config(iface_name, key, val):
    return set_other_config(key, val, get_iface(iface_name))


def del_external_id(key, fn):
    def _modifier_(tables, *_):
        row = fn(tables)

        if not row:
            return None

        external_ids = row.external_ids
        if key in external_ids:
            external_ids.pop(key)
            row.external_ids = external_ids

    return _modifier_


def del_iface_external_id(iface_name, key):
    return del_external_id(key, get_iface(iface_name))


def del_other_config(key, fn):
    def _modifier_(tables, *_):
        row = fn(tables)

        if not row:
            return None

        other_config = row.other_config
        if key in other_config:
            other_config.pop(key)
            row.other_config = other_config

    return _modifier_


def del_iface_other_config(iface_name, key):
    return del_other_config(key, get_iface(iface_name))


def del_port(bridge_name, fn):
    def _modifier_(tables, *_):
        bridge = get_bridge(bridge_name)(tables)

        if not bridge:
            return

        port = fn(tables)

        if not port:
            return

        ports = bridge.ports
        ports.remove(port)
        bridge.ports = ports

    return _modifier_


def del_port_by_uuid(bridge_name, port_uuid):
    return del_port(bridge_name, get_port(port_uuid, attr_name='uuid'))


def del_port_by_name(bridge_name, port_name):
    return del_port(bridge_name, get_port(port_name))


def set_controller(bridge_name, target, controller_info=None):
    controller_info = controller_info or {}

    def _modifier_(tables, insert):
        bridge = get_bridge(bridge_name)(tables)

        controller = get_controller(target)(tables)
        _uuid = None
        if not controller:
            _uuid = controller_info.get('uuid', uuid4())
            controller = insert(get_table('Controller')(tables), _uuid)
            controller.target = target
            controller.connection_mode = 'out-of-band'

        elif not controller.connection_mode:
            controller.connection_mode = 'out-of-band'

        if controller_info:
            for key, val in controller_info.items():
                if key in ['uuid']:
                    continue
                setattr(controller, key, val)

        bridge.controller = [controller]

        return _uuid

    return _modifier_


def create_port(bridge_name, port_info, iface_info=None):
    if iface_info is None:
        iface_info = {}

    if 'uuid' not in port_info:
        port_info['uuid'] = uuid4()

    if 'uuid' not in iface_info:
        iface_info['uuid'] = uuid4()

    def _modifier_(tables, insert):
        bridge = get_bridge(bridge_name)(tables)

        if not bridge:
            return

        default_port_name = 'port' + str(port_info['uuid'])

        if 'name' not in iface_info:
            iface_info['name'] = port_info.get('name', default_port_name)

        if 'type' not in iface_info:
            iface_info['type'] = ''

        if 'name' not in port_info:
            port_info['name'] = default_port_name

        iface = insert(get_table('Interface')(tables), iface_info['uuid'])
        for key, val in iface_info.items():
            if key in ['uuid']:
                continue
            setattr(iface, key, val)

        port = insert(get_table('Port')(tables), port_info['uuid'])
        for key, val in port_info.items():
            if key in ['uuid']:
                continue
            setattr(port, key, val)

        port.interfaces = [iface]

        if hasattr(bridge, 'ports'):
            bridge.ports += [port]
        else:
            bridge.ports = [port]

        return port_info['uuid'], iface_info['uuid']

    return _modifier_


def del_bridge(fn):
    def _modifier_(tables, *_):
        switch = get_switch()(tables)

        if not switch:
            return

        delete_bridges = fn(tables)

        if not delete_bridges:
            return
        elif not isinstance(delete_bridges, list):
            delete_bridges = [delete_bridges]

        delete_bridge_uuids = to_uuids(delete_bridges)
        switch.bridges = list(filter(lambda item: to_uuid(item) not in delete_bridge_uuids, switch.bridges))

    return _modifier_


def del_bridge_by_uuid(bridge_uuid):
    return del_bridge(get_bridge(bridge_uuid, attr_name='uuid'))


def del_bridge_by_name(bridge_name):
    return del_bridge(get_bridge(bridge_name))


def create_bridge(bridge_info, **kwargs):
    if 'uuid' not in bridge_info:
        bridge_info['uuid'] = uuid4()

    def _modifier_(tables, insert):
        switch = get_switch()(tables)

        if not switch:
            return

        default_bridge_name = 'bridge' + str(bridge_info['uuid'])

        if 'name' not in bridge_info:
            bridge_info['name'] = default_bridge_name

        bridge = insert(get_table('Bridge')(tables), bridge_info['uuid'])
        for key, val in bridge_info.items():
            if key in ['uuid']:
                continue
            setattr(bridge, key, val)

        port_info = kwargs.pop('port_info', {})
        port_info.setdefault('name', bridge_info['name'])
        iface_info = kwargs.pop('iface_info', {})
        iface_info.setdefault('type', 'internal')
        uuids = create_port(bridge_info['name'], port_info, iface_info, **kwargs)(tables, insert)

        if hasattr(switch, 'bridges'):
            switch.bridges += [bridge]
        else:
            switch.bridges = [bridge]

        return bridge_info['uuid'], *uuids

    return _modifier_


def get_manager(attr_val=None, *, attr_name='target', **kwargs):
    def _reader_(tables):
        return _get_table_row('Manager', attr_name, attr_val, tables=tables, **kwargs)

    return _reader_


def get_managers(*args, attr_name=None, **kwargs):
    return get_manager(*args, attr_name=attr_name, **kwargs, many=True)


def set_manager(target=None, manager_info=None):
    manager_info = manager_info or {}

    def _modifier_(tables, insert):
        if target is None:
            manager = get_manager(attr_name=None)(tables)
        else:
            manager = get_manager(target)(tables)
        _uuid = None
        if not manager:
            _uuid = manager_info.get('uuid', uuid4())
            manager = insert(get_table('Manager')(tables), _uuid)
            manager.target = target
            manager.connection_mode = 'out-of-band'

        if not manager.connection_mode:
            manager.connection_mode = 'out-of-band'

        if manager_info:
            for key, val in manager_info.items():
                if key in ['uuid']:
                    continue
                setattr(manager, key, val)

        return _uuid

    return _modifier_


class RequestFailed(Exception):
    pass


def send_request_read_and_get_result(manager, system_id, fn):
    res = manager.send_request(EventReadRequest(system_id, fn))
    return res.result


def send_request_modify_or_raise(manager, system_id, fn):
    res = manager.send_request(EventModifyRequest(system_id, fn))
    if res.status == 'unchanged':
        return
    if res.status != 'success':
        raise RequestFailed('%s: %s' % (res.status, res.err_msg), res)
    return res.status, res.insert_uuids
