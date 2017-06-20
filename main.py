import os
import slackclient
import time
from db import db
from credentials import SLACK_API_KEY, SLACK_BOT_ID


SOCKET_DELAY = 1

STATS_COMMANDS = ['much']
SUM_COMMANDS = ['sum']
client = slackclient.SlackClient(SLACK_API_KEY)

bot_name_in_public = f'<@{SLACK_BOT_ID}>'


def is_for_me(event):
    msg_type = event.get('type')
    if msg_type and msg_type == 'message' and not event.get('user') == SLACK_BOT_ID:
        if is_private(event):
            return True
        text = event.get('text')

        if bot_name_in_public in text.strip().split():
            return True


def handle_message(message, channel):
    if is_command_stats(message):
        file_name = db.get_stats()
        post_message(message='One moment...', channel=channel)
        with open(file_name, 'r') as f:
            client.api_call('files.upload', file=f, channels=channel, filename=file_name)
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
                    # print(event)
                    if is_for_me(event):
                        handle_message(message=event.get('text'),
                                       channel=event.get('channel')
                                       )
            time.sleep(SOCKET_DELAY)
    else:
        print('connection failed')

if __name__ == '__main__':
    run()
