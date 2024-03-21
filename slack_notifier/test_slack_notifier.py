"""Provides tests for SlackNotifier."""
import unittest
from unittest.mock import MagicMock

from typing_extensions import Self

from slack_notifier.slack_notifier import SlackNotifier


class TestSlackNotifier(unittest.TestCase):
    """Provides tests for SlackNotifier."""

    def test_send_markdown(self: Self) -> None:
        """The send_markdown function should be successful."""
        webhook_client = MagicMock()
        webhook_client.send.return_value.status_code = 200
        webhook_client.send.return_value.body = 'ok'

        slack_notifier = SlackNotifier('https://example.com', webhook_client)
        slack_notifier.send_markdown('test message')

        webhook_client.send.assert_called_once()
        webhook_client.send.assert_called_with(
            text='fallback',
            blocks=[
                {
                    'type': 'section',
                    'text': {
                        'type': 'mrkdwn',
                        'text': 'test message'
                    }
                }
            ]
        )
