"""Provide tests for diff_parser."""
import unittest

from typing_extensions import Self

from diff_parser.diff_parser import DiffParser


class TestDiffParser(unittest.TestCase):
    """Provide tests for diff_parser."""

    def test_parse_repo_name(self: Self) -> None:
        """
        A repo name should be parsed from a line of text.

        :return:
        """
        self.assertEqual('test-repo-1',
                         DiffParser._parse_repo_name('test_repo_1 = "123.foo.com/bar/test-repo-1:abc123"'))
        self.assertEqual('test-repo-1', DiffParser._parse_repo_name('test_repo_1 = "123.foo.com/test-repo-1:abc123"'))
        self.assertEqual('test-repo-1', DiffParser._parse_repo_name('test_repo_1 = "test-repo-1:abc123"'))
        self.assertIsNone(DiffParser._parse_repo_name('test_repo_1 = "123.foo.com/test:v1.2"'))
        self.assertIsNone(DiffParser._parse_repo_name('test_repo_1 = "https://foo.com"'))
        self.assertIsNone(DiffParser._parse_repo_name('bucket_arn = "arn:aws:s3:::foo-800000001"'))
        self.assertIsNone(
            DiffParser._parse_repo_name('snapshot = "arn:aws:rds:us-east-2:12345:cluster-202301062012000004"'))
        self.assertIsNone(DiffParser._parse_repo_name('name_suffix : "read_only"'))
        self.assertIsNone(
            DiffParser._parse_repo_name('LOCATIONS = "classpath:flyway/migrations,classpath:flyway/foo/bar"'))
        self.assertIsNone(DiffParser._parse_repo_name('  JAVA_OPTS = "--add-opens -javaagent:/opt/foo/foo.jar"'))

    def test_parse_commit(self: Self) -> None:
        """
        A commit should be parsed from a line of text.

        :return:
        """
        self.assertEqual('abc123', DiffParser._parse_commit('test_repo_1 = "123.foo.com/bar/test-repo-1:abc123"'))
        self.assertEqual('abc123', DiffParser._parse_commit('test_repo_1 = "123.foo.com/test-repo-1:abc123"'))
        self.assertEqual('abc123', DiffParser._parse_commit('test_repo_1 = "test-repo-1:abc123"'))
        self.assertIsNone(DiffParser._parse_commit('test_repo_1 = "123.foo.com/test:v1.2"'))
        self.assertIsNone(DiffParser._parse_commit('test_repo_1 = "https://foo.com"'))
        self.assertIsNone(DiffParser._parse_commit('bucket_arn = "arn:aws:s3:::foo-800000001"'))
        self.assertIsNone(
            DiffParser._parse_commit('snapshot = "arn:aws:rds:us-east-2:12345:cluster-202301062012000004"'))
        self.assertIsNone(DiffParser._parse_commit('name_suffix : "read_only"'))
        self.assertIsNone(
            DiffParser._parse_commit('LOCATIONS = "classpath:flyway/migrations,classpath:flyway/foo/bar"'))
        self.assertIsNone(DiffParser._parse_commit('  JAVA_OPTS = "--add-opens -javaagent:/opt/foo/foo.jar"'))
