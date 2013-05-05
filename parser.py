#!/usr/bin/env python
# -*- coding: utf-8 -*-

import struct
from twisted.internet.protocol import DatagramProtocol

from consts import *
from utils import *
from shared import huffman
HUF = huffman.CHuffman()
HUF.Init()
from packet import BasePacket


class Client(DatagramProtocol, object):
    def __init__(self, cl_host, cl_port, server):
        self.cl_host = cl_host
        self.cl_port = cl_port
        self.srv_host = server.srv_host
        self.srv_port = server.srv_port
        self.server = server

    def datagramReceived(self, data, (host, port)):
        """
        received from server to client
        """
        self.server_to_client_pkg(data)

    def send_to_server(self, data):
        self.transport.write(data, (self.srv_host, self.srv_port))

    def send_to_client(self, data):
        self.server.send_to_client(data, self.cl_host, self.cl_port)

    def client_to_server_pkg(self, data):
        self.send_to_server(data)

    def server_to_client_pkg(self, data):
        self.send_to_client(data)


class ClientParser(Client):
    def __init__(self, *args, **kwargs):
        super(ClientParser, self).__init__(*args, **kwargs)
        self.parser = Parser()

    def client_to_server_pkg(self, data):
        super(ClientParser, self).client_to_server_pkg(data)
        self.parser.process_package(data)

    def server_to_client_pkg(self, data):
        # super(ClientParser, self).server_to_client_pkg(data)
        data = self.parser.process_package(data)
        if data:
            self.send_to_client(data)


class Parser(object):
    base_packet = BasePacket()
    def process_package(self, data):
        self.base_packet.clear()
        if not self.base_packet.load_from_raw(data):
            print 'ERROR PARSE BASE_PACKET'
            print self.base_packet.parse_error
            return

        if self.base_packet.connless_data:
            return self.parse_connless(self.base_packet.connless_data)

        flags = self.base_packet.p_flags
        ack = self.base_packet.p_ack
        num_chunks = self.base_packet.p_num_chunks

        offset = 0
        data = self.base_packet.chunk_data

        return self.base_packet.build_raw()

    def parse_sys_msg(self, msg, data):
        pass

    def parse_game_msg(self, msg, data):
        #https://github.com/teeworlds/teeworlds/blob/master/src/game/client/gameclient.cpp#L481
        # print 'msg_id %s' % msg
        offset = 0
        if msg == NETMSGTYPE_SV_EXTRAPROJECTILE:
            num, ln = get_int(data[offset:])
            offset += ln
            project_file_list = []
            for k in range(num):
                p_file = {}
                X, ln = get_int(data[offset:])
                offset += ln
                Y, ln = get_int(data[offset:])
                offset += ln
                VelX, ln = get_int(data[offset:])
                offset += ln
                VelY, ln = get_int(data[offset:])
                offset += ln
                type, ln = get_int(data[offset:])
                offset += ln
                start_tick, ln = get_int(data[offset:])
                offset += ln
                p_file['m_X'] = X
                p_file['m_Y'] = Y
                p_file['m_VelX'] = VelX
                p_file['m_VelY'] = VelY
                p_file['m_Type'] = type
                p_file['m_StartTick'] = start_tick
                project_file_list.append(p_file)
            print project_file_list
            # m_pItems->AddExtraProjectile(&Proj);
        elif msg == NETMSGTYPE_SV_TUNEPARAMS:
            pass
        elif msg == NETMSGTYPE_SV_VOTEOPTIONLISTADD:
            pass
        elif msg == NETMSGTYPE_SV_GAMEMSG:
            #игровое сообщение
            game_msg_id, ln = get_int(data[offset:])
            offset += ln
            if game_msg_id not in range(len(gs_GameMsgList)):
                print 'ERROR! NETMSGTYPE_SV_GAMEMSG with unknown type of msg!!'
                return
            game_msg = gs_GameMsgList[game_msg_id]
            params = []
            for n in range(game_msg[1]):
                param, ln = get_int(data[offset:])
                offset += ln
                params.append(param)
            if game_msg[0] == DO_SPECIAL:
                if game_msg_id == GAMEMSG_CTF_DROP:
                    print 'Bip-Bip m_pSounds->Enqueue(CSounds::CHN_GLOBAL, SOUND_CTF_DROP);'
                    return
                if game_msg_id == GAMEMSG_CTF_RETURN:
                    print 'Bip-Bip m_pSounds->Enqueue(CSounds::CHN_GLOBAL, SOUND_CTF_RETURN);'
                    return
                if game_msg_id == GAMEMSG_TEAM_BALANCE_VICTIM:
                    #team_name = getTeamName(aParaI[0], m_GameInfo.m_GameFlags&GAMEFLAG_TEAMS)
                    team_name = str(params[0])
                    broadcast_msg = game_msg[2] % team_name
                    print 'm_pBroadcast->DoBroadcast! %s' % broadcast_msg
                    return
                if game_msg_id == GAMEMSG_CTF_GRAB:
                    print 'Bip-Bip! Comand %s get flag' % params[0]
                    return
                if game_msg_id == GAMEMSG_CTF_CAPTURE:
                    print 'Bip-Bip m_pSounds->Enqueue(CSounds::CHN_GLOBAL, SOUND_CTF_CAPTURE);'
                    #if (aParaI[2] <= 60*Client()->GameTickSpeed())
                    team_color = params[0] and "blue" or "red"
                    team_player = params[1]#m_aClients[clamp(aParaI[1], 0, MAX_CLIENTS-1)].m_aName
                    time = params[2] #aParaI[2]/(float)Client()->GameTickSpeed());
                    print 'm_pChat->AddLine'
                    print "The %s flag was captured by '%s' (%.2f seconds)" % (team_color, team_player, time)
                    return
                return
            try:
                game_message = game_msg[2].__mod__(tuple(params))
            except:
                print "ERROR! Wrong message %s with params %s" % (game_msg[2], str(params))
                return
            if game_msg[0] == DO_CHAT:
                print "m_pChat->AddLine"
                print game_message
            if game_msg[0] == DO_BROADCAST:
                print "m_pBroadcast->DoBroadcast"
                print game_message
            return

        elif msg == NETMSGTYPE_SV_CLIENTINFO:
            pass
        elif msg == NETMSGTYPE_SV_CLIENTDROP:
            pass
        # elif msg == NETMSGTYPE_SV_GAMEINFO:
        #     pass
        # elif msg == NETMSGTYPE_SV_SERVERSETTINGS:
        #     pass
        # elif msg == NETMSGTYPE_SV_TEAM:
        #     pass
        elif msg == NETMSGTYPE_SV_READYTOENTER:
            pass
        elif msg == NETMSGTYPE_SV_EMOTICON:
            print len(data)
            client_id, ln = get_int(data[offset:])
            offset += ln
            print len(data[offset:])
            emoticon_id, ln = get_int(data[offset:])
            offset += ln
            print 'Player %s do emoticon %s!' % (client_id, emoticon_id)
        elif msg == NETMSGTYPE_CL_EMOTICON:
            emoticon_id, ln = get_int(data)
            offset += ln
            print 'From client -- do emoticon %s!' % emoticon_id
        # elif msg == NETMSGTYPE_DE_CLIENTENTER:
        #     pass
        # elif msg == NETMSGTYPE_DE_CLIENTLEAVE:
        #     pass
        print secure_unpack_msg(msg, data)

    def print_data(self, data):
        pass
        # print ','.join(bin(x) for x in struct.unpack_from("!"+"B"*len(data), data))

    def parse_connless(self, data):
        if len(data) >= 0:
            pass
            #print 'CONNLESS data:', data