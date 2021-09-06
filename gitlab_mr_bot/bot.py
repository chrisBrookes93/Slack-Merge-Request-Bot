from flask import Flask, request, Response
import logging
import slack
from slackeventsapi import SlackEventAdapter
import sys
import threading

from gitlab_mr_bot.gitlab_handler import GitLabHandler
from gitlab_mr_bot.mr_list_message_block import MergeRequestListMessage

SLACK_TOKEN = ''
SLACK_SIGNING_SECRET = ''
HISTORY_READ_DAYS = 3
MR_URL_REGEX = ''
SCHEDULE = ''
PRIV_TOKEN = ''
GITLAB_URL = 'https://gitlab.com'

slack_client = None
slack_event_adapter = None
gitlab_client = None
flask_app = Flask(__name__)
bot_id = None


def run():
    global slack_client
    global slack_event_adapter
    global gitlab_client
    global flask_app
    global bot_id

    logging.basicConfig(format='%(message)s', level=logging.DEBUG, stream=sys.stdout)

    slack_client = slack.WebClient(token=SLACK_TOKEN)
    bot_id = slack_client.api_call('auth.test')['user_id']

    slack_event_adapter = SlackEventAdapter(SLACK_SIGNING_SECRET, '/slack/events', flask_app)

    gitlab_client = GitLabHandler(GITLAB_URL, PRIV_TOKEN)

    flask_app.run(debug=True)


# Stolen and adapted from: https://stackoverflow.com/questions/12691551/
# import datetime
# def date_by_sub_business_days(from_date, sub_days):
#     business_days_to_sub = sub_days
#     current_date = from_date
#     while business_days_to_sub > 0:
#         current_date -= datetime.timedelta(days=1)
#         weekday = current_date.weekday()
#         if weekday >= 5: # sunday = 6
#             continue
#         business_days_to_sub -= 1
#     return current_date

def post_merge_requests(channel_id):
    result = slack_client.conversations_history(channel=channel_id)

    conversation_history = result["messages"]

    url_list = ['https://gitlab.com/chrisBrookes93/currency_flask/-/merge_requests/2',
                'https://gitlab.com/chrisBrookes93/currency_flask/-/merge_requests/3',
                'https://gitlab.com/chrisBrookes93/currency_flask/-/merge_requests/4',
                'https://gitlab.com/chrisBrookes93/currency_flask/-/merge_requests/5',
                'https://gitlab.com/chrisBrookes93/currency_flask/-/merge_requests/6']

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
