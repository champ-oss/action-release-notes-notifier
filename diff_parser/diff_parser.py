"""Provides functionality for parsing git diffs."""
import logging
import re
from typing import Optional, Iterator, List

from diff_parser.RepoCommitChange import RepoCommitChange

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
        changes: List[RepoCommitChange] = []
        diff_list = list(unified_diff)

        for i in range(len(diff_list)):
            logger.info(diff_list[i])
            if not diff_list[i].startswith('+'):
                continue

            repo = DiffParser._parse_repo_name(diff_list[i])
            new_commit = DiffParser._parse_commit(diff_list[i])
            old_commit = DiffParser._parse_commit(diff_list[i - 1])
            if repo and new_commit:
                logger.info(f'found change: repo:{repo} old-commit:{old_commit} new-commit:{new_commit}')
                changes.append(RepoCommitChange(repository=repo, old_commit=old_commit, new_commit=new_commit))

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
