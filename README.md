# action-release-notes-notifier

A GitHub Action which sends notifications to Slack with the release notes of new releases.

[![.github/workflows/test.yml](https://github.com/champ-oss/action-release-notes-notifier/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/champ-oss/action-release-notes-notifier/actions/workflows/test.yml)
[![.github/workflows/release.yml](https://github.com/champ-oss/action-release-notes-notifier/actions/workflows/release.yml/badge.svg)](https://github.com/champ-oss/action-release-notes-notifier/actions/workflows/release.yml)

## Features

- Scans the most recent commit to find lines that contain a repository and commit that have been updated.
- Gathers information for pull requests related to any changed repositories and commits.
- Files to scan can be filtered using a regex pattern.
- Optionally creates a tag in the source repositories.

## Example of Slack notification

```markdown
The Dev environment has been updated

example-repo-1
• *<https://example.com/test_repo_1/123|Pull Request 123>* #123
• *<https://example.com/test_repo_1/124|Pull Request 124>* #124

example-repo-2
• *<https://example.com/test_repo_2/456|Pull Request 456>* #456

example-repo-3
• *<https://example.com/test_repo_3/789|Pull Request 789>* #789
```

## Example Usage

```yaml
name: release-notes-notifier

on:
  workflow_dispatch:
  push:
    branches:
      - main

jobs:
  release-notes-notifier:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: champ-oss/action-release-notes-notifier@main
        with:
          environment: Dev
          file-pattern: .*dev.*.tfvars
          tag-name: dev
          token: ${{ secrets.GITHUB_TOKEN }}
          organization: champ-oss
          slack-webhook: https://example.com/slack-webhook
```

## Parameters

| Parameter     | Required | Description                             |
|---------------|----------|-----------------------------------------|
| environment   | true     | Name of the environment                 |
| file-pattern  | true     | Regex pattern to filter files           |
| organization  | true     | GitHub organization name                |
| slack-webhook | true     | Slack webhook URL to send notifications |
| tag-name      | false    | Tag to add to the source repositories   |
| token         | false    | GitHub Token or PAT                     |

