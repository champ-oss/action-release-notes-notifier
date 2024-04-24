"""Provides functionality for formatting the notification message."""
from github_util.pull_request import PullRequest


class MessageFormatter:
    """Provides functionality for formatting the notification message."""

    @staticmethod
    def get_message_header(environment_name: str) -> str:
        """
        Get the header for the message.

        :param environment_name: Name of the environment being updated
        :return:
        """
        return f'The {environment_name} environment has been updated'

    @staticmethod
    def get_repo_pull_request_summary(repo_name: str, pull_requests: list[PullRequest]) -> str:
        """
        Add a summary of each pull request for the repository to the summary.

        :param repo_name: Name of the repository.
        :param pull_requests: List of pull request information
        :return:
        """
        summary = repo_name
        for pull_request in pull_requests:
            summary += f'\n \t • *<{pull_request.url}|{pull_request.title}>* #{pull_request.number}'
        return summary
