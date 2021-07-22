# gh-backport-action
Github action to backport PR.

## Targetted usage: 

```yaml
name: PR for release branch
on:
  push:
    branches: [ master ]
jobs:
  release_pull_request:
    runs-on: ubuntu-latest
    name: release_pull_request
    steps:
    - name: checkout
      uses: actions/checkout@v1
    - name: Create PR to branch
      uses: Nathanmalnoury/gh-backport-action@master
      with:
        pr_branch: 'recette'
        
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        
```
