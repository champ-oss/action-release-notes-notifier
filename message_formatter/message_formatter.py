"""Provides functionality for formatting the notification message."""
from typing_extensions import Self

from github_util.pull_request import PullRequest


class MessageFormatter:
    """Provides functionality for formatting the notification message."""

    @staticmethod
    def _create_summary(environment_name: str) -> str:
        """
        Create the summary message with the title header.

        :param environment_name: Name of the environment.
        :return: summary message
        """
        return f'The {environment_name} environment has been updated\n'

    def __init__(self: Self, environment_name: str) -> None:
        """
        Initialize the message formatter.

        :param environment_name: Name of the environment.
        """
        self._summary = MessageFormatter._create_summary(environment_name)

    def add_repo_pull_request_summary(self: Self, repo_name: str, pull_requests: list[PullRequest]) -> None:
        """
        Add a summary of each pull request for the repository to the summary.

        :param repo_name: Name of the repository.
        :param pull_requests: List of pull request information
        :return:
        """
        self._summary += f'\n{repo_name}'
        for pull_request in pull_requests:
            self._summary += f'\n \t • *<{pull_request.url}|{pull_request.title}>* #{pull_request.number}'
        self._summary += '\n\n'

    def get_summary(self: Self) -> str:
        """
        Get the summary message.

        :return:
        """
        return self._summary
