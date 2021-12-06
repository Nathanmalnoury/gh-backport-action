import argparse
import json
import os
import typing
import traceback
from datetime import datetime

from helpers import (
    _get_base_branch,
    _get_target_branch,
    _get_pr_number,
    git,
    github_get_commits_in_pr,
    github_open_pull_request,
    git_setup,
    github_open_issue,
)


def backport_commits(commits: typing.List[str], initial_name: str, to_branch: str):
    """
    Backport a list of commit on a *new* branch starting from to_branch.
    """

    new_branch = f"backport-{initial_name[:15]}-{datetime.utcnow().strftime('%m%d%y')}-{to_branch}"
    git("switch", "-c", new_branch, "origin/" + to_branch)
    print(f"Switched to future branch: {new_branch}.")
    try:
        for commit_hash in commits:
            git("cherry-pick", commit_hash)
    except Exception:
        print("An error occurred while cherry-picking.")
        raise RuntimeError("Could not cherry pick at least one commit automatically.")

    git("push", "-u", "origin", new_branch)
    return new_branch


def entrypoint(event_dict, pr_branch, pr_title, pr_body, gh_token):
    base_branch = _get_base_branch(event_dict)
    pr_number = _get_pr_number(event_dict)

    commits_to_backport = github_get_commits_in_pr(pr_number=pr_number, gh_token=gh_token)

    print(f"found {len(commits_to_backport)} commits to backport.")
    template_vars = {"pr_branch": pr_branch, "pr_number": pr_number, "base_branch": base_branch}

    new_branch = backport_commits(commits_to_backport, base_branch, pr_branch)
    github_open_pull_request(
        title=pr_title.format(**template_vars),
        head=new_branch,
        base=pr_branch,
        body=pr_body.format(**template_vars),
        gh_token=gh_token,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="automated backport GH action.")
    parser.add_argument("pr_branch", type=str)
    parser.add_argument("pr_title", type=str)
    parser.add_argument("pr_body", type=str)
    parser.add_argument("github_token", type=str)
    github_event_path = os.getenv("GITHUB_EVENT_PATH")

    with open(github_event_path, "r") as f:
        github_event = json.load(f)

    args = parser.parse_args()
    git_setup(args.github_token)
    try:
        entrypoint(
            event_dict=github_event,
            pr_branch=args.pr_branch,
            pr_title=args.pr_title,
            pr_body=args.pr_body,
            gh_token=args.github_token,
        )
    except Exception:
        main_traceback = traceback.format_exc()
        traceback_formatted_for_body = f"\n```python\n{main_traceback}```"
        try:
            pr_num = _get_pr_number(event_dict=github_event)
            title = f"Could not automatically backport #{pr_num}"
            body = f"Exception occurred when trying to cherry-pick PR #{pr_num}.\nPlease cherry-pick it manually."
            body += traceback_formatted_for_body
            github_open_issue(title, body, gh_token=args.github_token)
            exit(1)
        except Exception:  # could not get pr number ; fallback on next try/except
            pass
        try:
            tar_branch = _get_target_branch(event_dict=github_event)
            title = f"Could not automatically backport branch {tar_branch}"
            body = f"Exception occurred when trying to cherry-pick PR commits of `{tar_branch}`.\nPlease cherry-pick it manually."
            body += traceback_formatted_for_body

            github_open_issue(title, body, gh_token=args.github_token)
            exit(1)
        except Exception:  # could not get target branch; fallback on next try/except
            pass
        try:
            title = "Automatic Backport failed"
            body = "Exception occurred when trying to backport a branch.\nCheck `actions` tab to see more."
            body += traceback_formatted_for_body
            github_open_issue(title, body, gh_token=args.github_token)
            exit(1)
        except Exception:  # could not create a github issue;
            print("Several Exceptions occurred:")
            print(traceback)
            print("--" * 8)
            print(traceback.format_exc())
            exit(1)
