#!/bin/bash
# Wrapper script to run tactical change detection and display results

cd "$(dirname "$0")/.." || exit 1

echo "🔍 Running Tactical Change Detection..."
echo ""

python3 scripts/generate_tactical_change_report.py

# Get today's date for log file reference
TODAY=$(date +%Y-%m-%d)

echo ""
echo "📋 Report saved to:"
echo "  • logs/tactical_change_report_${TODAY}.txt"
echo "  • logs/tactical_changes_metadata_${TODAY}.json"
echo ""

# Check if report was generated and display it
if [ -f "logs/tactical_change_report_${TODAY}.txt" ]; then
    echo "---"
    echo "📄 Report Content:"
    echo "---"
    cat "logs/tactical_change_report_${TODAY}.txt"
fi
