# Slack MR Bot
Slack App (bot) that scans the last x days of a channel looking for links to active Merge Requests, then reposts them in a concise, but 
detailed list to the same channel. This is to remind developers of Merge Requests that require attention.

## Installation

- Go to https://api.slack.com/apps and click `Create New App`.
- Click `from manifest`, select the workspace, and paste in the contents of `slack_app_manifest.yaml`
- Set the logo under `Display Information` (image included in this repo)
- On the `Basic information` tab, go to `App-Level Tokens`. 
Create a new token with the permission of `connections:write` value. 
Copy this value, you will need this for the configuration.
- On the `OAuth & Permissions` menu, click `Install to Organization` and then `Allow`. Copy the `Bot User OAuth Token` value, you will need this for the configuration.
- On the same page click `Install to <workspace name>`, and then `Allow`.
- You *might* then need an Administrator to approve the app under https://app.slack.com/apps-manage/<workspace_ID>.


## Configuration
Configuration is achieved via environment variables that should exist in the container.

| Env Var Name | Description | Example Value                            |
| --- | --- |------------------------------------------|
| SLACK_BOT_TOKEN | Bot token | xoxb-xxxxxxxxx-yyyyyyyyyy-zzzzzzzzzzzzzz |
| SLACK_APP_TOKEN | App level token | xapp-X-xxxxxxxxxxxx-yyyyyyyyy-zzzzzzzzz  |
| DEBUG_LOG | Print debug logs if enabled | 1                                        |
| HISTORY_READ_DAYS | Number of days to read back into the chat (excluding weekends) | 3                                        |
| GITLAB_URL | Base URL of the GitLab instance| https://gitlab.com                       |
| GITLAB_PRIV_TOKEN | GitLab private token | abcdef12345                              |

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
You can get this bot to run on a schedule by setting up a Slack Workflow.
See the guide written [here](https://slack.com/intl/en-gb/help/articles/17542172840595-Build-a-workflow--Create-a-workflow-in-Slack). 
The Step will appear under the last option in the list called `Custom` under `GitLab MR Bot`.

## Example View
![Screenshot of the bot output](screenshot.PNG "Screenshot of the bot output")
