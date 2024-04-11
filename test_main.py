"""Provide tests for example handler."""
import unittest
from unittest.mock import MagicMock

from typing_extensions import Self

import main
from git_util.file_diff import FileDiff
from github_util.pull_request import PullRequest


class TestMain(unittest.TestCase):
    """Provide tests for main script."""

    def test_main(self: Self) -> None:
        """
        The main function should be successful.

        :return:
        """
        git_util = MagicMock()
        git_util.get_file_diffs_from_last_commit.return_value = [
            FileDiff(file_name='terraform/env/dev/dev-a.tfvars', unified_diff=[
                '--- \n',
                '+++ \n',
                '@@ -1,2 +1,2 @@\n',
                '-test_repo_1 = "123.foo.com/test-repo-1:abc123"',
                '+test_repo_1 = "123.foo.com/test-repo-1:abc456"',
                '-test_repo_2 = "123.foo.com/bar/test-repo-2:def123"',
                '+test_repo_2 = "123.foo.com/bar/test-repo-2:def456"'
                '-foo         = "bar1"',
                '+foo         = "bar2"'
            ]),
            FileDiff(file_name='terraform/env/dev/dev-b.tfvars', unified_diff=[
                '--- \n',
                '+++ \n',
                '@@ -1,2 +1,2 @@\n',
                '-test_repo_3 = "123.foo.com/test-repo-3:ghi123"',
                '+test_repo_3 = "123.foo.com/test-repo-3:ghi456"',
            ])
        ]

        slack_notifier = MagicMock()
        github_util = MagicMock()
        github_util.get_pull_requests_for_commit.side_effect = [
            [
                PullRequest(url='https://foo.com/test_repo_1', title='Pull Request 123a', number=123),
                PullRequest(url='https://foo.com/test_repo_1', title='Pull Request 123b', number=124)
            ],
            [
                PullRequest(url='https://foo.com/test_repo_2', title='Pull Request 456', number=456)
            ],
            [
                PullRequest(url='https://foo.com/test_repo_3', title='Pull Request 789', number=789)
            ]
        ]

        main.main(git_util=git_util,
                  slack_notifier=slack_notifier,
                  github_util=github_util,
                  environment_name='Dev',
                  file_pattern='.*dev.*.tfvars',
                  tag_name='test-tag')

        expected_slack_message = (
            'The Dev environment has been updated\n'
            '\n'
            'test-repo-1\n'
            ' \t • *<https://foo.com/test_repo_1|Pull Request 123a>* #123\n'
            ' \t • *<https://foo.com/test_repo_1|Pull Request 123b>* #124\n'
            '\n'
            '\n'
            'test-repo-2\n'
            ' \t • *<https://foo.com/test_repo_2|Pull Request 456>* #456\n'
            '\n'
            '\n'
            'test-repo-3\n'
            ' \t • *<https://foo.com/test_repo_3|Pull Request 789>* #789\n'
            '\n'
        )
        self.assertEqual(expected_slack_message, slack_notifier.send_markdown.call_args[0][0])

    def test_main_slack_message_should_be_none_when_summary_is_empty(self: Self) -> None:
        """The Slack message should be None e when no repo information is added to the summary."""
        git_util = MagicMock()
        git_util.get_file_diffs_from_last_commit.return_value = [
            FileDiff(file_name='terraform/env/dev/dev-a.tfvars', unified_diff=[
                '--- \n',
                '+++ \n',
                '@@ -1,2 +1,2 @@\n'
                '-foo         = "bar1"',
                '+foo         = "bar2"'
            ])
        ]

        slack_notifier = MagicMock()
        main.main(git_util=git_util,
                  slack_notifier=slack_notifier,
                  github_util=MagicMock(),
                  environment_name='Dev',
                  file_pattern='.*dev.*.tfvars',
                  tag_name='test-tag')

        self.assertIsNone(slack_notifier.send_markdown.call_args[0][0])
