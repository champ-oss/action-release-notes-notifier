"""Provides functionality to interact with the local git repository."""
import difflib
import logging
import re
from typing import List

from git import Repo, Diff
from typing_extensions import Self

from git_util.file_diff import FileDiff

logger = logging.getLogger(__name__)


class GitUtil:
    """Provides functionality to interact with the local git repository."""

    @staticmethod
    def _get_file_diff_from_git_diff(diff: Diff) -> FileDiff:
        """
        Get a FileDiff from a git.Diff object.

        :param diff: git.Diff object
        :return: FileDiff
        """
        return FileDiff(
            file_name=diff.b_path,
            unified_diff=difflib.unified_diff(diff.b_blob.data_stream.read().decode('utf-8').splitlines(),
                                              diff.a_blob.data_stream.read().decode('utf-8').splitlines())
        )

    def __init__(self: Self, repo: Repo = None) -> None:
        """
        Initialize the GitUtil.

        :param repo: git repo object
        """
        if not repo:
            logger.info('loading local repository')
            self.repo = Repo()
        else:
            self.repo = repo

    def get_file_diffs_from_last_commit(self: Self, file_name_pattern_filter: str) -> List[FileDiff]:
        """
        Get a list of file diffs from the last git commit.

        :param file_name_pattern_filter: Regex pattern to filter file names
        :return: list of FileDiffs
        """
        file_diffs: List[FileDiff] = []

        for item in self.repo.head.commit.diff('HEAD~1', create_patch=True):
            logger.info(f'found changed file: {item.b_path}')

            if re.match(file_name_pattern_filter, item.b_path) is None:
                logger.info(f'skipping file: {item.b_path}')
                continue

            file_diffs.append(self._get_file_diff_from_git_diff(item))

        return file_diffs
