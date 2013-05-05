#!/usr/bin/env python
# -*- coding: utf-8 -*-

import struct
from utils import *
from teewords_network import Messages


class ChunkMsg(object):
    def __init__(self):
        self.clean()

    def clean(self):
        self.parse_errors = ""

    def load_from_raw(self, data):
        offset = 0
        msg, ln = get_int(data)
        offset += ln
        sys = msg&1
        msg >>= 1

        if sys:
            pass
            # self.parse_sys_msg(msg, data[offset:])
        else:
            pass
            # self.parse_game_msg(msg, data[offset:])

            for mes in Messages:
                if mes.number == msg:
                    print mes.name + ': (' + str(len(data[offset:])) + ')',
                    res = mes.parse(data[offset:])
                    print str(res)
                    break

        return {'raw': data}

    def build_raw_from_data(self, data):
        return data['raw']


