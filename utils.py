#!/usr/bin/env python
# -*- coding: utf-8 -*-

import struct
from consts import *


def get_int(buf):
    offset = 0
    (result,) = struct.unpack_from("!B", buf, offset=offset)
    offset += 1
    sing = result & 0b01000000
    byte = result
    result = result & 0b00111111
    while byte & 0b10000000:
        offset += 1
        (byte,) = struct.unpack_from("!B", buf, offset=offset)
        result = (result<<7) | (byte&0b01111111)
    if sing:
        result ^= -1
    return (result, offset)

def get_string(buf):
    pos = 0
    res = ""
    if not buf:
        print "error get_string"
        return ""
    (byte,) = struct.unpack_from("!B", buf, offset=pos)
    while byte:
        if pos+1 > len(buf):
            print 'ERROR get_string'
            return ""
        res += chr(byte)
        pos += 1
        (byte,) = struct.unpack_from("!B", buf, offset=pos)
    return (res, pos+1)

def get_raw(buf, size):
    # print size
    if size > len(buf):
        raise Exception('error get raw. len: %s, need: %s' % (len(buf), size))
    result = buf[:size]
    return (result, size)


def secure_unpack_msg(type, data, unpacker=False):
    res = {}

    print type,
    offset = 0
    res['m_pMsgFailedOn'] = ""
    if type == NETMSGTYPE_SV_MOTD:
        res['type_str'] = "NETMSGTYPE_SV_MOTD"
        message, ln = get_string(data[offset:])
        offset += ln
        res['m_pMessage'] = message
    elif type == NETMSGTYPE_SV_CHAT:
        res['type_str'] = "NETMSGTYPE_SV_CHAT"
        team, ln = get_int(data[offset:])
        offset += ln
        client_id, ln = get_int(data[offset:])
        offset += ln
        message, ln = get_string(data[offset:])
        offset += ln
        if team < TEAM_SPECTATORS or team > TEAM_BLUE:
            res['m_pMsgFailedOn'] += 'm_Team;'
        if client_id < -1 or client_id > MAX_CLIENTS-1:
            res['m_pMsgFailedOn'] += 'm_ClientID;'
        res['m_Team'] = team
        res['m_ClientID'] = client_id
        res['m_pMessage'] = message
    elif type == NETMSGTYPE_SV_TEAM:
        res['type_str'] = "NETMSGTYPE_SV_TEAM"
        client_id, ln = get_int(data[offset:])
        offset += ln
        team, ln = get_int(data[offset:])
        offset += ln
        silent, ln = get_int(data[offset:])
        offset += ln
        cooldown_tick, ln = get_int(data[offset:])
        offset += ln
        if team < TEAM_SPECTATORS or team > TEAM_BLUE:
            res['m_pMsgFailedOn'] += 'm_Team;'
        if client_id < -1 or client_id > MAX_CLIENTS-1:
            res['m_pMsgFailedOn'] += 'm_ClientID;'
        if silent not in (0, 1):
            res['m_pMsgFailedOn'] += 'm_Silent;'
        if cooldown_tick < 0 or cooldown_tick > max_int:
            res['m_pMsgFailedOn'] += 'm_CooldownTick;'
        res['m_Team'] = team
        res['m_ClientID'] = client_id
        res['m_Silent'] = silent
        res['m_CooldownTick'] = cooldown_tick
    elif type == NETMSGTYPE_SV_KILLMSG:
        res['type_str'] = "NETMSGTYPE_SV_KILLMSG"
        killer, ln = get_int(data[offset:])
        offset += ln
        victim, ln = get_int(data[offset:])
        offset += ln
        weapon, ln = get_int(data[offset:])
        offset += ln
        mode_special, ln = get_int(data[offset:])
        offset += ln
        if killer < -1 or killer > MAX_CLIENTS-1:
            res['m_pMsgFailedOn'] += 'm_Killer;'
        if victim < -1 or victim > MAX_CLIENTS-1:
            res['m_pMsgFailedOn'] += 'm_Victim;'
        if weapon < -3 or weapon > NUM_WEAPONS-1:
            res['m_pMsgFailedOn'] += 'm_Weapon;'
        res['m_Killer'] = killer
        res['m_Victim'] = victim
        res['m_Weapon'] = weapon
        res['m_ModeSpecial'] = mode_special
    elif type == NETMSGTYPE_SV_TUNEPARAMS:
        res['type_str'] = "NETMSGTYPE_SV_TUNEPARAMS"
        pass
    elif type == NETMSGTYPE_SV_EXTRAPROJECTILE:
        res['type_str'] = "NETMSGTYPE_SV_EXTRAPROJECTILE"
        pass
    elif type == NETMSGTYPE_SV_READYTOENTER:
        res['type_str'] = "NETMSGTYPE_SV_READYTOENTER"
        pass
    elif type == NETMSGTYPE_SV_WEAPONPICKUP:
        res['type_str'] = "NETMSGTYPE_SV_WEAPONPICKUP"
        weapon, ln = get_int(data[offset:])
        offset += ln
        if weapon < 0 or weapon > NUM_WEAPONS-1:
            res['m_pMsgFailedOn'] += 'm_Weapon;'
        res['m_Weapon'] = weapon
    elif type == NETMSGTYPE_SV_EMOTICON:
        res['type_str'] = "NETMSGTYPE_SV_EMOTICON"
        client_id, ln = get_int(data[offset:])
        offset += ln
        emoticon, ln = get_int(data[offset:])
        offset += ln
        if client_id < 0 or client_id > MAX_CLIENTS-1:
            res['m_pMsgFailedOn'] += 'm_ClientID;'
        if emoticon < 0 or emoticon > 16:
            res['m_pMsgFailedOn'] += 'm_Emoticon;'
        res['m_ClientID'] = client_id
        res['m_Emoticon'] = emoticon
    elif type == NETMSGTYPE_SV_VOTECLEAROPTIONS:
        res['type_str'] = "NETMSGTYPE_SV_VOTECLEAROPTIONS"
        pass
    elif type == NETMSGTYPE_SV_VOTEOPTIONLISTADD:
        res['type_str'] = "NETMSGTYPE_SV_VOTEOPTIONLISTADD"
        pass
    elif type == NETMSGTYPE_SV_VOTEOPTIONADD:
        res['type_str'] = "NETMSGTYPE_SV_VOTEOPTIONADD"
        description, ln = get_string(data[offset:])#CUnpacker::SANITIZE_CC|CUnpacker::SKIP_START_WHITESPACES
        offset += ln
        res['m_pDescription'] = description
    elif type == NETMSGTYPE_SV_VOTEOPTIONREMOVE:
        res['type_str'] = "NETMSGTYPE_SV_VOTEOPTIONREMOVE"
        description, ln = get_string(data[offset:])#CUnpacker::SANITIZE_CC|CUnpacker::SKIP_START_WHITESPACES
        offset += ln
        res['m_pDescription'] = description
    elif type == NETMSGTYPE_SV_VOTESET:
        res['type_str'] = "NETMSGTYPE_SV_VOTESET"
        client_id, ln = get_int(data[offset:])
        offset += ln
        type, ln = get_int(data[offset:])
        offset += ln
        timeout, ln = get_int(data[offset:])
        offset += ln
        description, ln = get_string(data[offset:])#CUnpacker::SANITIZE_CC|CUnpacker::SKIP_START_WHITESPACES);
        offset += ln
        reason, ln = get_string(data[offset:])#CUnpacker::SANITIZE_CC|CUnpacker::SKIP_START_WHITESPACES);
        offset += ln
        if client_id < -1 or client_id > MAX_CLIENTS-1:
            res['m_pMsgFailedOn'] += 'm_ClientID;'
        if type < 0 or type > 7:
            res['m_pMsgFailedOn'] += 'm_Type;'
        if timeout < 0 or timeout > 60:
            res['m_pMsgFailedOn'] += 'm_Timeout;'
        res['m_ClientID'] = client_id
        res['m_Type'] = type
        res['m_Timeout'] = timeout
        res['m_pDescription'] = description
    elif type == NETMSGTYPE_SV_VOTESTATUS:
        pass

# case NETMSGTYPE_SV_VOTESTATUS:
# {
# CNetMsg_Sv_VoteStatus *pMsg = (CNetMsg_Sv_VoteStatus *)m_aMsgData;
# (void)pMsg;
# pMsg->m_Yes = pUnpacker->GetInt();
# pMsg->m_No = pUnpacker->GetInt();
# pMsg->m_Pass = pUnpacker->GetInt();
# pMsg->m_Total = pUnpacker->GetInt();
# if(pMsg->m_Yes < 0 || pMsg->m_Yes > MAX_CLIENTS) { m_pMsgFailedOn = "m_Yes"; break; }
# if(pMsg->m_No < 0 || pMsg->m_No > MAX_CLIENTS) { m_pMsgFailedOn = "m_No"; break; }
# if(pMsg->m_Pass < 0 || pMsg->m_Pass > MAX_CLIENTS) { m_pMsgFailedOn = "m_Pass"; break; }
# if(pMsg->m_Total < 0 || pMsg->m_Total > MAX_CLIENTS) { m_pMsgFailedOn = "m_Total"; break; }
# } break;
# 
# case NETMSGTYPE_SV_SERVERSETTINGS:
# {
# CNetMsg_Sv_ServerSettings *pMsg = (CNetMsg_Sv_ServerSettings *)m_aMsgData;
# (void)pMsg;
# pMsg->m_KickVote = pUnpacker->GetInt();
# pMsg->m_KickMin = pUnpacker->GetInt();
# pMsg->m_SpecVote = pUnpacker->GetInt();
# pMsg->m_TeamLock = pUnpacker->GetInt();
# pMsg->m_TeamBalance = pUnpacker->GetInt();
# pMsg->m_PlayerSlots = pUnpacker->GetInt();
# if(pMsg->m_KickVote < 0 || pMsg->m_KickVote > 1) { m_pMsgFailedOn = "m_KickVote"; break; }
# if(pMsg->m_KickMin < 0 || pMsg->m_KickMin > MAX_CLIENTS) { m_pMsgFailedOn = "m_KickMin"; break; }
# if(pMsg->m_SpecVote < 0 || pMsg->m_SpecVote > 1) { m_pMsgFailedOn = "m_SpecVote"; break; }
# if(pMsg->m_TeamLock < 0 || pMsg->m_TeamLock > 1) { m_pMsgFailedOn = "m_TeamLock"; break; }
# if(pMsg->m_TeamBalance < 0 || pMsg->m_TeamBalance > 1) { m_pMsgFailedOn = "m_TeamBalance"; break; }
# if(pMsg->m_PlayerSlots < 0 || pMsg->m_PlayerSlots > MAX_CLIENTS) { m_pMsgFailedOn = "m_PlayerSlots"; break; }
# } break;
# 
    elif type == NETMSGTYPE_SV_CLIENTINFO:
        res['type_str'] = "NETMSGTYPE_SV_CLIENTINFO"
        client_id, ln = get_int(data[offset:])
        offset += ln
        local, ln = get_int(data[offset:])
        offset += ln
        team, ln = get_int(data[offset:])
        offset += ln
        player_name, ln = get_string(data[offset:])#CUnpacker::SANITIZE_CC|CUnpacker::SKIP_START_WHITESPACES
        offset += ln
        player_clan, ln = get_string(data[offset:])#CUnpacker::SANITIZE_CC|CUnpacker::SKIP_START_WHITESPACES
        offset += ln
        country, ln = get_int(data[offset:])
        offset += ln
        skin_part_names = []
        use_custom_colors = []
        skin_part_colors = []
        for n in range(6):
            skin_name, ln= get_string(data[offset:])#CUnpacker::SANITIZE_CC|CUnpacker::SKIP_START_WHITESPACES
            offset += ln
            skin_part_names.append(skin_name)
        for n in range(6):
            custom_color, ln = get_int(data[offset:])
            offset += ln
            use_custom_colors.append(custom_color)
            if custom_color not in (0, 1):
                res['m_pMsgFailedOn'] += 'm_aUseCustomColors[%s];'%n
        for n in range(6):
            part_color, ln = get_int(data[offset:])
            offset += ln
            skin_part_colors.append(part_color)
        if client_id < 0 or client_id > MAX_CLIENTS-1:
            res['m_pMsgFailedOn'] += 'm_ClientID;'
        if local < 0 or local > 1:
            res['m_pMsgFailedOn'] += 'm_Local;'
        if team < TEAM_SPECTATORS or team > TEAM_BLUE:
            res['m_pMsgFailedOn'] += 'm_Team;'
        res['m_ClientID'] = client_id
        res['m_Team'] = team
        res['m_pName'] = player_name
        res['m_pClan'] = player_clan
        res['m_Country'] = country
        res['m_apSkinPartNames'] = skin_part_names
        res['m_aUseCustomColors'] = use_custom_colors
        res['m_aSkinPartColors'] = skin_part_colors
    elif type == NETMSGTYPE_SV_GAMEINFO:
        res['type_str'] = "NETMSGTYPE_SV_GAMEINFO"
        game_flags, ln = get_int(data[offset:])
        offset += ln
        score_limit, ln = get_int(data[offset:])
        offset += ln
        time_limit, ln = get_int(data[offset:])
        offset += ln
        match_num, ln = get_int(data[offset:])
        offset += ln
        match_current, ln = get_int(data[offset:])
        offset += ln
        if game_flags & (GAMEFLAG_TEAMS|GAMEFLAG_FLAGS|GAMEFLAG_SURVIVAL) != game_flags:
            res['m_pMsgFailedOn'] += 'm_GameFlags;'
        if score_limit < 0 or score_limit > max_int:
            res['m_pMsgFailedOn'] += 'm_ScoreLimit;'
        if time_limit < 0 or time_limit > max_int:
            res['m_pMsgFailedOn'] += 'm_TimeLimit;'
        if match_num < 0 or match_num > max_int:
            res['m_pMsgFailedOn'] += 'm_MatchNum;'
        if match_current < 0 or match_current > max_int:
            res['m_pMsgFailedOn'] += 'm_MatchCurrent;'
        res['m_GameFlags'] = game_flags
        res['m_ScoreLimit'] = score_limit
        res['m_TimeLimit'] = time_limit
        res['m_MatchNum'] = match_num
        res['m_MatchCurrent'] = match_current
    elif type == NETMSGTYPE_SV_CLIENTDROP:
        res['type_str'] = "NETMSGTYPE_SV_CLIENTDROP"
        client_id, ln = get_int(data[offset:])
        offset += ln
        reason, ln = get_string(data[offset:])
        offset += ln
        if client_id < 0 or client_id > MAX_CLIENTS-1:
            res['m_pMsgFailedOn'] += 'm_ClientID;'
        res['m_ClientID'] = client_id
        res['m_pReason'] = reason

    return res

# case NETMSGTYPE_SV_GAMEMSG:
# {
# CNetMsg_Sv_GameMsg *pMsg = (CNetMsg_Sv_GameMsg *)m_aMsgData;
# (void)pMsg;
# } break;
# 
# case NETMSGTYPE_DE_CLIENTENTER:
# {
# CNetMsg_De_ClientEnter *pMsg = (CNetMsg_De_ClientEnter *)m_aMsgData;
# (void)pMsg;
# pMsg->m_pName = pUnpacker->GetString(CUnpacker::SANITIZE_CC|CUnpacker::SKIP_START_WHITESPACES);
# pMsg->m_Team = pUnpacker->GetInt();
# if(pMsg->m_Team < TEAM_SPECTATORS || pMsg->m_Team > TEAM_BLUE) { m_pMsgFailedOn = "m_Team"; break; }
# } break;
# 
# case NETMSGTYPE_DE_CLIENTLEAVE:
# {
# CNetMsg_De_ClientLeave *pMsg = (CNetMsg_De_ClientLeave *)m_aMsgData;
# (void)pMsg;
# pMsg->m_pName = pUnpacker->GetString(CUnpacker::SANITIZE_CC|CUnpacker::SKIP_START_WHITESPACES);
# pMsg->m_pReason = pUnpacker->GetString(CUnpacker::SANITIZE_CC|CUnpacker::SKIP_START_WHITESPACES);
# } break;
# 
# case NETMSGTYPE_CL_SAY:
# {
# CNetMsg_Cl_Say *pMsg = (CNetMsg_Cl_Say *)m_aMsgData;
# (void)pMsg;
# pMsg->m_Team = pUnpacker->GetInt();
# pMsg->m_pMessage = pUnpacker->GetString();
# if(pMsg->m_Team < 0 || pMsg->m_Team > 1) { m_pMsgFailedOn = "m_Team"; break; }
# } break;
# 
# case NETMSGTYPE_CL_SETTEAM:
# {
# CNetMsg_Cl_SetTeam *pMsg = (CNetMsg_Cl_SetTeam *)m_aMsgData;
# (void)pMsg;
# pMsg->m_Team = pUnpacker->GetInt();
# if(pMsg->m_Team < TEAM_SPECTATORS || pMsg->m_Team > TEAM_BLUE) { m_pMsgFailedOn = "m_Team"; break; }
# } break;
# 
# case NETMSGTYPE_CL_SETSPECTATORMODE:
# {
# CNetMsg_Cl_SetSpectatorMode *pMsg = (CNetMsg_Cl_SetSpectatorMode *)m_aMsgData;
# (void)pMsg;
# pMsg->m_SpectatorID = pUnpacker->GetInt();
# if(pMsg->m_SpectatorID < SPEC_FREEVIEW || pMsg->m_SpectatorID > MAX_CLIENTS-1) { m_pMsgFailedOn = "m_SpectatorID"; break; }
# } break;
# 
# case NETMSGTYPE_CL_STARTINFO:
# {
# CNetMsg_Cl_StartInfo *pMsg = (CNetMsg_Cl_StartInfo *)m_aMsgData;
# (void)pMsg;
# pMsg->m_pName = pUnpacker->GetString(CUnpacker::SANITIZE_CC|CUnpacker::SKIP_START_WHITESPACES);
# pMsg->m_pClan = pUnpacker->GetString(CUnpacker::SANITIZE_CC|CUnpacker::SKIP_START_WHITESPACES);
# pMsg->m_Country = pUnpacker->GetInt();
# pMsg->m_apSkinPartNames[0] = pUnpacker->GetString(CUnpacker::SANITIZE_CC|CUnpacker::SKIP_START_WHITESPACES);
# pMsg->m_apSkinPartNames[1] = pUnpacker->GetString(CUnpacker::SANITIZE_CC|CUnpacker::SKIP_START_WHITESPACES);
# pMsg->m_apSkinPartNames[2] = pUnpacker->GetString(CUnpacker::SANITIZE_CC|CUnpacker::SKIP_START_WHITESPACES);
# pMsg->m_apSkinPartNames[3] = pUnpacker->GetString(CUnpacker::SANITIZE_CC|CUnpacker::SKIP_START_WHITESPACES);
# pMsg->m_apSkinPartNames[4] = pUnpacker->GetString(CUnpacker::SANITIZE_CC|CUnpacker::SKIP_START_WHITESPACES);
# pMsg->m_apSkinPartNames[5] = pUnpacker->GetString(CUnpacker::SANITIZE_CC|CUnpacker::SKIP_START_WHITESPACES);
# pMsg->m_aUseCustomColors[0] = pUnpacker->GetInt();
# pMsg->m_aUseCustomColors[1] = pUnpacker->GetInt();
# pMsg->m_aUseCustomColors[2] = pUnpacker->GetInt();
# pMsg->m_aUseCustomColors[3] = pUnpacker->GetInt();
# pMsg->m_aUseCustomColors[4] = pUnpacker->GetInt();
# pMsg->m_aUseCustomColors[5] = pUnpacker->GetInt();
# pMsg->m_aSkinPartColors[0] = pUnpacker->GetInt();
# pMsg->m_aSkinPartColors[1] = pUnpacker->GetInt();
# pMsg->m_aSkinPartColors[2] = pUnpacker->GetInt();
# pMsg->m_aSkinPartColors[3] = pUnpacker->GetInt();
# pMsg->m_aSkinPartColors[4] = pUnpacker->GetInt();
# pMsg->m_aSkinPartColors[5] = pUnpacker->GetInt();
# if(pMsg->m_aUseCustomColors[0] < 0 || pMsg->m_aUseCustomColors[0] > 1) { m_pMsgFailedOn = "m_aUseCustomColors[0]"; break; }
# if(pMsg->m_aUseCustomColors[1] < 0 || pMsg->m_aUseCustomColors[1] > 1) { m_pMsgFailedOn = "m_aUseCustomColors[1]"; break; }
# if(pMsg->m_aUseCustomColors[2] < 0 || pMsg->m_aUseCustomColors[2] > 1) { m_pMsgFailedOn = "m_aUseCustomColors[2]"; break; }
# if(pMsg->m_aUseCustomColors[3] < 0 || pMsg->m_aUseCustomColors[3] > 1) { m_pMsgFailedOn = "m_aUseCustomColors[3]"; break; }
# if(pMsg->m_aUseCustomColors[4] < 0 || pMsg->m_aUseCustomColors[4] > 1) { m_pMsgFailedOn = "m_aUseCustomColors[4]"; break; }
# if(pMsg->m_aUseCustomColors[5] < 0 || pMsg->m_aUseCustomColors[5] > 1) { m_pMsgFailedOn = "m_aUseCustomColors[5]"; break; }
# } break;
# 
# case NETMSGTYPE_CL_KILL:
# {
# CNetMsg_Cl_Kill *pMsg = (CNetMsg_Cl_Kill *)m_aMsgData;
# (void)pMsg;
# } break;
# 
# case NETMSGTYPE_CL_READYCHANGE:
# {
# CNetMsg_Cl_ReadyChange *pMsg = (CNetMsg_Cl_ReadyChange *)m_aMsgData;
# (void)pMsg;
# } break;
# 
# case NETMSGTYPE_CL_EMOTICON:
# {
# CNetMsg_Cl_Emoticon *pMsg = (CNetMsg_Cl_Emoticon *)m_aMsgData;
# (void)pMsg;
# pMsg->m_Emoticon = pUnpacker->GetInt();
# if(pMsg->m_Emoticon < 0 || pMsg->m_Emoticon > 16) { m_pMsgFailedOn = "m_Emoticon"; break; }
# } break;
# 
# case NETMSGTYPE_CL_VOTE:
# {
# CNetMsg_Cl_Vote *pMsg = (CNetMsg_Cl_Vote *)m_aMsgData;
# (void)pMsg;
# pMsg->m_Vote = pUnpacker->GetInt();
# if(pMsg->m_Vote < -1 || pMsg->m_Vote > 1) { m_pMsgFailedOn = "m_Vote"; break; }
# } break;
# 
# case NETMSGTYPE_CL_CALLVOTE:
# {
# CNetMsg_Cl_CallVote *pMsg = (CNetMsg_Cl_CallVote *)m_aMsgData;
# (void)pMsg;
# pMsg->m_Type = pUnpacker->GetString(CUnpacker::SANITIZE_CC|CUnpacker::SKIP_START_WHITESPACES);
# pMsg->m_Value = pUnpacker->GetString(CUnpacker::SANITIZE_CC|CUnpacker::SKIP_START_WHITESPACES);
# pMsg->m_Reason = pUnpacker->GetString(CUnpacker::SANITIZE_CC|CUnpacker::SKIP_START_WHITESPACES);
# pMsg->m_Force = pUnpacker->GetInt();
# if(pMsg->m_Force < 0 || pMsg->m_Force > 1) { m_pMsgFailedOn = "m_Force"; break; }
# } break;
# 
# default:
# m_pMsgFailedOn = "(type out of range)";
# break;
# }
# 
# if(pUnpacker->Error())
# m_pMsgFailedOn = "(unpack error)";
# 
# if(m_pMsgFailedOn)
# return 0;
# m_pMsgFailedOn = "";
# return m_aMsgData;
# };