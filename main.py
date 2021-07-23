"""
To consider:
 - Error scenario -> open issue ? Open PR with conflicts
 - Branch deletion of the duplicated target branch
"""
import argparse
import json
import os
import subprocess
from pathlib import Path

import typing
import requests

repo_path = Path("../cherry-pick-tests")


def git(*args):
    command_run = subprocess.run(["git", *args], stdout=subprocess.PIPE, check=True)
    if command_run.stdout is not None:
        return command_run.stdout.decode()


def get_commits_in_branch(
    merge_commit_sha: str, target_branch: typing.Optional[str]
) -> typing.List[str]:
    if not target_branch:
        target_branch = "."  # that way compare `base_branch` to current branch.
    list_commits_as_str = git(
        "cherry", merge_commit_sha + "~1", f"origin/{target_branch}"
    )

    # return multiple line `[+/-] hash`. If "+" needs cherry-pick, else has an equivalent already.
    lines = list_commits_as_str.split("\n")
    commit_split: typing.List[typing.List[str, str]] = [
        line_commit.split() for line_commit in lines if line_commit != ""
    ]
    commit_hashes = [line[1] for line in commit_split if line[0] == "+"]

    return commit_hashes


def backport_commits(commits: typing.List[str], initial_name: str, to_branch: str):
    """
    Backport a list of commit on a *new* branch starting from to_branch.
    """
    new_branch = f"backport-{initial_name}-{to_branch}"
    git("switch", "-c", new_branch, "origin/" + to_branch)
    print(f"Switched to future branch: {new_branch}.")
    try:
        for commit_hash in commits[::-1]:  # status returns newer first.
            git("cherry-pick", commit_hash)
    except:
        print("An error occurred while cherry-picking.")
    git("push", "-u", "origin", new_branch)


def _get_merge_commit_sha(event_dict: typing.Dict) -> str:
    try:
        return event_dict["pull_request"]["merge_commit_sha"]
    except:
        raise RuntimeError(
            "pull_request.merge_commit_sha not found in GITHUB_EVENT_PATH"
        )


def _get_base_branch(event_dict: typing.Dict) -> str:
    try:
        return event_dict["pull_request"]["base"]["ref"]
    except:
        raise RuntimeError("pull_request.base.ref not found in GITHUB_EVENT_PATH")


def _get_target_branch(event_dict: typing.Dict) -> str:
    try:
        return event_dict["pull_request"]["head"]["ref"]
    except:
        raise RuntimeError("pull_request.head.ref not found in GITHUB_EVENT_PATH")


def entrypoint(event_dict, pr_branch, gh_token):
    merge_sha = _get_merge_commit_sha(event_dict)
    base_branch = _get_base_branch(event_dict)
    target_branch = _get_target_branch(event_dict)
    git("checkout", base_branch)
    commits_to_backport = get_commits_in_branch(
        merge_commit_sha=merge_sha, target_branch=target_branch
    )
    print(f"found {len(commits_to_backport)} commits to backport.")
    backport_commits(commits_to_backport, merge_sha, pr_branch)


def git_setup(github_token):
    repo = os.getenv("GITHUB_REPOSITORY")
    actor = os.getenv("GITHUB_ACTOR")
    git(
        "remote",
        "set-url",
        "--push",
        "origin",
        f"https://{actor}:{github_token}@github.com/{repo}.git",
    )
    git("config", "user.email", "action@github.com")
    git("config", "user.name", "github action")


def get_commits_to_backport(gh_token, commits_url):

    headers = {
        "authorization": f"Bearer { gh_token }",
        "content-type": f"application/json",
        "accept": "application/vnd.github.v3+json",
    }
    req = requests.get(url=commits_url, headers=headers)
    json = req.json()
    commits = []
    for entry in json:
        sha = entry.get("sha", "")
        print(sha, entry)
        commits.append(sha)
    return commits


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="automated backport GH action.")
    parser.add_argument("pr_branch", type=str)
    parser.add_argument("github_token", type=str)
    github_event_path = os.getenv("GITHUB_EVENT_PATH")
    with open(github_event_path, "r") as f:
        github_event = json.load(f)

    args = parser.parse_args()
    git_setup(args.github_token)

    entrypoint(
        event_dict=github_event,
        pr_branch=args.pr_branch,
        gh_token=args.github_token,
    )
