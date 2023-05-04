import logging
import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_bolt.workflows.step import WorkflowStep
import sys
import threading

from slack_mr_bot.gitlab_handler import GitLabHandler
from slack_mr_bot.mr_list_message_block import MergeRequestListMessage
from slack_mr_bot.slack_channel_reader import SlackChannelReader

log_level = logging.DEBUG if os.environ.get("DEBUG_LOG") else logging.INFO
logging.basicConfig(format="%(message)s", level=log_level, stream=sys.stdout)

app = App(token=os.environ["SLACK_BOT_TOKEN"])
slack_channel_reader = SlackChannelReader(
    app.client, int(os.environ.get("HISTORY_READ_DAYS", 3))
)
bot_id = app.client.api_call("auth.test")["user_id"]
gitlab_client = GitLabHandler(os.environ["GITLAB_URL"], os.environ["GITLAB_PRIV_TOKEN"])


def post_merge_requests(channel_id):
    blocks = None
    url_list = slack_channel_reader.find_mr_urls(channel_id)

    message_list = MergeRequestListMessage()
    for url in url_list:
        mr = gitlab_client.fetch_merge_request(url)
        if mr is not None:
            message_list.add_mr(mr)

    if len(message_list) > 0:
        blocks = message_list.get_blocks()
        text = "We have {0} active Merge Requests".format(len(url_list))
    else:
        text = "We have no active Merge Requests"

    app.client.chat_postMessage(
        channel=channel_id,
        blocks=blocks,
        text=text,
        unfurl_links=False,
        unfurl_media=False,
    )


@app.event("message")
def handle_message_events(_body, _logger):
    # Prevents a lot of errors in the logs about unhandled events
    pass


@app.action("choose_channel")
def handle_some_action(ack, body, logger):
    # This endpoint will be hit when a workflow is created because of the channel select widget (unavoidable).
    # If this doesn't exist then a warning is raised.
    ack()


@app.command("/mrlist")
def mr_list(ack, respond, command):
    ack()
    user_id = command.get("user_id")
    channel_id = command.get("channel_id")

    if user_id is not None and bot_id != user_id:
        threading.Thread(target=post_merge_requests, args=(channel_id,)).start()

    return respond()


def edit(ack, step, configure):
    """
    Renders the channel drop down when creating a workflow
    """
    ack()

    blocks = [
        {
            "type": "actions",
            "elements": [
                {
                    "type": "channels_select",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select a channel",
                        "emoji": True,
                    },
                    "action_id": "choose_channel",
                }
            ],
        }
    ]
    configure(blocks=blocks)


def save(ack, view, update):
    """
    Triggered when a workflow is created/saved.
    """
    ack()

    input_values = view["state"]["values"]
    # Input values seems to be a dict with random keys, so choose the first (and only) element
    channel_id = list(input_values.values())[0]["choose_channel"]["selected_channel"]

    # Set the channel ID as an input so it will get passed into execute() (so that we know where to post)
    inputs = {"channel_id": {"value": channel_id}}

    update(inputs=inputs)


def execute(step, complete, fail):
    """
    Triggered when a workflow is executed
    """
    channel_id = step["inputs"]["channel_id"]["value"]
    post_merge_requests(channel_id)
    complete()


# Create a new WorkflowStep instance
ws = WorkflowStep(
    callback_id="list_active_mr",
    edit=edit,
    save=save,
    execute=execute,
)
# Pass Step to set up listeners
app.step(ws)


def run():
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()


if __name__ == "__main__":
    run()
