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
                '-test_repo_1 = "123.foo.com/test-repo-1:abc11"',
                '+test_repo_1 = "123.foo.com/test-repo-1:abc12"',
                '-test_repo_2 = "123.foo.com/bar/test-repo-2:abc21"',
                '+test_repo_2 = "123.foo.com/bar/test-repo-2:abc22"',
                '-foo         = "bar1"',
                '+foo         = "bar2"',
                '-test_repo_3 = "123.foo.com/test-repo-3:abc31"',
                '-test_repo_4 = "123.foo.com/bar/test-repo-4:abc41"',
                '+test_repo_3 = "123.foo.com/test-repo-3:abc32"',
                '+test_repo_4 = "123.foo.com/bar/test-repo-4:abc42"',
                '+test_repo_5 = "123.foo.com/bar/test-repo-5:abc52"',
                '-test_repo_6 = "123.foo.com/bar/test-repo-6:abc61"'
            ]),
            FileDiff(file_name='terraform/env/dev/dev-b.tfvars', unified_diff=[
                '--- \n',
                '+++ \n',
                '@@ -1,2 +1,2 @@\n',
                '-test_repo_6 = "123.foo.com/test-repo-6:ghi123"',
                '+test_repo_6 = "123.foo.com/test-repo-6:ghi456"',
            ])
        ]

        github_util = MagicMock()
        github_util.get_pull_requests_between_refs.side_effect = [
            [
                PullRequest(url='https://foo.com/test_repo_1', title='Pull Request 123a', number=123),
                PullRequest(url='https://foo.com/test_repo_1', title='Pull Request 123b', number=124)
            ],
            [
                PullRequest(url='https://foo.com/test_repo_2', title='Pull Request 456', number=456)
            ],
            [
                PullRequest(url='https://foo.com/test_repo_3', title='Pull Request 789', number=789)
            ],
            [],
            [
                PullRequest(url='https://foo.com/test_repo_5', title='Pull Request 2221', number=2221),
                PullRequest(url='https://foo.com/test_repo_5', title='Pull Request 2222', number=2222)
            ],
            [
                PullRequest(url='https://foo.com/test_repo_6', title='Pull Request 333', number=333)
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

        expected_blocks = [
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
            {
                'type': 'section',
                'text': {
                    'type': 'mrkdwn',
                    'text':
                        'test-repo-4'

                }
            },
            {
                'type': 'section',
                'text': {
                    'type': 'mrkdwn',
                    'text':
                        'test-repo-5'
                        '\n \t • *<https://foo.com/test_repo_5|Pull Request 2221>* #2221'
                        '\n \t • *<https://foo.com/test_repo_5|Pull Request 2222>* #2222'

                }
            },
            {
                'type': 'section',
                'text': {
                    'type': 'mrkdwn',
                    'text':
                        'test-repo-6'
                        '\n \t • *<https://foo.com/test_repo_6|Pull Request 333>* #333'

                }
            },
        ]
        self.assertEqual(expected_blocks, slack_client.send.call_args.kwargs['blocks'])

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
