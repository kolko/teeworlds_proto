#!/usr/bin/env python
# -*- coding: utf-8 -*-

import struct

from chunk_message import ChunkMsg

from shared import huffman
HUF = huffman.CHuffman()
HUF.Init()

PACKET_HEADER = '!BBB'
NET_PACKETHEADERSIZE = struct.calcsize(PACKET_HEADER)
NET_MAX_PACKETSIZE = 1400

NET_MAX_PAYLOAD = NET_MAX_PACKETSIZE-6
NET_MAX_CHUNKHEADERSIZE = 3
MAX_SNAPSHOT_PACKSIZE=900

NET_PACKETFLAG_CONTROL=1      #???
NET_PACKETFLAG_CONNLESS=2     #???? Наверное, когда идет подключение
NET_PACKETFLAG_RESEND=4       #хз, видать когда пакет повторно шлется
NET_PACKETFLAG_COMPRESSION=8  #сжатие блеадь

NET_CHUNKFLAG_VITAL = 1
MSGFLAG_VITAL=1


class BasePacket(object):
    def __init__(self):
        self.clear()
        self.ch_aggregator = ChunkAggregator()

    def clear(self):
        self.parse_error = ""

        self.p_ack = None
        self.p_num_chunks = None
        self.p_flags = None

        self.compression = None
        self.connless_data = None
        self.chunk_data = None

    def load_from_raw(self, data):
        """
        Parse raw packet data
        """
        offset = 0
        if (len(data) < NET_PACKETHEADERSIZE) or (len(data) > NET_MAX_PACKETSIZE):
            #дропаем кривой пакет
            self.parse_error = "Unstandart PACKET SIZE"
            return False
        #парсим заголовок
        flags_with_ack, ack_part, num_chunks = struct.unpack_from(PACKET_HEADER, data, offset=offset)
        offset += NET_PACKETHEADERSIZE
        flags = flags_with_ack>>4
        ack = ((flags_with_ack & 0b00001111) << 8 )| ack_part

        data_size = len(data[offset:])
        if data_size == 0:
            self.parse_error = "No data in packet"
            return False

        if flags & NET_PACKETFLAG_CONNLESS:
            self.connless_data = data[offset:]
            self.p_flags = NET_PACKETFLAG_CONNLESS
            self.p_ack = 0
            self.p_num_chunks = 0
            return True

        self.compression = False
        if flags & NET_PACKETFLAG_COMPRESSION:
            self.compression = True
            data = HUF.Decompress(data[offset:])
            offset = 0

        if flags & NET_PACKETFLAG_CONTROL:#неведомая хуйня
            self.chunk_data = data[offset:]
            self.p_flags = flags
            self.p_ack = ack
            self.p_num_chunks = num_chunks
            return True

        if len(data) > NET_MAX_PAYLOAD:
            self.parse_error = "Big payload NET_MAX_PAYLOAD"
            return False

        aggr = self.ch_aggregator.load_from_raw(data[offset:], num_chunks)
        self.chunk_data = self.ch_aggregator.build_raw()
        ###debug
        if data[offset:] != self.ch_aggregator.build_raw():
            print 'ERROR aggregator'
            print ','.join(bin(x) for x in struct.unpack_from("!"+"B"*len(data[offset:]), data[offset:]))
            print ','.join(bin(x) for x in struct.unpack_from("!"+"B"*len(self.ch_aggregator.build_raw()), self.ch_aggregator.build_raw()))
            self.chunk_data = data[offset:]
            return True
        ####
        self.p_flags = flags
        self.p_ack = ack
        self.p_num_chunks = self.ch_aggregator.num_chunks

        return True

    def build_raw(self):
        if not self.connless_data and not self.chunk_data:
            raise Exception('NO PAYLOAD IN PACKAGE')
        if self.connless_data and self.chunk_data:
            raise Exception(u'У пакета есть 2 типа данных. НЕ ВАЛИДНО!!!')
        if self.connless_data:
            #у CONNLESS сбрасываем всё лишнее
            p_flags = NET_PACKETFLAG_CONNLESS
            p_ack = 0
            p_num_chunks = 0
            compression = False
            payload = self.connless_data

        if self.chunk_data:
            p_num_chunks = self.p_num_chunks#todo: пока не дошли до чанков - не можем использовать
            p_flags = self.p_flags#тоже понятия не имеем что туда пихать
            p_ack = self.p_ack#аналогично
            payload = self.chunk_data

        if self.compression:
            payload = HUF.Compress(payload)

        flags_with_ack = p_flags<<4 | ( (self.p_ack>>8) & 0b00001111)
        ack_part = p_ack & 0b11111111

        header = struct.pack(PACKET_HEADER, flags_with_ack, ack_part, p_num_chunks)
        return header + payload


class ChunkAggregator(object):
    def __init__(self):
        self.clean()
        self.chunk_parser = Chuck()

    def clean(self):
        self.parse_error = ""
        self.chunks = []

    @property
    def num_chunks(self):
        return len(self.chunks)

    def load_from_raw(self, data, num_chunks):
        self.clean()
        offset = 0
        for chunk_num in range(num_chunks):
            chunk_data, ln = self.chunk_parser.data_from_raw(data[offset:])
            if not chunk_data:
                print self.chunk_parser.parse_error
                return False
            offset += ln
            self.chunks.append(chunk_data)
        return True

    def build_raw(self):
        return ''.join(self.chunk_parser.build_raw_from_data(data) for data in self.chunks)


class Chuck(object):
    def __init__(self):
        self.meggage_parser = ChunkMsg()
        self.clean()

    def clean(self):
        self.parse_error = ""

    def data_from_raw(self, data):
        self.clean()
        offset = 0
        if not data:
            self.self.parse_error += 'No chunk data'
            return (False, 0)

        flags_with_size, size_seq = struct.unpack_from("!BB", data, offset=offset)
        offset += 2
        flags = (flags_with_size>>6) & 0x03
        size = ((flags_with_size&0x3F)<<4) | (size_seq&0b1111)
        sequence = -1
        if flags & MSGFLAG_VITAL:
            seq = struct.unpack_from("!B", data, offset=offset)[0]
            offset += 1
            sequence = ((size_seq&0xC0)<<2) | seq

        if len(data[offset:]) < size:
            self.parse_error += 'ERROR! data < chuck_size\n'
            self.parse_error += bin(flags_with_size)+ ' ' + bin(size_seq) + '<--size' + str(len(data[offset:])) + ' '+ bin(len(data[offset:])) + '  ' + str(sequence)
            return (False, 0)

        raw_data = data[offset:size+offset]
        offset += size
        chunk_data = {
            'flags': flags,
            'sequence': sequence,
            # 'raw_data': raw_data,
            'message': self.meggage_parser.load_from_raw(raw_data),
        }
        return (chunk_data, offset)

    def build_raw_from_data(self, data):
        self.clean()
        flags = data['flags']
        sequence = data['sequence']
        # raw_data = data['raw_data']
        raw_data = self.meggage_parser.build_raw_from_data(data['message'])
        size = len(raw_data)

        flags_with_size = ((flags&0x03)<<6) | ((size>>4)&0x3F)
        size_seq = size & 0b1111
        if flags & MSGFLAG_VITAL:
            size_seq |= (sequence>>2)&0xC0
            sequence = sequence&0xFF
            header = struct.pack('!BBB', flags_with_size, size_seq, sequence)
        else:
            header = struct.pack('!BB', flags_with_size, size_seq)
        return header+raw_data

