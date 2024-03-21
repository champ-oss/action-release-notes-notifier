"""Represents a pull request."""
from dataclasses import dataclass


@dataclass
class PullRequest:
    """Represents a pull request."""

    title: str
    number: int
    url: str
