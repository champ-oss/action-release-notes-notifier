"""Provide tests for example handler."""
import unittest
from pathlib import Path
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

    def test_main(self: Self) -> None:
        """
        The main function should be successful.

        :return:
        """
        # Prepare file diffs
        repo = MagicMock()
        file1 = MagicMock()
        file1.b_path = 'terraform/env/dev/dev-a.tfvars'
        file1.b_blob.data_stream.read.return_value = b'''
        test_repo_1 = "123.foo.com/test-repo-1:abc123"
        test_repo_2 = "123.foo.com/bar/test-repo-2:def123"
        foo         = "bar1"'''

        file1.a_blob.data_stream.read.return_value = b'''
        test_repo_1 = "123.foo.com/test-repo-1:abc456"
        test_repo_2 = "123.foo.com/bar/test-repo-2:def456"
        foo         = "bar2"'''

        file2 = MagicMock()
        file2.b_path = 'terraform/env/dev/dev-b.tfvars'
        file2.b_blob.data_stream.read.return_value = b'test_repo_3 = "123.foo.com/test-repo-3:ghi123"'
        file2.a_blob.data_stream.read.return_value = b'test_repo_3 = "123.foo.com/test-repo-3:ghi456"'

        repo.head.commit.diff.return_value = [file1, file2]

        # Prepare pull request information
        test_repo_1 = MagicMock()
        test_repo_1.get_commit.return_value.get_pulls.return_value = [
            MagicMock(html_url='https://foo.com/test_repo_1', title='Pull Request 123', number=123)
        ]
        test_repo_2 = MagicMock()
        test_repo_2.get_commit.return_value.get_pulls.return_value = [
            MagicMock(html_url='https://foo.com/test_repo_2', title='Pull Request 456', number=456)
        ]
        test_repo_3 = MagicMock()
        test_repo_3.get_commit.return_value.get_pulls.return_value = [
            MagicMock(html_url='https://foo.com/test_repo_3', title='Pull Request 789', number=789)
        ]

        github_session = MagicMock()
        org = MagicMock()
        github_session.get_organization.return_value = org
        org.get_repo.side_effect = [test_repo_1, test_repo_2, test_repo_3]

        # Prepare webhook client
        webhook_client = MagicMock()
        webhook_client.send.return_value = MagicMock(status_code=200, body='ok')

        file_pattern = '.*dev.*.tfvars'

        main.main(repo, webhook_client, github_session, 'test', 'Dev', file_pattern)

        webhook_client.send.assert_called_once()

        with Path('test_expected_message.txt').open() as f:
            expected_slack_message = f.read()
        self.assertEquals(expected_slack_message, webhook_client.send.call_args[1]['blocks'][0]['text']['text'])

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
        self.assertEqual('\ntest-repo-1\n \t • *<https://foo.com|Pull Request 1>* #1', summary)

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
        changes = main.get_changes_from_last_commit(repo, '.*bar.*.txt')
        self.assertEqual({'test-repo-1': 'abc456', 'test-repo-2': 'abc456'}, changes)

    def test_matches_file_pattern(self: Self) -> None:
        """
        A file path should match a pattern.

        :return:
        """
        self.assertTrue(main.matches_file_pattern('terraform/env/dev/dev-defaults.tfvars', '.*dev.*.tfvars'))
        self.assertTrue(main.matches_file_pattern('terraform/env/dev/dev.tfvars', '.*dev.*.tfvars'))
        self.assertTrue(main.matches_file_pattern('terraform/env/dev/dev-foo.tfvars', '.*dev.*.tfvars'))
        self.assertFalse(main.matches_file_pattern('terraform/env/test/test.tfvars', '.*dev.*.tfvars'))
        self.assertFalse(main.matches_file_pattern('terraform/main.tf', '.*dev.*.tfvars'))
        self.assertFalse(main.matches_file_pattern('terraform/main.tfvars', '.*dev.*.tfvars'))
