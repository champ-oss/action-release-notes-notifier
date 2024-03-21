"""Parses the most recent commit for changes to variables."""
import difflib
import logging
import os
import re
from typing import Optional, Dict

from git import Repo
from github import Github, Auth, UnknownObjectException
from github.Organization import Organization

from slack_notifier.slack_notifier import SlackNotifier

logging.basicConfig(
    format='%(asctime)s [%(levelname)8s] %(message)s (%(filename)s:%(lineno)s)',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def main(repo: Repo, slack_notifier: SlackNotifier, github_session: Github,
         github_organization: str, environment_name: str, file_pattern: str) -> None:
    """
    Handle the main execution of the script.

    :return: None
    """
    changes = get_changes_from_last_commit(repo, file_pattern)
    if not changes:
        return

    org = github_session.get_organization(github_organization)

    summary = f'The {environment_name} environment has been updated\n'
    for repo_name, commit in changes.items():
        summary += get_pull_request_summary_from_commit(org, repo_name, commit)
        summary += '\n\n'

    slack_notifier.send_markdown(summary)


def get_pull_request_summary_from_commit(org: Organization, repo_name: str, commit: str) -> str:
    """
    Create a summary of pull requests associated with the commit.

    :param org: GitHub Organization
    :param repo_name: name of the repository
    :param commit: commit to find pull requests for
    :return: summary of pull requests
    """
    summary = f'\n{repo_name}'
    logger.info(f'loading repository:{repo_name}')
    try:
        repo = org.get_repo(repo_name)
    except UnknownObjectException as e:
        logger.warning(e)
        summary += '\n \t • unable to find repository'
        return summary

    logger.info(f'getting pull requests for commit:{commit} in repo:{repo_name}')
    for pull_request in repo.get_commit(commit).get_pulls():
        logger.info(f'found pull request:#{pull_request.number} {pull_request.title}')
        summary += f'\n \t • *<{pull_request.html_url}|{pull_request.title}>* #{pull_request.number}'

    return summary


def get_changes_from_last_commit(repo: Repo, file_pattern: str) -> Dict[str, str]:
    """
    Get a diff of changes from the most recent commit.

    :param repo: git repository
    :return: list of changes
    """
    changes: Dict[str, str] = {}

    for item in repo.head.commit.diff('HEAD~1', create_patch=True):
        logger.info(f'changed file: {item.b_path}')
        if not matches_file_pattern(item.b_path, file_pattern):
            logger.info(f'skipping file: {item.b_path}')
            continue

        changes.update(get_repo_commit_changes(item.b_blob.data_stream.read().decode('utf-8'),
                                               item.a_blob.data_stream.read().decode('utf-8')))

    return changes


def matches_file_pattern(file_path: str, pattern: str) -> bool:
    """
    Check if a file path matches the regex pattern.

    :param file_path: path of the file
    :param pattern: regex pattern to test
    :return: bool
    """
    match = re.match(pattern, file_path)
    return match is not None


def get_repo_commit_changes(before: str, after: str) -> Dict[str, str]:
    """
    Compare the before and after strings and return a list of changes.

    :param before: string before changes
    :param after: string after changes
    :return: list of changes
    """
    changes: Dict[str, str] = {}

    for line in difflib.unified_diff(before.splitlines(), after.splitlines()):
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
    main(repo=Repo(),
         slack_notifier=SlackNotifier(webhook_url=os.getenv('SLACK_WEBHOOK')),
         github_session=Github(auth=Auth.Token(os.getenv('TOKEN'))),
         github_organization=os.getenv('ORGANIZATION'),
         environment_name=os.getenv('ENVIRONMENT'),
         file_pattern=os.getenv('FILE_PATTERN'))
