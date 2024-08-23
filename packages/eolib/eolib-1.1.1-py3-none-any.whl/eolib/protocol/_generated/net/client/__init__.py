# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

"""
Data structures generated from the [eo-protocol](https://github.com/cirras/eo-protocol/tree/master/xml/net/client/protocol.xml){target="_blank"} XML specification.

Warning:
  - This subpackage should not be directly imported. 
  - Instead, import [eolib.protocol.net.client][] (or the top-level `eolib`).
"""

from .welcome_request_client_packet import *
from .welcome_msg_client_packet import *
from .welcome_agree_client_packet import *
from .warp_take_client_packet import *
from .warp_accept_client_packet import *
from .walk_spec_client_packet import *
from .walk_player_client_packet import *
from .walk_admin_client_packet import *
from .walk_action import *
from .train_type import *
from .trade_request_client_packet import *
from .trade_remove_client_packet import *
from .trade_close_client_packet import *
from .trade_agree_client_packet import *
from .trade_add_client_packet import *
from .trade_accept_client_packet import *
from .talk_use_client_packet import *
from .talk_tell_client_packet import *
from .talk_request_client_packet import *
from .talk_report_client_packet import *
from .talk_player_client_packet import *
from .talk_open_client_packet import *
from .talk_msg_client_packet import *
from .talk_announce_client_packet import *
from .talk_admin_client_packet import *
from .stat_skill_take_client_packet import *
from .stat_skill_remove_client_packet import *
from .stat_skill_open_client_packet import *
from .stat_skill_junk_client_packet import *
from .stat_skill_add_client_packet import *
from .stat_id import *
from .spell_use_client_packet import *
from .spell_target_type import *
from .spell_target_self_client_packet import *
from .spell_target_other_client_packet import *
from .spell_target_group_client_packet import *
from .spell_request_client_packet import *
from .sit_request_client_packet import *
from .sit_action import *
from .shop_sell_client_packet import *
from .shop_open_client_packet import *
from .shop_create_client_packet import *
from .shop_buy_client_packet import *
from .refresh_request_client_packet import *
from .range_request_client_packet import *
from .quest_use_client_packet import *
from .quest_list_client_packet import *
from .quest_accept_client_packet import *
from .priest_use_client_packet import *
from .priest_request_client_packet import *
from .priest_open_client_packet import *
from .priest_accept_client_packet import *
from .players_request_client_packet import *
from .players_list_client_packet import *
from .players_accept_client_packet import *
from .player_range_request_client_packet import *
from .party_take_client_packet import *
from .party_request_client_packet import *
from .party_remove_client_packet import *
from .party_accept_client_packet import *
from .paperdoll_request_client_packet import *
from .paperdoll_remove_client_packet import *
from .paperdoll_add_client_packet import *
from .npc_range_request_client_packet import *
from .message_ping_client_packet import *
from .marriage_request_type import *
from .marriage_request_client_packet import *
from .marriage_open_client_packet import *
from .login_request_client_packet import *
from .locker_take_client_packet import *
from .locker_open_client_packet import *
from .locker_buy_client_packet import *
from .locker_add_client_packet import *
from .jukebox_use_client_packet import *
from .jukebox_open_client_packet import *
from .jukebox_msg_client_packet import *
from .item_use_client_packet import *
from .item_junk_client_packet import *
from .item_get_client_packet import *
from .item_drop_client_packet import *
from .init_init_client_packet import *
from .guild_use_client_packet import *
from .guild_tell_client_packet import *
from .guild_take_client_packet import *
from .guild_request_client_packet import *
from .guild_report_client_packet import *
from .guild_remove_client_packet import *
from .guild_rank_client_packet import *
from .guild_player_client_packet import *
from .guild_open_client_packet import *
from .guild_kick_client_packet import *
from .guild_junk_client_packet import *
from .guild_info_type import *
from .guild_create_client_packet import *
from .guild_buy_client_packet import *
from .guild_agree_client_packet import *
from .guild_accept_client_packet import *
from .global_remove_client_packet import *
from .global_player_client_packet import *
from .global_open_client_packet import *
from .global_close_client_packet import *
from .file_type import *
from .face_player_client_packet import *
from .emote_report_client_packet import *
from .door_open_client_packet import *
from .dialog_reply import *
from .connection_ping_client_packet import *
from .connection_accept_client_packet import *
from .citizen_request_client_packet import *
from .citizen_reply_client_packet import *
from .citizen_remove_client_packet import *
from .citizen_open_client_packet import *
from .citizen_accept_client_packet import *
from .chest_take_client_packet import *
from .chest_open_client_packet import *
from .chest_add_client_packet import *
from .character_take_client_packet import *
from .character_request_client_packet import *
from .character_remove_client_packet import *
from .character_create_client_packet import *
from .chair_request_client_packet import *
from .byte_coords import *
from .book_request_client_packet import *
from .board_take_client_packet import *
from .board_remove_client_packet import *
from .board_open_client_packet import *
from .board_create_client_packet import *
from .barber_open_client_packet import *
from .barber_buy_client_packet import *
from .bank_take_client_packet import *
from .bank_open_client_packet import *
from .bank_add_client_packet import *
from .attack_use_client_packet import *
from .admin_interact_tell_client_packet import *
from .admin_interact_report_client_packet import *
from .account_request_client_packet import *
from .account_create_client_packet import *
from .account_agree_client_packet import *
