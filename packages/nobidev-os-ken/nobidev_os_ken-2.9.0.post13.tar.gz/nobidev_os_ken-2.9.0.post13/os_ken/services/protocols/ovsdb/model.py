from uuid import uuid4


class _UUIDDict(dict):
    def _uuidize(self):
        if '_uuid' not in self or self['_uuid'] is None:
            self['_uuid'] = uuid4()

    @property
    def uuid(self):
        self._uuidize()
        return self['_uuid']

    @uuid.setter
    def uuid(self, value):
        self['_uuid'] = value


class Row(_UUIDDict):
    @property
    def delete(self):
        if '_delete' in self and self['_delete']:
            return True

        return False

    @delete.setter
    def delete(self, value):
        self['_delete'] = value
