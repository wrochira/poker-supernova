from memory_reader import MemoryReader
from memory_reader.utils import value_from_bytes

from ._defs import *


MEMORY_READER = None


class Client():
    def __init__(self):
        self.is_initialised = False
        try:
            global MEMORY_READER
            MEMORY_READER = MemoryReader('PokerStars')
        except:
            return
        self.refresh_tables()
        self.is_initialised = True

    def refresh_tables(self):
        self.num_tables = MEMORY_READER.read_process_memory(MEMORY_READER.module_bases[0] + OFFSETS['client']['num_tables'])
        self.tables = [ ]
        for game_type in (0, 1):
            for table_index in range(self.num_tables):
                table = Table(self, table_index, game_type)
                table_state = table.get_state()
                if table_state.status_code == -1:
                    break
                self.tables.append(table)
                if len(self.tables) == self.num_tables:
                    return

    def get_table_states(self):
        return [ table.get_state() for table in self.tables ]


class Table():
    def __init__(self, client, table_index, game_type):
        self.client = client
        self.index = table_index
        self.game_type = game_type

        base_offsets = [ base+interval*self.index for base, interval in zip(OFFSETS['table']['base'][game_type], 
                                                                            OFFSETS['table']['interval'][game_type]) ]
        self.info_base = MEMORY_READER.resolve_pointer(MEMORY_READER.module_bases[0], base_offsets)
        self.seats = [ ]
        for seat_id in range(10):
            seat = Seat(self, seat_id)
            seat_state = seat.get_state()
            if not seat_state.does_exist:
                break
            self.seats.append(seat)

    def get_state(self):
        memory_chunk = MEMORY_READER.read_process_memory(self.info_base, data_type='bytes', num_bytes=256)
        button_position = value_from_bytes(memory_chunk, OFFSETS['table']['button_position'])
        turn_counter = value_from_bytes(memory_chunk, OFFSETS['table']['turn_counter'])
        pot = int(value_from_bytes(memory_chunk, OFFSETS['table']['pot']))
        hand_id = value_from_bytes(memory_chunk, OFFSETS['table']['hand_id'], num_bytes=8)
        num_cards = value_from_bytes(memory_chunk, OFFSETS['table']['num_cards'])
        #self_position = value_from_bytes(memory_chunk, OFFSETS['table']['self_position'])
        #time_remaining = value_from_bytes(memory_chunk, OFFSETS['table']['time_remaining'])
        status_code = self.get_status_code(button_position, turn_counter, hand_id)
        cards = [ ]
        seat_states = [ ]
        num_seats = len(seat_states)
        if status_code == -1:
            return TableState(status_code, button_position, turn_counter, pot, hand_id, cards, seat_states, num_seats)
        for card_id in range(min(num_cards, 5)):
            value = value_from_bytes(memory_chunk, OFFSETS['table']['card_values'] + 0x08 * card_id)
            suit = value_from_bytes(memory_chunk, OFFSETS['table']['card_suits'] + 0x08 * card_id,
                                    data_type='string', num_bytes=1)
            if value > 0:
                card = (value, suit)
                cards.append(card)
        for seat in self.seats:
            seat_state = seat.get_state()
            if seat_state.does_exist:
                seat_states.append(seat_state)
        num_seats = len(seat_states)
        if self.game_type == 1:
            pot /= 100
        return TableState(status_code, button_position, turn_counter, pot, hand_id, cards, seat_states, num_seats)

    def get_status_code(self, button_position, turn_counter, hand_id):
        # Null
        status_code = -1
        # Inactive
        if button_position == 0xFFFFFFFF:
            status_code = 0
        # Table closed (tournament) or hand transition (Zoom game)
        elif turn_counter == 0xFFFFFFFF and hand_id == 0:
            status_code = 0
        # Active
        elif button_position < len(self.seats):
            if hand_id == 0 or HAND_ID_LIMITS[0] < hand_id <= HAND_ID_LIMITS[1]:
                status_code = 1
        return status_code


class Seat():
    def __init__(self, table, seat_id):
        self.table = table
        self.index = seat_id
        self.info_base = self.table.info_base + OFFSETS['seat']['base'][0] + OFFSETS['seat']['base'][1] * self.index

    def get_state(self):
        position = self.index
        memory_chunk = MEMORY_READER.read_process_memory(self.info_base, data_type='bytes', num_bytes=256)
        name = value_from_bytes(memory_chunk, OFFSETS['seat']['name'], data_type='string', num_bytes=20)
        stack = int(value_from_bytes(memory_chunk, OFFSETS['seat']['stack']))
        bet = int(value_from_bytes(memory_chunk, OFFSETS['seat']['bet']))
        is_empty = bool(value_from_bytes(memory_chunk, OFFSETS['seat']['is_empty'], num_bytes=1))
        is_in_play = bool(value_from_bytes(memory_chunk, OFFSETS['seat']['is_in_play'], num_bytes=1))
        does_exist = value_from_bytes(memory_chunk, OFFSETS['seat']['does_exist']) == 0xFFFFFFFF
        cards = [ ]
        for card_id in range(2):
            value = value_from_bytes(memory_chunk, OFFSETS['seat']['card_values'] + 0x08 * card_id)
            suit = value_from_bytes(memory_chunk, OFFSETS['seat']['card_suits'] + 0x08 * card_id,
                                    data_type='string', num_bytes=1)
            if value > 0:
                card = (value, suit)
                cards.append(card)
        if self.table.game_type == 1:
            stack /= 100
            bet /= 100
        return SeatState(position, name, stack, bet, is_empty, is_in_play, does_exist, cards)


class TableState():
    def __init__(self, status_code, button_position, turn_counter, pot, hand_id, cards, seat_states, num_seats):
        self.status_code = status_code
        self.button_position = button_position
        self.turn_counter = turn_counter
        self.pot = pot
        self.hand_id = hand_id
        self.cards = cards
        self.seat_states = seat_states
        self.num_seats = num_seats


class SeatState():
    def __init__(self, position, name, stack, bet, is_empty, is_in_play, does_exist, cards):
        self.position = position
        self.name = name
        self.stack = stack
        self.bet = bet
        self.is_empty = is_empty
        self.is_in_play = is_in_play
        self.does_exist = does_exist
        self.cards = cards


def get_table_changes(ts1, ts2, check_seats=False):
    changes = { }
    for key in ts1.__dict__.keys():
        if key == 'seat_states':
            continue
        value_1, value_2 = ts1.__dict__[key], ts2.__dict__[key]
        if value_1 != value_2:
            changes[key] = (value_1, value_2)
    if check_seats:
        all_seat_changes = { }
        for ss_id, ss_pair in enumerate(zip(ts1.seat_states, ts2.seat_states)):
            seat_changes = get_seat_changes(*ss_pair)
            if len(seat_changes.keys()) > 0:
                all_seat_changes[ss_id] = seat_changes
        if len(all_seat_changes.keys()) > 0:
            changes['seat_states'] = all_seat_changes
    return changes

def get_seat_changes(ss1, ss2):
    changes = { }
    for key in ss1.__dict__.keys():
        value_1, value_2 = ss1.__dict__[key], ss2.__dict__[key]
        if value_1 != value_2:
            changes[key] = (value_1, value_2)
    return changes
