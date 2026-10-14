# jira-sprint-subtasks

Creates default subtasks for tickets in the active Jira sprint that don't have any yet.

| Condition | Subtask |
|---|---|
| Title has `[BE]`, not a spike | `[BE] Implementation` |
| Title has `[FE]`, not a spike | `[FE] Implementation` |
| Title has `[BE]`, spike | `[BE] Investigation` |
| Title has `[FE]`, spike | `[FE] Investigation` |
| Title has `[QA]` or QA Estimate is set | `[QA] Execute testing` (once) |

Tickets that already have subtasks are skipped, so it's safe to re-run.

## Usage

Requires Python 3 (standard library only) and a Jira personal access token.

```bash
export JIRA_TOKEN=...                          # never commit this
python3 create_sprint_subtasks.py --dry-run    # preview
python3 create_sprint_subtasks.py              # create subtasks in the active sprint
python3 create_sprint_subtasks.py --sprint ID  # target a specific sprint
```

Board, project and field IDs are constants at the top of the script.
