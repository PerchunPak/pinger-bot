class ServerInfo:
    def __init__(self, valid, alias, ip):
        self.valid = valid
        self.alias = alias
        self.ip = ip

    def __eq__(self, other):
        if not isinstance(other, ServerInfo):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return self.valid == other.valid and self.alias == other.alias and self.ip == other.ip
