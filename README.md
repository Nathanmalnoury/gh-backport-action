# gh-backport-action: GitHub action to backport a pull request.

Main features:
- Based on cherry-pick-ing on the branch needing the backport.
- Supports "Merge Commit", "Rebase and Merge" and "Squash and Merge" options.
- Opens a new PR if success, opens a new Issue if failure.

:warning: For this action to work, "Automatically delete head branches" must be disabled.


## Usage:
### Simple usage:
At each PR merged into master, opens a new Pull Request targeting `develop`.

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
        pr_branch: 'develop'
        github_token: ${{ secrets.GITHUB_TOKEN }}
```

### Using a label to indicate which PR should be backported:
Each Pull Request labeled `backport develop`, when merged, will be backported on `develop`.

```yaml
name: PR for release branch
on:
  pull_request:
    branches: [ master ]
    types: [ closed ]
jobs:
  release_pull_request:
    if: github.event.pull_request.merged == true && contains(github.event.pull_request.labels.*.name, 'backport develop')
    runs-on: ubuntu-latest
    name: release_pull_request
    steps:
    - name: checkout
      uses: actions/checkout@v1
    - name: Backport PR by cherry-pick-ing
      uses: Nathanmalnoury/gh-backport-action@master
      with:
        pr_branch: 'develop'
        github_token: ${{ secrets.GITHUB_TOKEN }}
```

## Backport procedure:

When action is triggerred, it first gets the list of commit hashes to backport using GitHub pulls API
([#list-commits-on-a-pull-request](https://docs.github.com/en/rest/reference/pulls#list-commits-on-a-pull-request)). This is how all 3 merging options
are supported, it also means that even in case of a `squash and merge` the full list of commits will be cherry-picked.

Using `git switch`, it then creates a new branch starting on `pr_branch` and then cherry-pick every commit retrieved.

If the backport procedure was successful, a new PR is open. Otherwise an issue is submitted, with helpful infos (traceback + pr number/target_branch) if github API is reachable.
