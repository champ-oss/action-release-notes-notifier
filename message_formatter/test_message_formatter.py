"""Provides tests for the message formatter."""
import unittest

from typing_extensions import Self

from github_util.pull_request import PullRequest
from message_formatter.message_formatter import MessageFormatter


class TestMessageFormatter(unittest.TestCase):
    """Provides tests for the message formatter."""

    def test_create_summary(self: Self) -> None:
        """Validate the summary message is created correctly."""
        summary = MessageFormatter._create_summary('Dev')
        self.assertEqual(summary, 'The Dev environment has been updated\n')

    def test_add_repo_pull_request_summary(self: Self) -> None:
        """Validate the pull requests are added to the summary correctly."""
        message_formatter = MessageFormatter('Dev')
        message_formatter.add_repo_pull_request_summary('repo1', [
            PullRequest(title='Pull Request 1', number=1, url='http://example.com/pr1'),
            PullRequest(title='Pull Request 2', number=2, url='http://example.com/pr2'),
        ])
        message_formatter.add_repo_pull_request_summary('repo2', [
            PullRequest(title='Pull Request 3', number=3, url='http://example.com/pr3'),
            PullRequest(title='Pull Request 4', number=4, url='http://example.com/pr4'),
        ])

        expected = (
            'The Dev environment has been updated\n'
            '\n'
            'repo1\n'
            ' \t • *<http://example.com/pr1|Pull Request 1>* #1\n'
            ' \t • *<http://example.com/pr2|Pull Request 2>* #2\n'
            '\n'
            '\n'
            'repo2\n'
            ' \t • *<http://example.com/pr3|Pull Request 3>* #3\n'
            ' \t • *<http://example.com/pr4|Pull Request 4>* #4\n'
            '\n'
        )

        summary = message_formatter.get_summary()
        self.assertEqual(expected, summary)
