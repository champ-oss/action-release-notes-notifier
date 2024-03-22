"""Provides functionality to send messages to Slack."""
import logging

from slack_sdk import WebhookClient
from typing_extensions import Self

logger = logging.getLogger(__name__)


class SlackNotifier:
    """Provides functionality to send messages to Slack."""

    def __init__(self: Self, webhook_url: str, webhook_client: WebhookClient = None) -> None:
        """
        Initialize the SlackNotifier.

        :param webhook_url: Webhook URL to send messages
        :param webhook_client: Optionally inject a WebhookClient
        """
        if not webhook_client:
            self._webhook_client = WebhookClient(webhook_url)
        else:
            self._webhook_client = webhook_client

    def send_markdown(self: Self, message: str) -> None:
        """
        Send a message to Slack in Markdown format.

        :param message: message to send
        :return: None
        """
        if not message:
            logger.info('not sending Slack message because message is empty')
            return

        logger.info('sending message to Slack')
        response = self._webhook_client.send(
            text='fallback',
            blocks=[
                {
                    'type': 'section',
                    'text': {
                        'type': 'mrkdwn',
                        'text': message
                    }
                }
            ]
        )
        logger.info(f'response from Slack: {response.status_code} {response.body}')
