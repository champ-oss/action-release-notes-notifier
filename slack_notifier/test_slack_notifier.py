"""Provides tests for SlackNotifier."""
import unittest
from unittest.mock import MagicMock

from typing_extensions import Self

from slack_notifier.slack_notifier import SlackNotifier


class TestSlackNotifier(unittest.TestCase):
    """Provides tests for SlackNotifier."""

    def test_add_message_block(self: Self) -> None:
        """The add_message_block function should add a message block."""
        slack_notifier = SlackNotifier('https://example.com')

        self.assertFalse(slack_notifier.has_messages())
        slack_notifier.add_message_block('test message 1')
        slack_notifier.add_message_block('test message 2')
        slack_notifier.add_message_block('test message header', at_beginning=True)
        self.assertEqual(slack_notifier._message_blocks, [
            {
                'type': 'section',
                'text': {
                    'type': 'mrkdwn',
                    'text': 'test message header'
                }
            },
            {
                'type': 'section',
                'text': {
                    'type': 'mrkdwn',
                    'text': 'test message 1'
                }
            },
            {
                'type': 'section',
                'text': {
                    'type': 'mrkdwn',
                    'text': 'test message 2'
                }
            }
        ])
        self.assertTrue(slack_notifier.has_messages())

    def test_add_message_block_when_message_empty(self: Self) -> None:
        """The add_message_block function should not add a message block if the message is empty."""
        slack_notifier = SlackNotifier('https://example.com')
        self.assertFalse(slack_notifier.has_messages())
        slack_notifier.add_message_block('')
        slack_notifier.add_message_block(None)
        self.assertFalse(slack_notifier.has_messages())

    def test_add_message_block_when_message_too_large(self: Self) -> None:
        """The add_message_block function should truncate the message if the message too large."""
        slack_notifier = SlackNotifier('https://example.com')
        self.assertFalse(slack_notifier.has_messages())

        test_message_line = 'This is a long sentence.\n'

        with self.assertLogs(level='WARNING') as logs:
            slack_notifier.add_message_block(test_message_line * 500)
            self.assertIn('message is longer than the Slack limit of 3000 characters', logs.output[0])

        self.assertEqual(2999, len(slack_notifier._message_blocks[0]['text']['text']))
        expected_lines = int(len(slack_notifier._message_blocks[0]['text']['text']) / len(test_message_line)) + 1

        self.maxDiff = None
        self.assertEqual(slack_notifier._message_blocks, [
            {
                'type': 'section',
                'text': {
                    'type': 'mrkdwn',
                    'text': (test_message_line * expected_lines).strip()
                }
            }
        ])

    def test_send_message(self: Self) -> None:
        """The send_message function should be successful."""
        webhook_client = MagicMock()
        webhook_client.send.return_value.status_code = 200
        webhook_client.send.return_value.body = 'ok'

        slack_notifier = SlackNotifier('https://example.com', webhook_client)
        slack_notifier.add_message_block('test message')
        slack_notifier.send_message()

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

    def test_send_message_when_empty(self: Self) -> None:
        """The send_message function should not send a message when the message blocks are empty."""
        webhook_client = MagicMock()
        slack_notifier = SlackNotifier('https://example.com', webhook_client)
        slack_notifier.send_message()
        webhook_client.send.assert_not_called()
        self.assertFalse(slack_notifier.has_messages())

    def test_send_message_when_too_many_blocks(self: Self) -> None:
        """The send_message function should log a warning when there are too many blocks."""
        webhook_client = MagicMock()
        slack_notifier = SlackNotifier('https://example.com', webhook_client)
        webhook_client.send.return_value.status_code = 200
        webhook_client.send.return_value.body = 'ok'

        for _ in range(51):
            slack_notifier.add_message_block('test message')

        self.assertTrue(slack_notifier.has_messages())
        self.assertEqual(len(slack_notifier._message_blocks), 51)

        with self.assertLogs(level='WARNING') as logs:
            slack_notifier.send_message()
            self.assertIn('message is greater than the Slack limit of 50 blocks', logs.output[0])

        webhook_client.send.assert_called_once()
        self.assertEqual(50, len(webhook_client.send.call_args[1]['blocks']))
