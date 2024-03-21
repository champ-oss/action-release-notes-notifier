"""Provides functionality for formatting the notification message."""
from typing import Optional

from typing_extensions import Self

from github_util.pull_request import PullRequest


class MessageFormatter:
    """Provides functionality for formatting the notification message."""

    def __init__(self: Self, environment_name: str) -> None:
        """
        Initialize the message formatter.

        :param environment_name: Name of the environment.
        """
        self._environment_name = environment_name
        self._summary = ''

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

    def get_final_summary(self: Self) -> Optional[str]:
        """
        Get the final overall summary message. If no information has been added, return None.

        :return:
        """
        if self._summary:
            return f'The {self._environment_name} environment has been updated\n' + self._summary
        return None
