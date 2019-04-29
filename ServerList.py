'''
    Basic hard coded server list class
'''

class ServerList:

    _servers = {
        "Italy | Dungeon experience (no pizza included)": ("188.164.131.220", 18202),
        "France | Dungeon experience (no baguette included)": ("91.121.50.14", 52902),
        "England | Dungeon experience (no chips included)": ("46.101.56.200", 9337),
        "Local loopback 127.0.0.1 (requires a locally run server)": ("127.0.0.1", 8222)
    }

    @classmethod
    def Names(cls):
        names = []
        for name in cls._servers:
            names.append(name)
        return names

    @classmethod
    def IPFromName(cls, name):
        if name in cls._servers:
            return cls._servers[name][0]
        else:
            return None

    @classmethod
    def PortFromName(cls, name):
        if name in cls._servers:
            return cls._servers[name][1]
        else:
            return None
