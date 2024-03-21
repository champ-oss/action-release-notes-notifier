"""Parses the most recent commit for changes to variables."""
import logging
import os
import re
from typing import Optional, Dict, Iterator

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
         environment_name: str, file_pattern: str) -> None:
    """
    Handle the main execution of the script.

    :return: None
    """
    file_diffs = git_util.get_file_diffs_from_last_commit(file_pattern)
    if not file_diffs:
        return

    message_formatter = MessageFormatter(environment_name)

    for file_diff in file_diffs:
        for repo_name, commit in get_repo_commit_changes(file_diff.unified_diff).items():
            pull_requests = github_util.get_pull_requests_for_commit(repo_name, commit)
            message_formatter.add_repo_pull_request_summary(repo_name=repo_name, pull_requests=pull_requests)

    slack_notifier.send_markdown(message_formatter.get_summary())


def matches_file_pattern(file_path: str, pattern: str) -> bool:
    """
    Check if a file path matches the regex pattern.

    :param file_path: path of the file
    :param pattern: regex pattern to test
    :return: bool
    """
    match = re.match(pattern, file_path)
    return match is not None


def get_repo_commit_changes(unified_diff: Iterator[str]) -> Dict[str, str]:
    """
    Compare the before and after strings and return a list of changes.

    :param unified_diff: unified diff string
    :return: list of changes
    """
    changes: Dict[str, str] = {}

    for line in unified_diff:
        if not line.startswith('+'):
            continue

        repo = parse_repo_name(line)
        commit = parse_commit(line)
        if repo and commit:
            logger.info(f'changed: repo:{repo} commit:{commit}')
            changes[repo] = commit

    return changes


def parse_repo_name(line: str) -> Optional[str]:
    """
    Parse the repository name from a line of text.

    Example of line: (should return: test-repo-1)
    test_repo_1 = "123.foo.com/bar/test-repo-1:abc123"

    :param line:
    :return:
    """
    match = re.search(r'([^/":]+):\w+\"', line)
    if match:
        return match.group(1)
    return None


def parse_commit(line: str) -> Optional[str]:
    """
    Parse the commit hash from a line of text.

    Example of line: (should return: abc123)
    test_repo_1 = "123.foo.com/bar/test-repo-1:abc123"

    :param line:
    :return:
    """
    match = re.search(r'\w:(\w+)\"', line)
    if match:
        return match.group(1)
    return None


if __name__ == '__main__':
    main(git_util=GitUtil(),
         slack_notifier=SlackNotifier(webhook_url=os.getenv('SLACK_WEBHOOK')),
         github_util=GitHubUtil(access_token=os.getenv('TOKEN'), organization_name=os.getenv('ORGANIZATION')),
         environment_name=os.getenv('ENVIRONMENT'),
         file_pattern=os.getenv('FILE_PATTERN'))
