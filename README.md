# update-feedstock-version
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/beckermr/update-feedstock-version/main.svg)](https://results.pre-commit.ci/latest/github/beckermr/update-feedstock-version/main) [![tests](https://github.com/beckermr/update-feedstock-version/actions/workflows/tests.yml/badge.svg)](https://github.com/beckermr/update-feedstock-version/actions/workflows/tests.yml)

GitHub Action to update the version of a feedstock.

## Usage

Add a GitHub Actions workflow file like this one:

```yaml
name: update feedstock version
on:
  workflow_dispatch:
    inputs:
      version:
        description: 'the new version'
        required: true
        type: string

jobs:
  update-feedstock-version:
    runs-on: ubuntu-latest
    name: update-feedstock-version
    steps:
      - name: run
        uses: beckermr/update-feedstock-version@main
        with:
          feedstock: <name of feedstock>-feedstock
          version: ${{ inputs.version }}
          github-token: ${{ secrets.GITHUB_PAT }}
          automerge: true
```

Then you can trigger the version update by dispatching the workflow in the UI. It is also possible to trigger the workflow on GitHub release events.

See the [action.yml](action.yml) for details on possible inputs and options.

## Required Token Permissions and Scopes

### Classic Tokens

For classic tokens, you need read/write permissions for the the `repo` and `workflow` scopes. For classic tokens, you pass the token to the `github-token` input.

### Fine-grained Tokens

For fine-grained tokens, you need to generate two tokens with different scopes and pass them to different inputs. These are detailed in the table below.

| Action Input Parameter  | Allowed Repository         | Scopes (permissions)                             |
| ----------------------- | -------------------------- | ------------------------------------------------ |
| `github-token`          | upstream feedstock         | pull_request (read/write)                        |
| `github-token-for-fork` | your fork of the feedstock | contents (read/write), workflows (read/write)    |
