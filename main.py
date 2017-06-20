import os
import slackclient
import time

API_KEY = os.environ.get('SLACK_API_KEY')
SLACK_BOT_ID = os.environ.get('SLACK_BOT_ID')

SOCKET_DELAY = 1

COMMANDS = ['much']
client = slackclient.SlackClient(API_KEY)
is_ok = client.api_call('users.list').get('ok')


def get_user(user):
    return f'<@{user}>'

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
    if is_command(message):
        post_message(message=message, channel=channel)


def post_message(message, channel):
    client.api_call('chat.postMessage', channel=channel, text=message, as_user=True)


def is_private(event):
    return event.get('channel', '').startswith('D')


def is_command(message):
    messages = [word.lower() for word in message.strip().split()]
    return any(command in messages for command in COMMANDS)


def run():
    if client.rtm_connect():
        print('connect')
        while True:
            event_list = client.rtm_read()
            if len(event_list) > 0:
                for event in event_list:
                    print(event)
                    if is_for_me(event):
                        handle_message(message=event.get('text'),
                                       channel=event.get('channel')
                                       )
            time.sleep(SOCKET_DELAY)
    else:
        print('connection failed')

if __name__ == '__main__':
    run()