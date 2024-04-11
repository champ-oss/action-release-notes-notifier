"""Parses the most recent commit for changes to variables."""
import logging
import os

from diff_parser.diff_parser import DiffParser
from git_util.git_util import GitUtil
from github_util.github_util import GitHubUtil
from message_formatter.message_formatter import MessageFormatter
from slack_notifier.slack_notifier import SlackNotifier

logging.basicConfig(
    format='%(asctime)s [%(levelname)8s] %(message)s (%(filename)s:%(lineno)s)',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def main(git_util: GitUtil, slack_notifier: SlackNotifier, github_util: GitHubUtil,
         environment_name: str, file_pattern: str, tag_name: str) -> None:
    """
    Handle the main execution of the script.

    :return: None
    """
    file_diffs = git_util.get_file_diffs_from_last_commit(file_pattern)
    if not file_diffs:
        return

    message_formatter = MessageFormatter(environment_name)

    for file_diff in file_diffs:
        for repo_name, commit in DiffParser.get_repo_commit_changes(file_diff.unified_diff).items():
            pull_requests = github_util.get_pull_requests_for_commit(repo_name, commit)
            message_formatter.add_repo_pull_request_summary(repo_name=repo_name, pull_requests=pull_requests)
            if tag_name:
                github_util.tag_commit(repo_name, commit, tag_name)

    slack_notifier.send_markdown(message_formatter.get_final_summary())


if __name__ == '__main__':
    main(git_util=GitUtil(),
         slack_notifier=SlackNotifier(webhook_url=os.getenv('SLACK_WEBHOOK')),
         github_util=GitHubUtil(access_token=os.getenv('TOKEN'), organization_name=os.getenv('ORGANIZATION')),
         environment_name=os.getenv('ENVIRONMENT'),
         file_pattern=os.getenv('FILE_PATTERN'),
         tag_name=os.getenv('TAG_NAME'))
