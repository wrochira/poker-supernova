import time
import datetime

from poker_supernova import Client, get_table_changes


def watch_the_pots(client):
    previous_states = [ ]
    while True:
        client.refresh_tables()
        current_states = client.get_table_states()
        timestamp = datetime.datetime.now().strftime('%H:%M:%S')
        for table_id, states_pair in enumerate(zip(previous_states, current_states)):
            changes = get_table_changes(*states_pair)
            if 'pot' in changes.keys():
                before, after = changes['pot']
                print(timestamp, 'Table', table_id, 'pot value changed from', before, 'to', after)
        previous_states = current_states
        time.sleep(0.1)


if __name__ == '__main__':
    client = Client()
    if client.is_initialised:
        print('Successfully hooked PokerStars process.')
        watch_the_pots(client)
    else:
        print('Unable to hook PokerStars process.')
