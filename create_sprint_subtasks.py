#!/usr/bin/env python3
"""Create default subtasks for tickets in the active sprint that have none.

Rules (per parent ticket with no subtasks):
  - Not a spike: [BE] in title -> "[BE] Implementation", [FE] -> "[FE] Implementation"
  - Spike:       [BE] in title -> "[BE] Investigation",  [FE] -> "[FE] Investigation"
  - QA Estimate set           -> "[QA] Execute testing"

Usage:
  export JIRA_TOKEN=<personal access token>   # Jira profile > Personal Access Tokens
  python3 create_sprint_subtasks.py --dry-run  # preview only
  python3 create_sprint_subtasks.py            # create subtasks
  python3 create_sprint_subtasks.py --sprint 6290  # target a specific sprint id
"""
import argparse
import json
import os
import sys
import urllib.parse
import urllib.error
import urllib.request

JIRA = "https://jira.ninjavan.net"
BOARD_ID = 220
PROJECT_KEY = "XXB"
SUBTASK_TYPE_ID = "5"
QA_ESTIMATE_FIELD = "customfield_12005"


def api(method, path, body=None):
    req = urllib.request.Request(
        JIRA + path,
        method=method,
        data=json.dumps(body).encode() if body is not None else None,
        headers={
            "Authorization": "Bearer " + os.environ["JIRA_TOKEN"],
            "Accept": "application/json",
            "Content-Type": "application/json",
            # Cloudflare blocks the default Python-urllib user agent (error 1010)
            "User-Agent": "create-sprint-subtasks/1.0",
        },
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as e:
        sys.exit(f"{method} {path} failed: HTTP {e.code}\n{e.read().decode(errors='replace')[:500]}")


def active_sprint():
    sprints = api("GET", f"/rest/agile/1.0/board/{BOARD_ID}/sprint?state=active")["values"]
    sprints = [s for s in sprints if s.get("originBoardId") == BOARD_ID] or sprints
    if not sprints:
        sys.exit("No active sprint found on board %d" % BOARD_ID)
    return sprints[0]


def subtasks_for(fields):
    title = fields["summary"]
    spike = "spike" in fields["issuetype"]["name"].lower()
    suffix = "Investigation" if spike else "Implementation"
    subs = [f"{tag} {suffix}" for tag in ("[BE]", "[FE]") if tag in title]
    if fields.get(QA_ESTIMATE_FIELD) is not None:
        subs.append("[QA] Execute testing")
    return subs


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="show what would be created")
    parser.add_argument("--sprint", type=int, help="sprint id (default: active sprint)")
    args = parser.parse_args()

    if "JIRA_TOKEN" not in os.environ:
        sys.exit("Set JIRA_TOKEN to a Jira personal access token")

    sprint_id = args.sprint or active_sprint()["id"]
    jql = f"sprint = {sprint_id} AND issuetype not in subTaskIssueTypes() ORDER BY key"
    query = urllib.parse.urlencode({
        "jql": jql,
        "maxResults": 500,
        "fields": f"summary,issuetype,subtasks,{QA_ESTIMATE_FIELD}",
    })
    issues = api("GET", "/rest/api/2/search?" + query)["issues"]
    print(f"Sprint {sprint_id}: {len(issues)} tickets")

    for issue in issues:
        fields = issue["fields"]
        if fields["subtasks"]:
            continue
        subs = subtasks_for(fields)
        if not subs:
            print(f"  {issue['key']}: no rule matched ({fields['summary']})")
        for summary in subs:
            if args.dry_run:
                print(f"  {issue['key']} -> {summary} (dry run)")
                continue
            created = api("POST", "/rest/api/2/issue", {"fields": {
                "project": {"key": PROJECT_KEY},
                "parent": {"key": issue["key"]},
                "issuetype": {"id": SUBTASK_TYPE_ID},
                "summary": summary,
            }})
            print(f"  {issue['key']} -> {summary}: {created['key']}")


if __name__ == "__main__":
    main()
