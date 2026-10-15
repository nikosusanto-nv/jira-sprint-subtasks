#!/bin/zsh
# Install a macOS launchd job that runs the script every Wednesday at 17:00 and 18:00.
# With --only-new-sprint it only acts on the Wednesday the new sprint starts; other runs skip.
# Usage: ./install-schedule.sh            (install / update)
#        ./install-schedule.sh uninstall  (remove)
set -e

LABEL="com.$(whoami).jira-sprint-subtasks"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
LOG="$HOME/Library/Logs/jira-sprint-subtasks.log"
SCRIPT="${0:A:h}/create_sprint_subtasks.py"
PYTHON="$(python3 -c 'import sys; print(sys.executable)')"

launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true

if [[ "$1" == "uninstall" ]]; then
  rm -f "$PLIST"
  echo "Removed $LABEL"
  exit 0
fi

mkdir -p "$HOME/Library/LaunchAgents"
cat > "$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>$LABEL</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/zsh</string>
    <string>-c</string>
    <string>source ~/.zshrc >/dev/null 2>&amp;1; exec "$PYTHON" "$SCRIPT" --only-new-sprint</string>
  </array>
  <key>StartCalendarInterval</key>
  <array>
    <dict><key>Weekday</key><integer>3</integer><key>Hour</key><integer>17</integer><key>Minute</key><integer>0</integer></dict>
    <dict><key>Weekday</key><integer>3</integer><key>Hour</key><integer>18</integer><key>Minute</key><integer>0</integer></dict>
  </array>
  <key>StandardOutPath</key><string>$LOG</string>
  <key>StandardErrorPath</key><string>$LOG</string>
</dict>
</plist>
EOF

launchctl bootstrap "gui/$(id -u)" "$PLIST"
echo "Installed $LABEL: Wednesdays 17:00 and 18:00 (log: $LOG)"
