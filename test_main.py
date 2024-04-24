"""Provide tests for example handler."""
import unittest
from unittest.mock import MagicMock

from typing_extensions import Self

import main
from git_util.file_diff import FileDiff
from github_util.pull_request import PullRequest
from slack_notifier.slack_notifier import SlackNotifier


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

        slack_client = MagicMock()
        slack_client.send.return_value.status_code = 200
        slack_client.send.return_value.body = 'ok'

        main.main(git_util=git_util,
                  slack_notifier=SlackNotifier('', slack_client),
                  github_util=github_util,
                  environment_name='Dev',
                  file_pattern='.*dev.*.tfvars',
                  tag_name='test-tag')

        slack_client.send.assert_called_with(
            text='fallback',
            blocks=[
                {
                    'type': 'section',
                    'text': {
                        'type': 'mrkdwn',
                        'text': 'The Dev environment has been updated'
                    }
                },
                {
                    'type': 'section',
                    'text': {
                        'type': 'mrkdwn',
                        'text':
                            'test-repo-1'
                            '\n \t • *<https://foo.com/test_repo_1|Pull Request 123a>* #123'
                            '\n \t • *<https://foo.com/test_repo_1|Pull Request 123b>* #124'

                    }
                },
                {
                    'type': 'section',
                    'text': {
                        'type': 'mrkdwn',
                        'text':
                            'test-repo-2'
                            '\n \t • *<https://foo.com/test_repo_2|Pull Request 456>* #456'

                    }
                },
                {
                    'type': 'section',
                    'text': {
                        'type': 'mrkdwn',
                        'text':
                            'test-repo-3'
                            '\n \t • *<https://foo.com/test_repo_3|Pull Request 789>* #789'

                    }
                },
            ]
        )

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

        slack_client = MagicMock()
        slack_notifier = SlackNotifier('', slack_client)

        main.main(git_util=git_util,
                  slack_notifier=slack_notifier,
                  github_util=MagicMock(),
                  environment_name='Dev',
                  file_pattern='.*dev.*.tfvars',
                  tag_name='test-tag')

        self.assertFalse(slack_notifier.has_messages())
        slack_client.send.assert_not_called()
