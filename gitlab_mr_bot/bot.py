# TODO - schedule message

from flask import Flask, request, Response
import logging
import slack
from slackeventsapi import SlackEventAdapter
import sys
import threading

from gitlab_mr_bot.gitlab_handler import GitLabHandler
from gitlab_mr_bot.mr_list_message_block import MergeRequestListMessage
from gitlab_mr_bot.slack_channel_reader import SlackChannelReader

logging.basicConfig(format='%(message)s', level=logging.DEBUG, stream=sys.stdout)

SLACK_TOKEN = ''
SLACK_SIGNING_SECRET = ''
HISTORY_READ_DAYS = 3
SCHEDULE = ''
PRIV_TOKEN = ''
GITLAB_URL = 'https://gitlab.com'
DEBUG = True

flask_app = Flask(__name__)
slack_client = slack.WebClient(token=SLACK_TOKEN)
slack_event_adapter = SlackEventAdapter(SLACK_SIGNING_SECRET, '/slack/events', flask_app)
slack_channel_reader = SlackChannelReader(slack_client, HISTORY_READ_DAYS, GITLAB_URL)
bot_id = slack_client.api_call('auth.test')['user_id']
gitlab_client = GitLabHandler(GITLAB_URL, PRIV_TOKEN)


def run():
    flask_app.run(debug=DEBUG)


def post_merge_requests(channel_id):
    url_list = slack_channel_reader.find_mr_urls(channel_id)

    message_list = MergeRequestListMessage()
    for url in url_list:
        mr = gitlab_client.fetch_merge_request(url)
        message_list.add_mr(mr)

    blocks = message_list.get_blocks()
    slack_client.chat_postMessage(channel=channel_id, blocks=blocks)


@flask_app.route('/mr_list', methods=['POST'])
def mr_list():
    data = request.form
    user_id = data.get('user_id')
    channel_id = data.get('channel_id')

    if user_id is not None and bot_id != user_id:
        threading.Thread(target=post_merge_requests, args=(channel_id,)).start()

    return Response(), 200


if __name__ == '__main__':
    run()
