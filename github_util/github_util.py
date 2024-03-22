"""Provides functionality for interfacing with GitHub repositories."""
import logging
from typing import Optional

from github import Github, Auth, UnknownObjectException
from github.Commit import Commit
from github.Repository import Repository
from typing_extensions import Self

from github_util.pull_request import PullRequest

logger = logging.getLogger(__name__)


class GitHubUtil:
    """Provides functionality for interfacing with GitHub repositories."""

    @staticmethod
    def get_repo_commit(repo: Repository, commit: str) -> Optional[Commit]:
        """
        Get a commit by hash.

        :param repo: GitHub repository
        :param commit: commit hash
        :return: GitHub commit
        """
        try:
            return repo.get_commit(commit)
        except UnknownObjectException as e:
            logger.warning(f'unable to find repo commit: {repo}:{commit} error:{e}')
            return None

    def __init__(self: Self, access_token: str, organization_name: str, github_session: Github = None) -> None:
        """
        Initialize the GitHub utility.

        :param access_token: GitHub personal access token
        :param organization_name: Name of the GitHub organization
        :param github_session: authenticated session to GitHub
        """
        if not github_session:
            logger.info('logging in to GitHub using access token')
            self.github_session = Github(auth=Auth.Token(access_token))
        else:
            self.github_session = github_session

        logger.info(f'getting GitHub organization: {organization_name}')
        self.organization = self.github_session.get_organization(organization_name)

    def get_repo(self: Self, repo_name: str) -> Optional[Repository]:
        """
        Get a repository by name.

        :param repo_name: name of the repository
        :return: GitHub repository
        """
        try:
            return self.organization.get_repo(repo_name)
        except UnknownObjectException as e:
            logger.warning(f'unable to find repository: {repo_name} error:{e}')
            return None

    def get_pull_requests_for_commit(self: Self, repo_name: str, commit: str) -> list[PullRequest]:
        """
        Get pull requests associated with a commit.

        :param repo_name: name of the repository
        :param commit: commit to find pull requests for
        :return: list of pull requests
        """
        logger.info(f'getting pull requests for commit:{commit} in repo:{repo_name}')
        repo = self.get_repo(repo_name)
        if not repo:
            return []

        commit = self.get_repo_commit(repo, commit)
        if not commit:
            return []

        pull_requests = []
        for pr in commit.get_pulls():
            logger.info(f'found pull request: {repo_name} - #{pr.number} {pr.title}')
            pull_requests.append(PullRequest(title=pr.title, number=pr.number, url=pr.html_url))
        return pull_requests
