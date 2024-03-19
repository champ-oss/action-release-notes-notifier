"""Provide tests for example handler."""
import unittest

from git import Repo
from typing_extensions import Self

import main


class TestMain(unittest.TestCase):
    """Provide tests for main script."""

    def test_get_changes_from_last_commit(self: Self) -> None:
        """
        A repo commit change should be found in the most recent commit.

        :return:
        """
        repo = Repo()
        repo.remote().fetch()
        repo.git.checkout('test-image-change-1')
        changes = main.get_changes_from_last_commit(repo)
        self.assertEqual([{'ghi-client': '75ea3c7265ef1bf821397f88e8d42efdeea9561e'}], changes)

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
