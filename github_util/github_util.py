"""Provides functionality for interfacing with GitHub repositories."""
import logging
from typing import Optional

from github import Github, Auth, UnknownObjectException, GithubException
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
        except (UnknownObjectException, GithubException) as e:
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
        except (UnknownObjectException, GithubException) as e:
            logger.warning(f'unable to find repository: {repo_name} error:{e}')
            return None

    def get_pull_requests_between_refs(self: Self, repo_name: str, base: str, head: str) -> list[PullRequest]:
        """
        Compare two git refs and get a list of pull requests between them.

        :param repo_name: name of the repository
        :param base: base ref to compare from
        :param head: head ref to compare to
        :return: list of pull requests
        """
        repo = self.get_repo(repo_name)
        if not repo:
            return []

        pull_requests: list[PullRequest] = []

        for commit in self._compare_and_get_merge_commit_hashes(repo, base, head):
            for pull_request in self._get_pull_requests_for_commit(repo, commit):
                if pull_request not in pull_requests:
                    pull_requests.append(pull_request)

        return pull_requests

    def _get_pull_requests_for_commit(self: Self, repo: Repository, commit: str) -> list[PullRequest]:
        """
        Get pull requests associated with a commit.

        :param repo: GitHub repository
        :param commit: commit to find pull requests for
        :return: list of pull requests
        """
        logger.info(f'getting pull requests for commit:{commit} in repo:{repo.name}')
        commit = self.get_repo_commit(repo, commit)
        if not commit:
            return []

        pull_requests = []
        for pr in commit.get_pulls():
            logger.info(f'found pull request: {repo.name} - #{pr.number} {pr.title}')
            pull_requests.append(PullRequest(title=pr.title, number=pr.number, url=pr.html_url))
        return pull_requests

    def tag_commit(self: Self, repo_name: str, commit: str, tag: str) -> None:
        """
        Tag a commit in a repository.

        :param repo_name: name of the repository
        :param commit: commit sha
        :param tag: name of the tag to apply to the commit
        """
        logger.info(f'tagging commit:{commit} in repo:{repo_name} with tag:{tag}')
        repo = self.get_repo(repo_name)
        if not repo:
            return

        if not self._update_git_tag(repo, commit, tag):
            self._create_git_tag(repo, commit, tag)

    @staticmethod
    def _compare_and_get_merge_commit_hashes(repo: Repository, base: str, head: str) -> list[str] | None:
        """
        Compare two git refs and get a list of merge commit hashes between them.

        :param repo: GitHub repository
        :param base: base ref to compare from
        :param head: head ref to compare to
        :return: list of git commit hashes
        """
        logger.info(f'Comparing {base} and {head} for repo:{repo.name}')
        comparison = repo.compare(base, head)
        commits = [commit.sha for commit in comparison.commits if len(commit.parents) > 1]
        logger.info(f'found {len(commits)} merge commits between {base} and {head} in {repo.name}')
        return commits

    @staticmethod
    def _update_git_tag(repo: Repository, commit: str, tag: str) -> bool:
        """
        Update a git tag in the repo if the tag already exists.

        :param repo: GitHub Repository
        :param commit: commit sha
        :param tag: name of the tag to update
        :return: true or false if the tag was updated successfully
        """
        try:
            repo.get_git_ref(f'tags/{tag}').edit(commit)
        except (UnknownObjectException, GithubException) as e:
            logger.debug(f'get_git_ref failed: {repo.name}:{commit} error:{e}')
            return False
        return True

    @staticmethod
    def _create_git_tag(repo: Repository, commit: str, tag: str) -> bool:
        """
        Create a git tag in the repo.

        :param repo: GitHub Repository
        :param commit: commit sha
        :param tag: name of the tag to create
        :return: true or false if the tag was created successfully
        """
        try:
            repo.create_git_ref(f'refs/tags/{tag}', commit)
        except (UnknownObjectException, GithubException) as e:
            logger.warning(f'unable to create git ref: {repo.name}:{commit} error:{e}')
            return False
        return True
