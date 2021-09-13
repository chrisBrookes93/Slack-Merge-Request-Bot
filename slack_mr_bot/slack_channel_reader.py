from datetime import datetime, timedelta
import re

WEEKEND_DAYS = [5, 6]  # Assumes you're using date.weekday() rather than isoweekday() when checking for weekdays


class SlackChannelReader:

    URL_REGEX = '\\/[^\\/]+\\/[^\\/]+\\/\\-\\/merge_requests\\/[\\d]+'

    def __init__(self, slack_client, days_to_read):
        self.slack_client = slack_client
        self.days_to_read = days_to_read

    def find_mr_urls(self, channel_id):
        url_list = []
        start_from = self._calculate_read_to_datetime()
        result = self.slack_client.conversations_history(limit=1000, channel=channel_id, oldest=start_from.timestamp())

        conversation_history = result["messages"]

        for message_dict in conversation_history:
            # Ignore messages from bots
            if 'bot_id' in message_dict or message_dict['type'] != 'message':
                continue

            text = message_dict['text']
            matches = re.findall(self.URL_REGEX, text)
            url_list.extend(matches)

        return set(url_list)

    @staticmethod
    def _calculate_read_to_datetime():
        """
        Calculate how far to read back (not including weekend days).
        """
        now = datetime.now()
        days_back = 3
        target_date = now

        while days_back:
            target_date = target_date - timedelta(days=1)
            if target_date.weekday() not in WEEKEND_DAYS:
                days_back -= 1

        return target_date
