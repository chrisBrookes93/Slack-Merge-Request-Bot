# work out dates without weekend
import logging
import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import sys
import threading

from slack_mr_bot.gitlab_handler import GitLabHandler
from slack_mr_bot.mr_list_message_block import MergeRequestListMessage
from slack_mr_bot.slack_channel_reader import SlackChannelReader


HISTORY_READ_DAYS = 3
GITLAB_URL = 'https://gitlab.com'
DEBUG = True

logging.basicConfig(format='%(message)s', level=logging.DEBUG if DEBUG else logging.INFO, stream=sys.stdout)

app = App(token=os.environ['SLACK_BOT_TOKEN'])
slack_channel_reader = SlackChannelReader(app.client, HISTORY_READ_DAYS, GITLAB_URL)
bot_id = app.client.api_call('auth.test')['user_id']
gitlab_client = GitLabHandler(GITLAB_URL, os.environ['GITLAB_PRIV_TOKEN'])


def post_merge_requests(channel_id):
    blocks = None
    url_list = slack_channel_reader.find_mr_urls(channel_id)

    if url_list:
        message_list = MergeRequestListMessage()
        for url in url_list:
            mr = gitlab_client.fetch_merge_request(url)
            message_list.add_mr(mr)

        blocks = message_list.get_blocks()
    text = 'We have {0} active Merge Requests'.format(len(url_list))
    app.client.chat_postMessage(channel=channel_id,
                                blocks=blocks,
                                text=text,
                                unfurl_links=False,
                                unfurl_media=False)


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
    SocketModeHandler(app, os.environ['SLACK_APP_TOKEN']).start()


if __name__ == '__main__':
    run()
