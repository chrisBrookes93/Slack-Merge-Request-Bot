import gitlab
import logging
import re

logger = logging.getLogger(__name__)


class GitLabHandler:
    URL_REGEX = "\\/([^\\/]+)\\/([^\\/]+)[^\\d]+([\\d]+)"

    def __init__(self, url, private_token):
        self.url = url
        self.private_token = private_token
        self.client = gitlab.Gitlab(url, private_token=private_token)
        self.client.auth()

    def fetch_merge_request(self, url):
        try:
            match = re.search(self.URL_REGEX, url)
            if match and len(match.groups()) == 3:
                namespace, project, mr_id = match.groups()

                proj = self.client.projects.get(f"{namespace}/{project}")
                mr = proj.mergerequests.get(id=mr_id)

                if mr.state == "opened":
                    all_threads = [x for x in mr.notes.list() if hasattr(x, "resolved")]
                    unresolved_threads = [
                        x for x in all_threads if not getattr(x, "resolved", True)
                    ]

                    pipeline_status = None
                    pipelines = mr.pipelines.list()
                    if pipelines:
                        pipeline_status = pipelines[0].status

                    return {
                        "title": mr.title,
                        "author": mr.author["name"],
                        "approval_count": len(mr.approvals.get().approved_by),
                        "open_thread_count": len(unresolved_threads),
                        "total_thread_count": len(all_threads),
                        "summary": mr.description,
                        "url": mr.web_url,
                        "pipeline_status": pipeline_status,
                    }
            else:
                logger.error("Failed to parse URL: {}".format(url))
        except gitlab.GitlabGetError as gge:
            logger.error(gge.error_message)
