HAND_ID_LIMITS = (200000000000, 999999999999)

# Offsets for PokerStars 7 (Build: 46014)
OFFSETS = { 'client' : { 'num_tables' : 0x133CAB0 },

            'table' : { 'base' : ((0x01344248, 0x20, 0x04, 0x00, 0xDF8),
                                  (0x01344248, 0x14, 0x00, 0xDF8)),
                        'interval' : ((0x00, 0x00, 0x10, 0x00, 0x00),
                                      (0x00, 0x00, 0x04, 0x00)),
                        'button_position' : 0x00,
                        'turn_counter' : 0x04,
                        'is_post_flop' : 0x08,
                        'pot' : 0x18,
                        'hand_id' : 0x40,
                        'num_cards' : 0x58,
                        'card_values' : 0x64,
                        'card_suits' : 0x68,
                        'self_position' : 0x10B0,
                        'time_remaining' : 0x11C4 },

            'seat' : { 'base' : 0x0218,
                       'interval' : 0x0160,
                       'name' : 0x00,
                       'stack' : 0x58,
                       'bet' : 0x68,
                       'is_empty' : 0x80,
                       'is_in_play' : 0x88,
                       'does_exist' : 0x8C,
                       'card_values' : 0x9C,
                       'card_suits' : 0xA0 } }
