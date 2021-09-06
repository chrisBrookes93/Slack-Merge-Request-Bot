
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
            'author': self.mr_dict['author']
        }
        summary = self.mr_dict['summary'].replace('\n', ' ').replace('\r', '')
        summary = (summary[:177] + '...') if len(summary) > 177 else summary
        format_dict['summary'] = summary

        approvals = self.mr_dict['approval_count']

        # TODO - remove this line, its for debugging!
        import random
        approvals = random.choice([0, 1, 2, 3, 4])

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
