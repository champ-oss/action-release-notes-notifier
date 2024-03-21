"""Represents a git diff for a single file."""
from dataclasses import dataclass
from typing import Iterator


@dataclass
class FileDiff:
    """Represents a git diff for a single file."""

    file_name: str
    unified_diff: Iterator[str]
