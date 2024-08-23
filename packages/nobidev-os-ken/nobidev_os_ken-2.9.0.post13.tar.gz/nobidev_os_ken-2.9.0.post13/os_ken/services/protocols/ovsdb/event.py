from os_ken.controller import event as os_ken_event
from os_ken.controller import handler


class EventRowBase(os_ken_event.EventBase):
    def __init__(self, system_id, table, row, event_type):
        super().__init__()
        self.system_id = system_id
        self.table = table
        self.row = row
        self.event_type = event_type

    def __str__(self):
        return '%s<system_id=%s table=%s, uuid=%s>' % (self.__class__.__name__,
                                                       self.system_id,
                                                       self.table,
                                                       self.row['_uuid'])


class EventRowDelete(EventRowBase):
    def __init__(self, system_id, table, row):
        super().__init__(system_id, table, row, 'Deleted')


class EventRowInsert(EventRowBase):
    def __init__(self, system_id, table, row):
        super().__init__(system_id, table, row, 'Inserted')


class EventRowUpdate(os_ken_event.EventBase):
    def __init__(self, system_id, table, old, new):
        super().__init__()
        self.system_id = system_id
        self.table = table
        self.old = old
        self.new = new
        self.event_type = 'Updated'

    def __str__(self):
        return '%s<system_id=%s table=%s, uuid=%s>' % (self.__class__.__name__,
                                                       self.system_id,
                                                       self.table,
                                                       self.old['_uuid'])


class EventModifyRequest(os_ken_event.EventRequestBase):
    """ Dispatch a modify function to OVSDB

    `func` must be a callable that accepts an insert fucntion and the
    IDL.tables object. It can then modify the tables as needed. For inserts,
    specify a UUID for each insert, and return a tuple of the temporary
    UUID's. The execution of `func` will be wrapped in a single transaction
    and the reply will include a dict of temporary UUID to real UUID mappings.

    e.g.

        new_port_uuid = uuid.uuid4()

        def modify(tables, insert):
            bridges = tables['Bridge'].rows
            bridge = None
            for b in bridges:
                if b.name == 'my-bridge':
                    bridge = b

            if not bridge:
                return

            port = insert('Port', new_port_uuid)

            bridge.ports = bridge.ports + [port]

            return (new_port_uuid, )

        request = EventModifyRequest(system_id, modify)
        reply = send_request(request)

        port_uuid = reply.insert_uuids[new_port_uuid]
    """

    def __init__(self, system_id, func):
        super().__init__()
        self.dst = 'OVSDB'
        self.system_id = system_id
        self.func = func

    def __str__(self):
        return '%s<system_id=%s>' % (self.__class__.__name__, self.system_id)


class EventModifyReply(os_ken_event.EventReplyBase):
    def __init__(self, system_id, status, insert_uuids, err_msg):
        super().__init__()
        self.system_id = system_id
        self.status = status
        self.insert_uuids = insert_uuids
        self.err_msg = err_msg

    def __str__(self):
        return ('%s<system_id=%s, status=%s, insert_uuids=%s, error_msg=%s>'
                % (self.__class__.__name__,
                   self.system_id,
                   self.status,
                   self.insert_uuids,
                   self.err_msg))


class EventNewOVSDBConnection(os_ken_event.EventBase):
    def __init__(self, client):
        super().__init__()
        self.client = client

    def __str__(self):
        return '%s<system_id=%s>' % (self.__class__.__name__,
                                     self.client.system_id)

    @property
    def system_id(self):
        return self.client.system_id


class EventReadRequest(os_ken_event.EventRequestBase):
    def __init__(self, system_id: str, func: callable):
        super().__init__()
        self.system_id = system_id
        self.func = func
        self.dst = 'OVSDB'


class EventReadReply[T](os_ken_event.EventReplyBase):
    def __init__(self, system_id: str, result: T, err_msg: str = ''):
        super().__init__()
        self.system_id = system_id
        self.result = result
        self.err_msg = err_msg


class EventRowInsertedBase(EventRowInsert):
    def __init__(self, ev):
        super().__init__(ev.system_id, ev.table, ev.row)


class EventRowDeletedBase(EventRowDelete):
    def __init__(self, ev):
        super().__init__(ev.system_id, ev.table, ev.row)


class EventRowUpdatedBase(EventRowUpdate):
    def __init__(self, ev):
        super().__init__(ev.system_id, ev.table, ev.old, ev.new)


class EventPortInserted(EventRowInsertedBase):
    pass


class EventPortDeleted(EventRowDeletedBase):
    pass


class EventPortUpdated(EventRowUpdatedBase):
    pass


class EventInterfaceInserted(EventRowInsertedBase):
    pass


class EventInterfaceDeleted(EventRowDeletedBase):
    pass


class EventInterfaceUpdated(EventRowUpdatedBase):
    pass


handler.register_service(f'{__package__}.manager')
