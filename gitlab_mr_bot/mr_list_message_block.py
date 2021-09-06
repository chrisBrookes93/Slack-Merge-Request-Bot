from gitlab_mr_bot.mr_message_block import MergeRequestMessage


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
