# TODO - schedule message
# work out dates without weekend

import logging
import slack
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import sys
import threading

from gitlab_mr_bot.gitlab_handler import GitLabHandler
from gitlab_mr_bot.mr_list_message_block import MergeRequestListMessage
from gitlab_mr_bot.slack_channel_reader import SlackChannelReader


SLACK_TOKEN = 'xoxb-...'
SLACK_APP_TOKEN = 'xapp-...'
HISTORY_READ_DAYS = 3
SCHEDULE = ''
GITLAB_PRIV_TOKEN = ''
GITLAB_URL = 'https://gitlab.com'
DEBUG = True

logging.basicConfig(format='%(message)s', level=logging.DEBUG if DEBUG else logging.INFO, stream=sys.stdout)




app = App(token=SLACK_BOT_TOKEN, process_before_response=True)
slack_client = slack.WebClient(token=SLACK_BOT_TOKEN)
slack_channel_reader = SlackChannelReader(slack_client, HISTORY_READ_DAYS, GITLAB_URL)
bot_id = slack_client.api_call('auth.test')['user_id']
gitlab_client = GitLabHandler(GITLAB_URL, GITLAB_PRIV_TOKEN)


def post_merge_requests(channel_id):
    url_list = slack_channel_reader.find_mr_urls(channel_id)

    message_list = MergeRequestListMessage()
    for url in url_list:
        mr = gitlab_client.fetch_merge_request(url)
        message_list.add_mr(mr)

    blocks = message_list.get_blocks()
    slack_client.chat_postMessage(channel=channel_id, blocks=blocks, text='We have the following active Merge Requests:')


@app.event("message")
def handle_message_events(_body, _logger):
    # Prevents a lot of errors in the logs
    pass


@app.command("/mrlist")
def mr_list(ack, respond, command):
    ack()
    user_id = command.get('user_id')
    channel_id = command.get('channel_id')

    if user_id is not None and bot_id != user_id:
        threading.Thread(target=post_merge_requests, args=(channel_id,)).start()

    return respond()


def run():
    SocketModeHandler(app, SLACK_APP_TOKEN).start()


if __name__ == '__main__':
    run()
