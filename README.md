# LinkedIn Automation

Automatisierte LinkedIn-Content-Pipeline: Von der Idee zum fertigen Post mit Bild.

## Konzept

```
Telegram-Nachricht (Idee) 
    → Bot empfängt & speichert in DB
    → KI generiert LinkedIn-Post im persönlichen Stil
    → KI erstellt passendes Bild/Design
    → Bot sendet fertigen Post + Bild zurück via Telegram
```

## Quick Start

```bash
# 1. Repository klonen
git clone https://github.com/lorenzk99/linkedin.git
cd linkedin

# 2. Abhängigkeiten installieren
pip install -r requirements.txt

# 3. Umgebungsvariablen konfigurieren
cp .env.example .env
# .env mit eigenen API-Keys befuellen

# 4. Datenbank initialisieren
python -m app.db.init

# 5. Bot starten
python -m app.main
```

## Projektstruktur

```
linkedin/
├── app/
│   ├── main.py                 # Einstiegspunkt, Bot-Start
│   ├── config.py               # Konfiguration & Env-Variablen
│   ├── bot/
│   │   ├── handlers.py         # Telegram-Message-Handler
│   │   └── commands.py         # Bot-Kommandos (/start, /post, /list, /style)
│   ├── db/
│   │   ├── models.py           # Datenbank-Modelle (Ideas, Posts, StyleProfiles)
│   │   ├── init.py             # DB-Initialisierung
│   │   └── repository.py       # CRUD-Operationen
│   ├── ai/
│   │   ├── post_generator.py   # LinkedIn-Post-Generierung via Claude API
│   │   ├── style_analyzer.py   # Stil-Analyse bestehender Posts
│   │   └── prompts.py          # Prompt-Templates
│   ├── images/
│   │   ├── generator.py        # Bild-Generierung (DALL-E / Canva)
│   │   └── templates.py        # Bild-Vorlagen & Branding
│   └── utils/
│       ├── linkedin_scraper.py # Bestehende Posts einlesen
│       └── formatters.py       # Text-Formatierung
├── data/
│   ├── style_profiles/         # Gespeicherte Stil-Profile
│   └── sample_posts/           # Beispiel-Posts fuer Stil-Training
├── tests/
├── .env.example
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## Tech Stack

| Komponente | Technologie | Warum |
|---|---|---|
| Bot Framework | python-telegram-bot v21+ | Stabil, async, gut dokumentiert |
| Datenbank | PostgreSQL + SQLAlchemy | Skalierbar, JSON-Support fuer flexible Daten |
| Post-Generierung | Claude API (Anthropic) | Bester Output fuer nuancierte, stilgetreue Texte |
| Bild-Generierung | DALL-E 3 + Canva API | DALL-E fuer kreative Bilder, Canva fuer gebrandete Designs |
| Deployment | Docker + Railway/Render | Einfaches Hosting, guenstig fuer Bots |

## Themen-Cluster

### Cluster 1: Stellenschaltung & Kanal-Strategie
- Kanal-Matching nach Zielgruppe
- Anzeigentexte die konvertieren
- Timing & Budget-Verteilung
- Social Recruiting vs. klassische Jobboersen

### Cluster 2: KI im Recruiting (praktisch)
- Realistische Anwendungsfaelle vs. Marketing-Versprechen
- Wo Automatisierung wirklich Zeit spart
- Bias & Fairness bei KI im Recruiting

### Cluster 3: Skills-based Hiring (allgemein)
- Warum Kompetenzen wichtiger sind als Abschluesse
- Wie man Skills richtig bewertet
- Praxisbeispiele aus dem Markt

### Cluster 4: Founder Einblicke
- NextStepHR aufbauen - ehrliche Learnings
- Rueckschlaege & harte Entscheidungen
- Team-Aufbau & Kultur

## Lizenz

Privat - Alle Rechte vorbehalten.
