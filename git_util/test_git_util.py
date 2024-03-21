"""Provides unit tests for the GitUtil class."""
import unittest
from unittest.mock import MagicMock

from typing_extensions import Self

from git_util.git_util import GitUtil


class TestGitUtil(unittest.TestCase):
    """Provides unit tests for the GitUtil class."""

    def test_get_file_diff_from_git_diff(self: Self) -> None:
        """Validate the _get_file_diff_from_git_diff method is successful."""
        diff = MagicMock()
        diff.b_path = 'test.txt'
        diff.b_blob.data_stream.read.return_value = b'hello\nworld1\n'
        diff.a_blob.data_stream.read.return_value = b'hello\nworld2\n'

        file_diff = GitUtil._get_file_diff_from_git_diff(diff)
        self.assertEqual(file_diff.file_name, 'test.txt')
        self.assertEqual(
            [
                '--- \n',
                '+++ \n',
                '@@ -1,2 +1,2 @@\n',
                ' hello',
                '-world1',
                '+world2'
            ], list(file_diff.unified_diff)
        )

    def test_get_file_diffs_from_last_commit_with_multiple_files(self: Self) -> None:
        """Validate multiple file diffs are returned."""
        git_diff_file_1 = MagicMock()
        git_diff_file_1.b_path = 'terraform/env/dev-1.tfvars'
        git_diff_file_1.b_blob.data_stream.read.return_value = b'hello\nworld1\n'
        git_diff_file_1.a_blob.data_stream.read.return_value = b'hello\nworld2\n'

        git_diff_file_2 = MagicMock()
        git_diff_file_2.b_path = 'terraform/env/dev-2.tfvars'
        git_diff_file_2.b_blob.data_stream.read.return_value = b'hello\nworld3\n'
        git_diff_file_2.a_blob.data_stream.read.return_value = b'hello\nworld4\n'

        repo = MagicMock()
        repo.head.commit.diff.return_value = [git_diff_file_1, git_diff_file_2]

        git_util = GitUtil(repo)
        file_diffs = git_util.get_file_diffs_from_last_commit('.*dev.*.tfvars')
        self.assertEqual(len(file_diffs), 2)

        self.assertEqual(file_diffs[0].file_name, 'terraform/env/dev-1.tfvars')
        self.assertEqual(
            [
                '--- \n',
                '+++ \n',
                '@@ -1,2 +1,2 @@\n',
                ' hello',
                '-world1',
                '+world2'
            ],
            list(file_diffs[0].unified_diff)
        )

        self.assertEqual(file_diffs[1].file_name, 'terraform/env/dev-2.tfvars')
        self.assertEqual(
            [
                '--- \n',
                '+++ \n',
                '@@ -1,2 +1,2 @@\n',
                ' hello',
                '-world3',
                '+world4'
            ],
            list(file_diffs[1].unified_diff)
        )

    def test_get_file_diffs_from_last_commit_with_filtered_files(self: Self) -> None:
        """Validate the undesired files are filtered out."""
        repo = MagicMock()
        repo.head.commit.diff.return_value = [
            MagicMock(b_path='terraform/env/dev-1.tfvars'),
            MagicMock(b_path='terraform/env/qa.tfvars'),
            MagicMock(b_path='main.tf'),
            MagicMock(b_path='foo.tfvars')
        ]
        git_util = GitUtil(repo)
        file_diffs = git_util.get_file_diffs_from_last_commit('.*dev.*.tfvars')
        self.assertEqual(len(file_diffs), 1)
