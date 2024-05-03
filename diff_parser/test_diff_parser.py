"""Provide tests for diff_parser."""
import pytest

from diff_parser.diff_parser import DiffParser
from diff_parser.repo_commit_change import RepoCommitChange


def test_get_repo_commit_changes() -> None:
    """Validate the get_repo_commit_changes method is successful."""
    changes = DiffParser.get_repo_commit_changes(
        unified_diff=[
            '--- \n',
            '+++ \n',
            '@@ -1,2 +1,2 @@\n',
            '-test_repo_1 = "123.foo.com/test-repo-1:abc11"',
            '+test_repo_1 = "123.foo.com/test-repo-1:abc12"',
            '-test_repo_2 = "123.foo.com/bar/test-repo-2:abc21"',
            '+test_repo_2 = "123.foo.com/bar/test-repo-2:abc22"',
            '-foo         = "bar1"',
            '+foo         = "bar2"',
            '-test_repo_3 = "123.foo.com/test-repo-3:abc31"',
            '-test_repo_4 = "123.foo.com/bar/test-repo-4:abc41"',
            '+test_repo_3 = "123.foo.com/test-repo-3:abc32"',
            '+test_repo_4 = "123.foo.com/bar/test-repo-4:abc42"',
            '+test_repo_5 = "123.foo.com/bar/test-repo-5:abc52"',
            '-test_repo_6 = "123.foo.com/bar/test-repo-6:abc61"'
        ]
    )
    assert list(changes) == [
        RepoCommitChange(repository='test-repo-1', old_commit='abc11', new_commit='abc12'),
        RepoCommitChange(repository='test-repo-2', old_commit='abc21', new_commit='abc22'),
        RepoCommitChange(repository='test-repo-3', old_commit='abc31', new_commit='abc32'),
        RepoCommitChange(repository='test-repo-4', old_commit='abc41', new_commit='abc42'),
        RepoCommitChange(repository='test-repo-5', old_commit='', new_commit='abc52')
    ]


@pytest.mark.parametrize('test_input,expected', [
    ('test_repo_1 = "123.foo.com/bar/test-repo-1:abc123"', 'test-repo-1'),
    ('test_repo_1 = "123.foo.com/test-repo-1:abc123"', 'test-repo-1'),
    ('test_repo_1 = "test-repo-1:abc123"', 'test-repo-1'),
    ('test_repo_1 = "123.foo.com/test:v1.2"', None),
    ('test_repo_1 = "https://foo.com"', None),
    ('bucket_arn  = "arn:aws:s3:::foo-800000001"', None),
    ('snapshot    = "arn:aws:rds:us-east-2:12345:cluster-202301062012000004"', None),
    ('name_suffix : "read_only"', None),
    ('LOCATIONS   = "classpath:flyway/migrations,classpath:flyway/foo/bar"', None),
    ('  JAVA_OPTS = "--add-opens -javaagent:/opt/foo/foo.jar"', None),
])
def test_parse_repo_name(test_input: str, expected: str) -> None:
    """Validate the _parse_repo_name method is successful."""
    assert DiffParser._parse_repo_name(test_input) == expected


@pytest.mark.parametrize('test_input,expected', [
    ('test_repo_1 = "123.foo.com/bar/test-repo-1:abc123"', 'abc123'),
    ('test_repo_1 = "123.foo.com/test-repo-1:abc123"', 'abc123'),
    ('test_repo_1 = "test-repo-1:abc123"', 'abc123'),
    ('test_repo_1 = "123.foo.com/test:v1.2"', None),
    ('test_repo_1 = "https://foo.com"', None),
    ('bucket_arn  = "arn:aws:s3:::foo-800000001"', None),
    ('snapshot    = "arn:aws:rds:us-east-2:12345:cluster-202301062012000004"', None),
    ('name_suffix : "read_only"', None),
    ('LOCATIONS   = "classpath:flyway/migrations,classpath:flyway/foo/bar"', None),
    ('  JAVA_OPTS = "--add-opens -javaagent:/opt/foo/foo.jar"', None),
])
def test_parse_commit(test_input: str, expected: str) -> None:
    """Validate the _parse_commit method is successful."""
    assert DiffParser._parse_commit(test_input) == expected
