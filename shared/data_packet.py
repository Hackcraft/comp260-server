import json
from enum import Enum

from shared.data_tags import DataTags
from shared.login_tags import LoginTags

# https://stackoverflow.com/questions/24481852/serialising-an-enum-member-to-json
PUBLIC_ENUMS = {
    'DataTags': DataTags,
    'LoginTags': LoginTags
}

class EnumEncoder(json.JSONEncoder):
    def default(self, obj):
        if type(obj) in PUBLIC_ENUMS.values():
            return {"__enum__": str(obj)}
        return json.JSONEncoder.default(self, obj)

def as_enum(d):
    if "__enum__" in d:
        name, member = d["__enum__"].split(".")
        return getattr(PUBLIC_ENUMS[name], member)
    else:
        return d

class DataPacket():

    @staticmethod
    def separate(data):
        tag = ""
        msg = ""
        try:
            arr = json.loads(data, object_hook=as_enum)
            tag = arr['tag']
            msg = arr['msg']
        except Exception as e:
            print(e)
        return tag, msg

    @staticmethod
    def combine(tag: Enum, msg="none"):
        return json.dumps({"tag": tag, "msg": msg}, cls=EnumEncoder)
