#!/bin/bash
echo ""
echo "=== LinkedIn Bot Update ==="
echo ""

cd ~/Desktop/linkedin 2>/dev/null || cd "$(dirname "$0")" || exit 1

echo "Code wird aktualisiert..."
git pull origin claude/linkedin-recruiting-content-lmuaml

echo ""
echo "Bot wird gestartet..."
echo "(Zum Beenden: Ctrl+C)"
echo ""
python3 -m app.main
