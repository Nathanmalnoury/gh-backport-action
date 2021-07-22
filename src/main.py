"""
To consider:
 - Error scenario -> open issue ? Open PR with conflicts
 - Branch deletion of the duplicated target branch
"""
import argparse
import os
import random
import subprocess
from pathlib import Path

import typing

repo_path = Path("../cherry-pick-tests")


def git(*args):
    print(["git", *args])
    command_run = subprocess.run(["git", *args], stdout=subprocess.PIPE, check=True)
    if command_run.stdout is not None:
        return command_run.stdout.decode()


def get_commits_in_branch(
    base_branch: str, target_branch: typing.Optional[str]
) -> typing.List[str]:
    if not target_branch:
        target_branch = "."  # that way compare `base_branch` to current branch.
    list_commits_as_str = git(
        "log", f"{base_branch}..{target_branch}", "--pretty=oneline"
    )
    lines_commits = list_commits_as_str.split("\n")
    commit_hashes = [
        line_commit.split()[0] for line_commit in lines_commits if line_commit != ""
    ]
    return commit_hashes


def backport_commits(commits: typing.List[str], to_branch: str):
    """
    Backport a list of commit on a *new* branch starting from to_branch.
    """
    pr_name = random.randint(1, 10000000)
    new_branch = f"backport-{pr_name}-{to_branch}"
    git("switch", "-c", new_branch, to_branch)
    print(commits)
    for commit_hash in commits[::-1]:  # status returns newer first.
        git("cherry-pick", commit_hash)


def entrypoint(target_branch, base_branch, pr_branch):
    commits_to_backport = get_commits_in_branch(base_branch, target_branch)
    backport_commits(commits_to_backport, pr_branch)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="automated backport GH action.")
    parser.add_argument("base_branch", type=str)
    parser.add_argument("target_branch", type=str)
    parser.add_argument("pr_branch", type=str)
    parser.add_argument("github_token", type=str)
    # git("checkout", base_branch)
    # github_token = args.github_token todo: for opening PRs and stuff.
    args = parser.parse_args()
    print(args)
    entrypoint(
        target_branch=args.target_branch,
        base_branch=args.base_branch,
        pr_branch=args.pr_branch,
    )
