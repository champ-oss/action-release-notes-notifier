"""Represents a pull request."""
from dataclasses import dataclass


@dataclass
class RepoCommitChange:
    """Represents a change for a repository and commit."""

    repository: str
    old_commit: str = ''
    new_commit: str = ''
