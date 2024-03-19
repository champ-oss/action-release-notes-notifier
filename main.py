"""Parses the most recent commit for changes to variables."""
import difflib
import logging
import re
from typing import Optional, Dict, List

from git import Repo

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def main() -> None:
    """
    Handle the main execution of the script.

    :return: None
    """
    repo = Repo()
    get_changes_from_last_commit(repo)


def get_changes_from_last_commit(repo: Repo) -> List[Dict[str, str]]:
    """
    Get a diff of changes from the most recent commit.

    :param repo: git repository
    :return: list of changes
    """
    for item in repo.head.commit.diff('HEAD~1', create_patch=True):
        logger.info(f'changed file: {item.b_path}')

        changes = get_repo_commit_changes(item.b_blob.data_stream.read().decode('utf-8'),
                                          item.a_blob.data_stream.read().decode('utf-8'))
        return changes


def get_repo_commit_changes(before: str, after: str) -> List[Dict[str, str]]:
    """
    Compare the before and after strings and return a list of changes.

    :param before: string before changes
    :param after: string after changes
    :return: list of changes
    """
    changes: List[Dict[str, str]] = []

    for line in difflib.unified_diff(before.splitlines(), after.splitlines()):
        if not line.startswith('+'):
            continue

        repo = parse_repo_name(line)
        commit = parse_commit(line)
        if repo and commit:
            logger.info(f'changed: repo:{repo} commit:{commit}')
            changes.append({repo: commit})

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
    main()
