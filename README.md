# Slack MR Bot
Slack App (bot) that scans the last x days of a channel looking for links to active Merge Requests, then reposts them in a concise, but 
detailed list to the same channel. This is to remind developers of Merge Requests that require attention.

## Installation

- In the Slack Workspace admin settings, create new app by uploading `slack_app_manifest.yml`
- Set the logo (image included in this repo)
- On the `Basic information` tab, go to `App-Level Tokens`. 
Create a new token with the permission of `connections:write` value. 
You will need this for the configuration.
- On the `OAuth & Permissions menu`, copy the `Bot User OAuth Token` value. 
You will need this for the configuration.


## Configuration
Configuration is acheived via environment variables that should exist in the container.

| Env Var Name | Description | Example Value |
| --- | --- | --- |
| SLACK_BOT_TOKEN | Bot token | xoxb-xxxxxxxxx-yyyyyyyyyy-zzzzzzzzzzzzzz |
| SLACK_APP_TOKEN | App level token | xapp-1-xxxxxxxxxxxx-yyyyyyyyy-zzzzzzzzz |
| DEBUG_LOG | Print debug logs if enabled | 1  |
| HISTORY_READ_DAYS | Number of days to read back into the chat (excluding weekends) | 3  |
| GITLAB_URL | Base URL of the GitLab instance| https://gitlab.com |
| GITLAB_PRIV_TOKEN | GitLab private token | abcdef12345 |

## Installing Package
```bash
$ pip install -r requirements.txt
$ pip install .
```

## Running
From the command line:
```bash
$ python -m slack_mr_bot
```
Or:
```bash
$ slack_mr_bot
```
From Python:
```python
from slack_mr_bot import bot
bot.run()
```

#### Docker

```bash
$ make build
$ make up
```

## Executing on a schedule
You can get this bot to run on a schedule by setting up a [Slack Workflow](https://slack.com/intl/en-gb/help/articles/360035692513-Guide-to-Workflow-Builder). 

Under the Slack Workspace settings, find `Workflow Builder`. 

Click `Create` and then follow the steps:
- Give the workflow a descriptive name and then click `Next`.
- Select `Scheduled date & time`. Choose an appropriate daily time to trigger the workflow. Click `Next`.
- Click `Add Step` and then select the `List Active Merge Requests` action from the list.
- Select the Slack channel you wish this workflow to apply to and then click `Save`
- Click `Publish` to finalise and activate the workflow.


## Example View
![Screenshot of the bot output](screenshot.PNG "Screenshot of the bot output")
