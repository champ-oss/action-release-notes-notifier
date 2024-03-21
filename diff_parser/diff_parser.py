"""Provides functionality for parsing git diffs."""
import logging
import re
from typing import Optional, Iterator, Dict

logger = logging.getLogger(__name__)


class DiffParser:
    """Provides functionality for parsing git diffs."""

    @staticmethod
    def get_repo_commit_changes(unified_diff: Iterator[str]) -> Dict[str, str]:
        """
        Parse the diff string to get the repo and commit changes.

        :param unified_diff: unified diff string
        :return: list of changes
        """
        changes: Dict[str, str] = {}

        for line in unified_diff:
            if not line.startswith('+'):
                continue

            repo = DiffParser._parse_repo_name(line)
            commit = DiffParser._parse_commit(line)
            if repo and commit:
                logger.info(f'found change: repo:{repo} commit:{commit}')
                changes[repo] = commit

        return changes

    @staticmethod
    def _parse_repo_name(line: str) -> Optional[str]:
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

    @staticmethod
    def _parse_commit(line: str) -> Optional[str]:
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
