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

## Setup

Requires Python 3 (standard library only) and a Jira personal access token.

### 1. Generate a Jira token

1. In Jira, click your avatar (top right) → **Profile**.
2. Open **Personal Access Tokens** → **Create token**.
3. Give it a name (e.g. `sprint-subtasks`), optionally set an expiry, and click **Create**.
4. Copy the token right away. Jira only shows it once.

Never commit the token or paste it into chats or tickets. If it leaks, revoke it from the same page and create a new one.

### 2. Save it in `~/.zshrc`

Run this, paste the token when prompted, and press Enter. The token isn't shown on screen or saved to shell history:

```bash
read -s "t?Jira token: " && echo "export JIRA_TOKEN=$t" >> ~/.zshrc && unset t && echo saved
```

Load it into the current terminal (new terminals pick it up automatically):

```bash
source ~/.zshrc
```

To replace the token later, delete the old `export JIRA_TOKEN=...` line from `~/.zshrc` and run the command again.

## Usage

```bash
python3 create_sprint_subtasks.py --dry-run    # preview
python3 create_sprint_subtasks.py              # create subtasks in the active sprint
python3 create_sprint_subtasks.py --sprint ID  # target a specific sprint
```

Board, project and field IDs are constants at the top of the script.
