#!/bin/bash
# Setup weekly cron job for Theta-Lab dashboard email.
# Runs every Monday at 7:00 AM.
# Prerequisite: set GMAIL_ADDRESS and GMAIL_APP_PASSWORD in .env first.

SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PYTHON=$(which python3)
RUNNER="$SCRIPT_DIR/mcp/routines/weekly_dashboard.py"
LOG="$SCRIPT_DIR/logs/cron.log"

# Ensure cron service is running (WSL requires manual start)
if ! pgrep -x cron > /dev/null 2>&1; then
    echo "Starting cron service..."
    sudo service cron start
fi

# Build cron entry: Monday 7:00 AM
CRON_ENTRY="0 7 * * 1 cd $SCRIPT_DIR && $PYTHON $RUNNER >> $LOG 2>&1"

# Check if already installed
EXISTING=$(crontab -l 2>/dev/null | grep "weekly_dashboard.py")
if [ -n "$EXISTING" ]; then
    echo "Cron job already installed:"
    echo "  $EXISTING"
    echo "To update, run: crontab -e"
    exit 0
fi

# Install
(crontab -l 2>/dev/null; echo "$CRON_ENTRY") | crontab -
echo "Cron job installed: $CRON_ENTRY"
echo ""
echo "To verify: crontab -l"
echo "To remove:  crontab -e  (delete the line)"
echo ""
echo "WSL note: cron does not auto-start. Add this to your WSL startup:"
echo "  sudo service cron start"
echo "Or run manually any time: python3 $RUNNER"
