# Slack MR Bot
Slack IRC bot to scan the last x days of a channel looking for MR links, then repost them in a concise, but 
detailed list to the channel.

## Installation

- Create new app via the manifest yaml file
- Set the logo (image included in this repo)
- On the `Basic information` tab, go to `App-Level Tokens`. 
Create a new token with the permission of `connections:write` value. 
You will need this for the configuration.
- On the `OAuth & Permissions menu`, copy the `Bot User OAuth Token` value. 
You will need this for the configuration.


## Configuration

| Env Var Name | Description | Example Value |
| --- | --- | --- |
| SLACK_BOT_TOKEN | Bot token | xoxb-xxxxxxxxx-yyyyyyyyyy-zzzzzzzzzzzzzz |
| SLACK_APP_TOKEN | App level token | xapp-1-xxxxxxxxxxxx-yyyyyyyyy-zzzzzzzzz |
| DEBUG_LOG | Print debug logs if enabled | 1  |
| HISTORY_READ_DAYS | Number of days to read back into the chat (excluding weekends) | 3  |
| GITLAB_URL | Base URL of the GitLab instance| https://gitlab.com |
| GITLAB_PRIV_TOKEN | GitLab private token | abcdef12345 |

## Running
```python
$ python -m slack_mr_bot
```

#### Docker

```bash
$ make build
$ make up
```

## Screenshot
![Screenshot of the bot output](screenshot.PNG "Screenshot of the bot output")