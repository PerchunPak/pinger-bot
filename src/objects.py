class ServerInfo:
    def __init__(self, valid, alias, num_ip):
        self.valid = valid
        self.alias = alias
        self.num_ip = num_ip

    def __eq__(self, other):
        if not isinstance(other, ServerInfo):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return self.valid == other.valid and self.alias == other.alias and self.num_ip == other.num_ip
