"""Provide tests for diff_parser."""
import pytest

from diff_parser.diff_parser import DiffParser


def test_get_repo_commit_changes() -> None:
    """Validate the get_repo_commit_changes method is successful."""
    changes = DiffParser.get_repo_commit_changes(
        unified_diff=[
            '--- \n',
            '+++ \n',
            '@@ -1,2 +1,2 @@\n',
            '-test_repo_1 = "123.foo.com/test-repo-1:abc123"',
            '+test_repo_1 = "123.foo.com/test-repo-1:abc456"',
            '-test_repo_2 = "123.foo.com/bar/test-repo-2:def123"',
            '+test_repo_2 = "123.foo.com/bar/test-repo-2:def456"'
            '-foo         = "bar1"',
            '+foo         = "bar2"'
        ]
    )
    assert changes == {
        'test-repo-1': 'abc456',
        'test-repo-2': 'def456'
    }


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
