# requires flask, slackclient, slackeventsapi, gitlab?
class MergeRequestMessage:
    MSG_TEMPLATE = "<{url}|*{title}*>\n" \
                   "*Author:* `{author}`  \n" \
                   "*Unresolved Threads: * {unresolved_threads}\t\t\t\t " \
                   "*Approvals:* {approvals}" \
                   "{pipeline_status}" \
                   "{summary}"

    PIPELINE_LOOKUP = {
        'failed': ':red_circle:',
        'success': ':large_green_circle:'
    }
    PIPELINE_DEFAULT = ':large_blue_circle:'

    def __init__(self, mr_dict):
        self.mr_dict = mr_dict

    def _get_pipeline_message(self):
        pipeline_status = self.mr_dict['pipeline_status']
        if pipeline_status:
            icon = self.PIPELINE_LOOKUP.get(pipeline_status, self.PIPELINE_DEFAULT)
            return f"*Pipeline:*  {icon}\n"
        else:
            return '\n'

    def get_block(self):
        format_dict = {
            'url': self.mr_dict['url'],
            'title': self.mr_dict['title'],
            'author': self.mr_dict['author'],
            'summary': self.mr_dict['summary']
        }

        approvals = self.mr_dict['approval_count']
        # TODO - remove this line, its for debugging!
        import random
        approvals = random.choice([0,1,2,3,4])

        format_dict['approvals'] = ':white_check_mark: ' * approvals
        # For alignment
        format_dict['approvals'] += '      ' * (4 - approvals)

        format_dict['pipeline_status'] = self._get_pipeline_message()

        if self.mr_dict['open_thread_count'] == 0 and self.mr_dict['total_thread_count'] == 0:
            format_dict['unresolved_threads'] = '0\t'
        else:
            format_dict['unresolved_threads'] = '{open_thread_count}/{total_thread_count}'.format(
                open_thread_count=self.mr_dict['open_thread_count'],
                total_thread_count=self.mr_dict['total_thread_count'])

        text = self.MSG_TEMPLATE.format(**format_dict)

        return {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": text
            }
        }


class MergeRequestListMessage:
    DIVIDER = {'type': 'divider'}

    def __init__(self, mr_list=None):
        self.mr_messages = []
        if mr_list:
            for mr in mr_list:
                self.add_mr(mr)

    def add_mr(self, mr):
        self.mr_messages.append(MergeRequestMessage(mr))

    def get_blocks(self):
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*We have the following active Merge Requests:*"
                }
            },
            {
                "type": "divider"
            }]

        for mr in self.mr_messages:
            blocks.append(mr.get_block())
            blocks.append(MergeRequestListMessage.DIVIDER)

        return blocks


import gitlab

from flask import Flask, request, Response
import slack
import re
from slackeventsapi import SlackEventAdapter

SLACK_TOKEN = ''
SLACK_SIGNING_SECRET = ''
HISTORY_READ_DAYS = 3
MR_URL_REGEX = ''
SCHEDULE = ''
URL_REGEX = 'gitlab\\.com\\/([^\\/]+)\\/([^\\/]+)[^\\d]+([\\d]+)'
PRIV_TOKEN = ''
GITLAB_URL = 'https://gitlab.com'


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


def fetch_mr(gl, url):
    try:
        match = re.search(URL_REGEX, url)
        if match and len(match.groups()) == 3:
            namespace, project, mr_id = match.groups()

            proj = gl.projects.get(f'{namespace}/{project}')
            mr = proj.mergerequests.get(id=mr_id)

            if mr.state == 'opened':
                all_threads = [x for x in mr.notes.list() if hasattr(x, 'resolved')]
                unresolved_threads = [x for x in all_threads if not getattr(x, 'resolved', True)]
                summary = mr.description.replace('\n', ' ').replace('\r', '')
                summary = (summary[:177] + '...') if len(summary) > 177 else summary

                pipeline_status = None
                pipelines = mr.pipelines.list()
                if pipelines:
                    pipeline_status = mr.pipelines.list()[0].status

                return {
                    'title': mr.title,
                    'author': mr.author['name'],
                    'approval_count': len(mr.approvals.get().approved_by),
                    'open_thread_count': len(unresolved_threads),
                    'total_thread_count': len(all_threads),
                    'summary': summary,
                    'url': mr.web_url,
                    'pipeline_status': pipeline_status
                }
    except gitlab.GitlabGetError as gge:
        print(gge.error_message)


client = slack.WebClient(token=SLACK_TOKEN)
BOT_ID = client.api_call('auth.test')['user_id']

app = Flask(__name__)
slack_event_adapter = SlackEventAdapter(SLACK_SIGNING_SECRET, '/slack/events', app)

gl = gitlab.Gitlab(GITLAB_URL, private_token=PRIV_TOKEN)
gl.auth()


# def send_welcome_message(channel, user):
#     welcome = WelcomeMessage(channel, user)
#     message = welcome.get_message()
#     response = client.chat_postMessage(**message)
#     welcome.timestamp = response['ts']


@app.route('/mr_list', methods=['POST'])
def mr_list():
    data = request.form
    user_id = data.get('user_id')
    channel_id = data.get('channel_id')
    result = client.conversations_history(channel=channel_id)

    conversation_history = result["messages"]

    url_list = ['https://gitlab.com/chrisBrookes93/currency_flask/-/merge_requests/2',
                'https://gitlab.com/chrisBrookes93/currency_flask/-/merge_requests/3',
                'https://gitlab.com/chrisBrookes93/currency_flask/-/merge_requests/4',
                'https://gitlab.com/chrisBrookes93/currency_flask/-/merge_requests/5',
                'https://gitlab.com/chrisBrookes93/currency_flask/-/merge_requests/6']

    if user_id is not None and BOT_ID != user_id:
        message_list = MergeRequestListMessage()
        for url in url_list:
            mr = fetch_mr(gl, url)
            message_list.add_mr(mr)

        blocks = message_list.get_blocks()
        client.chat_postMessage(channel=channel_id, blocks=blocks)

        #
    return Response(), 200


app.run(debug=True)
