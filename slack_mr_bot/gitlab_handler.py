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

    @staticmethod
    def _get_all_discussions(mr):
        ret_val = []
        page = 1
        ds = mr.discussions.list(per_page=50)
        ret_val.extend(ds)

        while ds:
            page += 1
            ds = mr.discussions.list(per_page=50, page=page)
            ret_val.extend(ds)

        return ret_val

    @staticmethod
    def _get_unresolved_thread_count(mr):
        unresolved_threads = 0
        ds = GitLabHandler._get_all_discussions(mr)
        for d in ds:
            if d.attributes.get('notes'):
                # We have to check the first note to see if it's a thread
                note_0 = d.attributes['notes'][0]

                if note_0.get('type') and note_0['type'].lower() in ("discussionnote", "diffnote") and note_0['resolved'] is False:
                    unresolved_threads += 1

        return unresolved_threads

    def fetch_merge_request(self, url):
        try:
            match = re.search(self.URL_REGEX, url)
            if match and len(match.groups()) == 3:
                namespace, project, mr_id = match.groups()

                proj = self.client.projects.get(f"{namespace}/{project}")
                mr = proj.mergerequests.get(id=mr_id)

                if mr.state == "opened":
                    pipeline_status = None
                    pipelines = mr.pipelines.list()
                    if pipelines:
                        pipeline_status = pipelines[0].status

                    return {
                        "title": mr.title,
                        "author": mr.author["name"],
                        "approval_count": len(mr.approvals.get().approved_by),
                        "open_thread_count": GitLabHandler._get_unresolved_thread_count(mr),
                        "summary": mr.description,
                        "url": mr.web_url,
                        "pipeline_status": pipeline_status,
                    }
            else:
                logger.error("Failed to parse URL: {}".format(url))
        except gitlab.GitlabGetError as gge:
            logger.error(gge.error_message)
