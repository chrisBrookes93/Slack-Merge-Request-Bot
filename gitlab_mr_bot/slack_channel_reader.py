import datetime
import re

class SlackChannelReader:

    BASE_URL_REGEX = '{domain_name}\/[^\/]+\/[^\/]+.*\/merge_requests\/[\d]+'

    def __init__(self, slack_client, days_to_read, gitlab_domain_name):
        self.slack_client = slack_client
        self.days_to_read = days_to_read
        self.url_regex = self.BASE_URL_REGEX.format(domain_name=re.escape(gitlab_domain_name))

    def find_mr_urls(self, channel_id):
        url_list = []
        start_from = self._calculate_read_to_datetime()
        result = self.slack_client.conversations_history(channel=channel_id, oldest=start_from.timestamp())

        conversation_history = result["messages"]

        for message_dict in conversation_history:
            # Ignore messages from bots
            if 'bot_id' in message_dict or message_dict['type'] != 'message':
                continue

            text = message_dict['text']
            matches = re.findall(self.url_regex, text)
            url_list.extend(matches)

        # url_list = ['https://gitlab.com/chrisBrookes93/currency_flask/-/merge_requests/2',
        #             'https://gitlab.com/chrisBrookes93/currency_flask/-/merge_requests/3',
        #             'https://gitlab.com/chrisBrookes93/currency_flask/-/merge_requests/4',
        #             'https://gitlab.com/chrisBrookes93/currency_flask/-/merge_requests/5',
        #             'https://gitlab.com/chrisBrookes93/currency_flask/-/merge_requests/6']

        return set(url_list)

    def _calculate_read_to_datetime(self):
        """
        Calculate how far to read back (not including weekend days).
        :return:
        """
        tod = datetime.datetime.now()
        # td = datetime.timedelta(days=self.days_to_read)
        # TODO - this is for debugging purposes, remove
        td = datetime.timedelta(minutes=30)
        to_read = tod - td
        return to_read

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