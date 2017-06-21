import os
import csv
import slackclient
import time
from datetime import datetime
from db import db
from credentials import SLACK_API_KEY, SLACK_BOT_ID

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(BASE_DIR, 'results')

if not os.path.exists(RESULTS_DIR):
    os.makedirs(RESULTS_DIR)

SOCKET_DELAY = 1

STATS_COMMANDS = ['much']
SUM_COMMANDS = ['sum']
client = slackclient.SlackClient(SLACK_API_KEY)

bot_name_in_public = f'<@{SLACK_BOT_ID}>'


def get_current_date():
    return datetime.now().strftime('%d_%m_%H_%M')


def is_for_me(event):
    msg_type = event.get('type')
    if msg_type and msg_type == 'message' and not event.get('user') == SLACK_BOT_ID:
        if is_private(event):
            return True
        text = event.get('text')

        if bot_name_in_public in text.strip().split():
            return True


def make_csv(data, file_name):
    with open(file_name, 'w', newline='') as f:
        file = csv.writer(f)
        for item in data.fetchall():
            file.writerow(item)


def load_file_to_channel(file_name, channel):
    with open(file_name, 'r') as f:
        client.api_call('files.upload', file=f, channels=channel, filename=file_name)


def handle_message(message, channel):
    if is_command_stats(message):
        post_message(message='One moment...', channel=channel)
        cursor_from_db = db.get_stats()
        current_date = get_current_date()
        file_name = f'{RESULTS_DIR}/result_{current_date}.csv'
        make_csv(cursor_from_db, file_name)
        load_file_to_channel(file_name, channel)
        post_message(message='Here', channel=channel)
    elif is_command_sum(message):
        result = db.get_sum()
        post_message(message=result, channel=channel)


def post_message(message, channel):
    client.api_call('chat.postMessage', channel=channel, text=message, as_user=True)


def is_private(event):
    return event.get('channel', '').startswith('D')


def is_command_stats(message):
    messages = [word.lower() for word in message.strip().split()]
    return any(command in messages for command in STATS_COMMANDS)


def is_command_sum(message):
    messages = [word.lower() for word in message.strip().split()]
    return any(command in messages for command in SUM_COMMANDS)


def run():
    if client.rtm_connect():
        print('connect')
        while True:
            event_list = client.rtm_read()
            if len(event_list) > 0:
                for event in event_list:
                    if is_for_me(event):
                        handle_message(message=event.get('text'),
                                       channel=event.get('channel')
                                       )
            time.sleep(SOCKET_DELAY)
    else:
        print('connection failed')

if __name__ == '__main__':
    run()

