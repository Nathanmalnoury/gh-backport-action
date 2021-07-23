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

## What does it do ? 

It should be used on PR closing successfully (= merged). In that case, it compares the base branch before this commit to the pr head branch in order to retrieve commits that were added during that merge.
It then creates a new branch starting from `pr_branch` and try to cherry-pick each commit found earlier.

Todo:
- Test action in case of a 1) squash and merge 2) rebase and merge
- Successful cherry pick should lead to a new PR
- Head branch being deleted should lead to an issue.
- Unsuccessful retrieving of commits to cherry pick should lead to opening an issue
- Unsuccessful cherry-pick of these commits should also lead to opening an issue.
