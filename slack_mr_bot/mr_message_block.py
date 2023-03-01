class MergeRequestMessage:
    MSG_TEMPLATE = (
        "<{url}|*{title}*>\n"
        "*Author:* `{author}`  \n"
        "*Unresolved Threads: * {unresolved_threads}\t\t\t\t "
        "*Approvals:* {approvals}"
        "{pipeline_status}"
        "{summary}"
    )

    PIPELINE_LOOKUP = {"failed": ":red_circle:", "success": ":large_green_circle:"}
    PIPELINE_DEFAULT = ":large_blue_circle:"

    def __init__(self, mr_dict):
        self.mr_dict = mr_dict

    def _get_pipeline_message(self):
        pipeline_status = self.mr_dict["pipeline_status"]
        if pipeline_status:
            icon = self.PIPELINE_LOOKUP.get(pipeline_status, self.PIPELINE_DEFAULT)
            return f"*Pipeline:*  {icon}\n"
        else:
            return "\n"

    def get_block(self):
        format_dict = {
            "url": self.mr_dict["url"],
            "title": self.mr_dict["title"],
            "author": self.mr_dict["author"],
            "unresolved_threads": self.mr_dict["open_thread_count"],
            "pipeline_status": self._get_pipeline_message(),
        }
        summary = self.mr_dict["summary"].replace("\n", " ").replace("\r", "")
        summary = (summary[:177] + "...") if len(summary) > 177 else summary
        format_dict["summary"] = summary

        approvals = self.mr_dict["approval_count"]

        format_dict["approvals"] = ":white_check_mark: " * approvals
        # For alignment
        format_dict["approvals"] += "      " * (4 - approvals)

        text = self.MSG_TEMPLATE.format(**format_dict)

        return {"type": "section", "text": {"type": "mrkdwn", "text": text}}
