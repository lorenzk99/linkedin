#!/bin/bash
set -e

echo ""
echo "======================================"
echo "  LinkedIn Bot - Automatisches Setup"
echo "======================================"
echo ""

# 1. Homebrew
if ! command -v brew &> /dev/null; then
    echo "[1/5] Homebrew wird installiert..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
    eval "$(/opt/homebrew/bin/brew shellenv)"
else
    echo "[1/5] Homebrew ist bereits installiert."
fi

# 2. Python
if ! command -v python3 &> /dev/null; then
    echo "[2/5] Python wird installiert..."
    brew install python
else
    echo "[2/5] Python ist bereits installiert."
fi

# 3. Projekt-Ordner
echo "[3/5] Projekt wird eingerichtet..."
cd ~/Desktop/linkedin 2>/dev/null || true

# 4. .env Datei
if [ ! -f .env ]; then
    echo ""
    echo "--- API-Keys eingeben ---"
    echo "(Einfach einfuegen mit Cmd+V und Enter druecken)"
    echo ""
    read -p "Telegram Bot Token (von @BotFather): " TG_TOKEN
    read -p "Telegram User-ID (von @userinfobot): " TG_USER
    read -p "Anthropic API-Key (sk-ant-...): " ANTHROPIC_KEY
    read -p "OpenAI API-Key (sk-proj-...): " OPENAI_KEY

    cat > .env << ENVEOF
TELEGRAM_BOT_TOKEN=${TG_TOKEN}
TELEGRAM_ALLOWED_USERS=${TG_USER}
ANTHROPIC_API_KEY=${ANTHROPIC_KEY}
OPENAI_API_KEY=${OPENAI_KEY}
DATABASE_URL=sqlite+aiosqlite:///./data/linkedin_automation.db
ENVEOF
    echo ""
    echo ".env Datei erstellt!"
else
    echo "[4/5] .env existiert bereits."
fi

# 5. Abhaengigkeiten & Start
echo "[4/5] Python-Pakete werden installiert..."
pip3 install -q -r requirements.txt

echo "[5/5] Datenbank wird initialisiert..."
python3 -m app.db.init

echo ""
echo "======================================"
echo "  Setup abgeschlossen!"
echo "======================================"
echo ""
echo "Starte den Bot..."
echo "(Zum Beenden: Ctrl+C)"
echo ""
python3 -m app.main
