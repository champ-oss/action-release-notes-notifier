"""Provides functionality to send messages to Slack."""
import logging

from slack_sdk import WebhookClient
from typing_extensions import Self

logger = logging.getLogger(__name__)


class SlackNotifier:
    """Provides functionality to send messages to Slack."""

    _message_blocks = None

    def __init__(self: Self, webhook_url: str, webhook_client: WebhookClient = None) -> None:
        """
        Initialize the SlackNotifier.

        :param webhook_url: Webhook URL to send messages
        :param webhook_client: Optionally inject a WebhookClient
        """
        self._message_blocks = []
        if not webhook_client:
            self._webhook_client = WebhookClient(webhook_url)
        else:
            self._webhook_client = webhook_client

    def add_message_block(self: Self, message: str, at_beginning: bool = False) -> None:
        """
        Add a message block to be sent to Slack.

        :param message: text of the message
        :param at_beginning: If true, add the message to the beginning (a header for example)
        :return: None
        """
        if not message:
            return

        if len(message) > 3000:
            logger.warning('message is longer than the Slack limit of 3000 characters and will be truncated '
                           '(https://api.slack.com/reference/block-kit/composition-objects#text)')
            message = message[:3000].rsplit('\n', 1)[0]  # truncate the message after the last newline

        block = {
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': message[:3000]
            }
        }
        if at_beginning:
            self._message_blocks.insert(0, block)
        else:
            self._message_blocks.append(block)

    def has_messages(self: Self) -> bool:
        """
        Check if there are messages to send.

        :return: True if there are messages, False otherwise
        """
        return len(self._message_blocks) > 0

    def send_message(self: Self) -> None:
        """
        Send a message to Slack using the message blocks.

        :return: None
        """
        if len(self._message_blocks) == 0:
            logger.info('not sending Slack message because message is empty')
            return

        if len(self._message_blocks) > 50:
            logger.warning('message is greater than the Slack limit of 50 blocks, only the first 50 blocks will be sent'
                           '(https://api.slack.com/reference/block-kit/blocks)')

        logger.info('sending message to Slack')
        response = self._webhook_client.send(text='fallback', blocks=self._message_blocks[:50])
        logger.info(f'response from Slack: {response.status_code} {response.body}')
        assert response.status_code == 200
