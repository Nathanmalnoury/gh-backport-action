# gh-backport-action
Github action to backport PR.

## Targetted usage:

```yaml
name: PR for release branch
on:
  pull_request:
    branches: [ master ]
    types: [ closed ]
jobs:
  release_pull_request:
    if: github.event.pull_request.merged == true
    runs-on: ubuntu-latest
    name: release_pull_request
    steps:
    - name: checkout
      uses: actions/checkout@v1
    - name: Create PR to branch
      uses: Nathanmalnoury/gh-backport-action@master
      with:
        pr_branch: 'recette'
        github_token: ${{ secrets.GITHUB_TOKEN }}
```
