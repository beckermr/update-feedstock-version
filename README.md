# update-feedstock-version

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
          # A GitHub personal access token is required
          github-token: ${{ secrets.GITHUB_PAT }}
          automerge: true
```

Then you can trigger the version update by dispatching the workflow in the UI. It is also possible to trigger the workflow on GitHub release events.

See the [action.yml](action.yml) for details on possible inputs and options.
