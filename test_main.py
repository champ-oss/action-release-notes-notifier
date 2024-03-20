"""Provide tests for example handler."""
import unittest
from unittest.mock import MagicMock

from typing_extensions import Self

import main


class TestMain(unittest.TestCase):
    """Provide tests for main script."""

    def setUp(self: Self) -> None:
        """
        Set up the environment for tests.

        :return:
        """
        pass

    def tearDown(self: Self) -> None:
        """
        Clean up the environment after tests.

        :return:
        """
        pass

    def test_parse_repo_name(self: Self) -> None:
        """
        A repo name should be parsed from a line of text.

        :return:
        """
        self.assertEqual('test-repo-1', main.parse_repo_name('test_repo_1 = "123.foo.com/bar/test-repo-1:abc123"'))
        self.assertEqual('test-repo-1', main.parse_repo_name('test_repo_1 = "123.foo.com/test-repo-1:abc123"'))
        self.assertEqual('test-repo-1', main.parse_repo_name('test_repo_1 = "test-repo-1:abc123"'))
        self.assertIsNone(main.parse_repo_name('test_repo_1 = "123.foo.com/test:v1.2"'))
        self.assertIsNone(main.parse_repo_name('test_repo_1 = "https://foo.com"'))
        self.assertIsNone(main.parse_repo_name('bucket_arn = "arn:aws:s3:::foo-800000001"'))
        self.assertIsNone(main.parse_repo_name('snapshot = "arn:aws:rds:us-east-2:12345:cluster-202301062012000004"'))
        self.assertIsNone(main.parse_repo_name('name_suffix : "read_only"'))
        self.assertIsNone(main.parse_repo_name('LOCATIONS = "classpath:flyway/migrations,classpath:flyway/foo/bar"'))
        self.assertIsNone(main.parse_repo_name('  JAVA_OPTS = "--add-opens -javaagent:/opt/foo/foo.jar"'))

    def test_parse_commit(self: Self) -> None:
        """
        A commit should be parsed from a line of text.

        :return:
        """
        self.assertEqual('abc123', main.parse_commit('test_repo_1 = "123.foo.com/bar/test-repo-1:abc123"'))
        self.assertEqual('abc123', main.parse_commit('test_repo_1 = "123.foo.com/test-repo-1:abc123"'))
        self.assertEqual('abc123', main.parse_commit('test_repo_1 = "test-repo-1:abc123"'))
        self.assertIsNone(main.parse_commit('test_repo_1 = "123.foo.com/test:v1.2"'))
        self.assertIsNone(main.parse_commit('test_repo_1 = "https://foo.com"'))
        self.assertIsNone(main.parse_commit('bucket_arn = "arn:aws:s3:::foo-800000001"'))
        self.assertIsNone(main.parse_commit('snapshot = "arn:aws:rds:us-east-2:12345:cluster-202301062012000004"'))
        self.assertIsNone(main.parse_commit('name_suffix : "read_only"'))
        self.assertIsNone(main.parse_commit('LOCATIONS = "classpath:flyway/migrations,classpath:flyway/foo/bar"'))
        self.assertIsNone(main.parse_commit('  JAVA_OPTS = "--add-opens -javaagent:/opt/foo/foo.jar"'))

    def test_get_pull_request_summary_from_commit(self: Self) -> None:
        """
        A summary of pull requests should be returned from a commit.

        :return:
        """
        org = MagicMock()
        repo = MagicMock()
        repo.get_commit.return_value.get_pulls.return_value = [
            MagicMock(html_url='https://foo.com', title='Pull Request 1', number=1)
        ]
        org.get_repo.return_value = repo

        summary = main.get_pull_request_summary_from_commit(org, 'test-repo-1', 'abc123')
        self.assertEqual('test-repo-1\n \t • *<https://foo.com|Pull Request 1>* #1', summary)

    def test_get_changes_from_last_commit(self: Self) -> None:
        """
        A diff of changes should be returned from the most recent commit.

        :return:
        """
        repo = MagicMock()

        file1 = MagicMock()
        file1.b_path = 'foo/bar1.txt'
        file1.b_blob.data_stream.read.return_value = b'test_repo_1 = "123.foo.com/test-repo-1:abc123"'
        file1.a_blob.data_stream.read.return_value = b'test_repo_1 = "123.foo.com/test-repo-1:abc456"'

        file2 = MagicMock()
        file2.b_path = 'foo/bar2.txt'
        file2.b_blob.data_stream.read.return_value = b'test_repo_2 = "123.foo.com/test-repo-2:abc123"'
        file2.a_blob.data_stream.read.return_value = b'test_repo_2 = "123.foo.com/test-repo-2:abc456"'

        repo.head.commit.diff.return_value = [file1, file2]
        changes = main.get_changes_from_last_commit(repo)
        self.assertEqual({'test-repo-1': 'abc456', 'test-repo-2': 'abc456'}, changes)
