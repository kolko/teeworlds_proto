#!/usr/bin/env python
# -*- coding: utf-8 -*-

import consts
from utils import *

class NetBaseType(object):
    def __init__(self, name):
        self.name = name

    def parse(self, data):
        return


class NetMessage(NetBaseType):
    def __init__(self, name, content):
        super(NetMessage, self).__init__(name)
        self.content = content
        self.number = getattr(consts, 'NETMSGTYPE_'+name.upper())
        for item in content:
            setattr(self, item.name, None)

    def parse(self, data):
        offset = 0
        res = {}
        for item in self.content:
            name = item.name
            val, ln = item.parse(data[offset:])
            offset += ln
            res[name] = val
        return res


class NetObject(NetMessage):
    def __init__(self, name, content):
        self.name = name
        self.content = content


class NetIntAny(NetBaseType):
    def parse(self, data):
        value, ln = get_int(data)
        return (value, ln)

    def validate(self, value):
        return True


class NetIntRange(NetIntAny):
    def __init__(self, name, fr, to):
        self.name = name
        self.fr = fr
        self.to = to

    def validate(self, value):
        return True


class NetBool(NetIntRange):
    def __init__(self, name):
        super(NetBool, self).__init__(name, -1, 2) # todo check 0,1!


class NetTick(NetIntRange):
    def __init__(self, name):
        super(NetTick, self).__init__(name, 0, max_int) # todo check  <  >


class Enum(NetBaseType):
    def __init__(self, name, values):
        super(Enum, self).__init__(name)
        self.values = values

    def parse(self, data):
        value, ln = get_int(data)
        print self.values
        return (value, ln)


class Flags(Enum):
    pass


class NetEnum(NetBaseType):
    def __init__(self, name, enum):
        super(NetEnum, self).__init__(name)
        self.enum = enum

    def parse(self, data):
        value, ln = get_int(data)
        value_str = self.enum.values[value]
        return (value_str, ln)


class NetFlag(Flags):
    pass


class NetArray(NetBaseType):
    def __init__(self, obj, count):
        super(NetArray, self).__init__(obj.name)
        self.obj = obj
        self.count = count

    def parse(self, data):
        offset = 0
        values = []
        for n in range(self.count):
            val, ln = self.obj.parse(data[offset:])
            offset += ln
            values.append(val)
        return (values, ln)


class NetString(NetBaseType):
    def parse(self, data):
        value, ln = get_string(data)
        return (value, ln)


class NetStringStrict(NetString):
    pass


class NetEvent(NetBaseType):
    def __init__(self, name, values):
        pass