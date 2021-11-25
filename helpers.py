import os
import subprocess
import typing
from subprocess import CalledProcessError

import requests


class GitException(Exception):
    """Exception raised when using git command line from python."""

    pass


def git(*args):
    try:
        command_run = subprocess.run(["git", *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        if command_run.stdout is not None:
            return command_run.stdout.decode()
    except CalledProcessError as e:
        output = e.stderr
        try:
            output = output.decode()
        except:
            pass
        raise GitException(output)


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


def _get_pr_number(event_dict: typing.Dict) -> int:
    try:
        return event_dict["pull_request"]["number"]
    except:
        raise RuntimeError("pull_request.number not found in GITHUB_EVENT_PATH")


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


def github_api_headers(gh_token):
    return {
        "authorization": f"Bearer {gh_token}",
        "content-type": f"application/json",
        "accept": "application/vnd.github.v3+json",
    }


def _github_repo_url():
    repo = os.getenv("GITHUB_REPOSITORY")
    api_url = os.getenv("GITHUB_API_URL")
    return f"{api_url}/repos/{repo}"


def github_open_pull_request(title: str, body: str, head: str, base: str, gh_token: str) -> int:
    headers = github_api_headers(gh_token=gh_token)
    body = {
        "head": head,
        "base": base,
        "title": title,
        "body": body,
    }

    response = requests.post(url=f"{_github_repo_url()}/pulls", json=body, headers=headers)
    response.raise_for_status()
    return response.json()["number"]


def github_open_issue(title: str, body: str, gh_token: str):
    headers = github_api_headers(gh_token=gh_token)
    body = {
        "title": title,
        "body": body,
    }

    response = requests.post(url=f"{_github_repo_url()}/issues", json=body, headers=headers)
    response.raise_for_status()
    
def github_add_label_to_pr(pr_number: int, label: str, gh_token: str):
    headers = github_api_headers(gh_token=gh_token)
    body = {
        "labels": [label]
    }
    
    response = requests.patch(url=f"{_github_repo_url()}/issues/{pr_number}", json=body, headers=headers)
    response.raise_for_status()

def github_get_commits_in_pr(pr_number: int, gh_token: str) -> typing.Any:
    headers = github_api_headers(gh_token=gh_token)

    response = requests.get(url=f"{_github_repo_url()}/pulls/{pr_number}/commits", headers=headers)
    response.raise_for_status()
    commits = []
    for commit in response.json():
        commits.append(commit["sha"])
    return commits
