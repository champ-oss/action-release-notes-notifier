"""Provides functionality for parsing git diffs."""
import logging
import re
from typing import Optional, Iterator, List

from diff_parser.repo_commit_change import RepoCommitChange

logger = logging.getLogger(__name__)


class DiffParser:
    """Provides functionality for parsing git diffs."""

    @staticmethod
    def get_repo_commit_changes(unified_diff: Iterator[str]) -> List[RepoCommitChange]:
        """
        Parse the diff string to get the repo and commit changes.

        :param unified_diff: unified diff string
        :return: list of changes
        """
        changes: dict[str, RepoCommitChange] = {}

        for line in unified_diff:
            repo = DiffParser._parse_repo_name(line)
            if not repo:
                continue
            if not changes.get(repo):
                changes[repo] = RepoCommitChange(repository=repo)

            if line.startswith('+'):
                changes[repo].new_commit = DiffParser._parse_commit(line)

            if line.startswith('-'):
                changes[repo].old_commit = DiffParser._parse_commit(line)

        for repo, change in changes.items():
            if not change.new_commit:
                continue
            logger.info(f'found change: repo:{repo} old-commit:{change.old_commit} new-commit:{change.new_commit}')
            yield change

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
