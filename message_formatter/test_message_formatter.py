"""Provides tests for the message formatter."""
import unittest

from typing_extensions import Self

from github_util.pull_request import PullRequest
from message_formatter.message_formatter import MessageFormatter


class TestMessageFormatter(unittest.TestCase):
    """Provides tests for the message formatter."""

    def test_get_repo_pull_request_summary(self: Self) -> None:
        """The pull request summary should be formatted correctly."""
        summary = MessageFormatter.get_repo_pull_request_summary('repo1', [
            PullRequest(title='Pull Request 1', number=1, url='http://example.com/pr1'),
            PullRequest(title='Pull Request 2', number=2, url='http://example.com/pr2'),
        ])

        expected = (
            'repo1'
            '\n \t • *<http://example.com/pr1|Pull Request 1>* #1'
            '\n \t • *<http://example.com/pr2|Pull Request 2>* #2'
        )
        self.assertEqual(expected, summary)

    def test_get_message_header(self: Self) -> None:
        """The header should be formatted correctly."""
        self.assertEqual(
            'The Dev environment has been updated',
            MessageFormatter.get_message_header('Dev')
        )
