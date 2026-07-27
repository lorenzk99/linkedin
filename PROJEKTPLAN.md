# Projektplan: LinkedIn Automation Tool

## Ueberblick

**Ziel:** Ein End-to-End-System, das Ideen per Telegram entgegennimmt, in LinkedIn-Posts im persoenlichen Stil umwandelt, passende Bilder generiert und alles per Telegram zurueckliefert.

**Zeitrahmen:** 4-5 Wochen Entwicklung

---

## Phase 1: Fundament (Woche 1)

### 1.1 Projekt-Setup
- [x] Repository erstellen
- [x] Projektstruktur anlegen
- [ ] Python-Umgebung mit Poetry/pip einrichten
- [ ] Linting & Formatting (ruff, black)
- [ ] Docker-Setup fuer lokale Entwicklung

### 1.2 Telegram Bot Grundgeruest
- [ ] Bot bei @BotFather registrieren
- [ ] Bot-Token sicher in .env speichern
- [ ] Basis-Handler: /start, /help
- [ ] Nachrichten-Empfang (Text + Bilder)
- [ ] Bestaetigungsnachricht bei Ideen-Eingang

### 1.3 Datenbank
- [ ] PostgreSQL via Docker Compose
- [ ] SQLAlchemy Models:
  - `ideas` - Eingehende Ideen mit Timestamp, Status, Cluster-Zuordnung
  - `posts` - Generierte LinkedIn-Posts mit Versionen
  - `style_profiles` - Stil-Merkmale des Nutzers
  - `images` - Generierte Bilder mit Metadaten
- [ ] Alembic fuer Migrationen
- [ ] Basis-CRUD-Operationen

**Deliverable:** Bot empfaengt Nachrichten und speichert sie in der Datenbank.

---

## Phase 2: Stil-Analyse & Post-Generierung (Woche 2)

### 2.1 Bestehende Posts analysieren
- [ ] LinkedIn-Posts sammeln (manuell als JSON/CSV einspeisen)
- [ ] Stil-Analyse-Modul:
  - Tonalitaet (direkt, motivierend, provokant)
  - Textlaenge und Absatz-Struktur
  - Emoji-Nutzung
  - Hook-Patterns (erste Zeile)
  - CTA-Patterns (letzte Zeile)
  - Hashtag-Strategie
- [ ] Stil-Profil als JSON speichern

### 2.2 Post-Generierung
- [ ] Claude API Integration (Anthropic SDK)
- [ ] Prompt-Engineering:
  - System-Prompt mit Stil-Profil
  - Cluster-spezifische Anweisungen
  - Beispiel-Posts als Few-Shot-Referenz
- [ ] Post-Varianten generieren (2-3 Versionen pro Idee)
- [ ] Qualitaetspruefung:
  - Laenge (1200-1800 Zeichen optimal fuer LinkedIn)
  - Hook-Staerke
  - CTA vorhanden
  - Hashtag-Anzahl (3-5)

### 2.3 Themen-Cluster-Engine
- [ ] Automatische Cluster-Erkennung fuer eingehende Ideen
- [ ] Cluster-spezifische Prompt-Anpassung
- [ ] Abwechslung sicherstellen (nicht 2x gleicher Cluster hintereinander)

**Deliverable:** Aus einer Idee werden 2-3 fertige Post-Entwuerfe im richtigen Stil.

---

## Phase 3: Bild-Generierung (Woche 3)

### 3.1 Bild-Stil definieren
- [ ] Bestehende LinkedIn-Bilder analysieren:
  - Farbpalette
  - Typografie
  - Layout-Muster
  - Branding-Elemente
- [ ] Bild-Templates pro Cluster erstellen

### 3.2 KI-Bildgenerierung
- [ ] DALL-E 3 API Integration
- [ ] Prompt-Templates fuer konsistenten Stil:
  - Professionelle Fotos/Szenen
  - Text-Overlay-faehige Bilder
  - Infografik-artige Designs
- [ ] Bild-Nachbearbeitung:
  - Richtige Groesse fuer LinkedIn (1200x627px oder 1080x1080px)
  - Branding-Overlay (Logo, Farben)
  - Text-Integration falls gewuenscht

### 3.3 Canva API Alternative
- [ ] Canva API Integration als Option
- [ ] Brand Kit nutzen fuer konsistente Designs
- [ ] Template-basierte Bild-Erstellung

**Deliverable:** Zu jedem Post wird ein passendes, gebrandetes Bild generiert.

---

## Phase 4: Telegram-Delivery & Workflow (Woche 4)

### 4.1 Rueckkanal via Telegram
- [ ] Post + Bild als fertige Nachricht zuruecksenden
- [ ] Inline-Keyboard fuer Aktionen:
  - "Veroeffentlichen" (direkt oder geplant)
  - "Ueberarbeiten" (mit Feedback)
  - "Neues Bild" (alternatives Bild generieren)
  - "Verwerfen"
- [ ] Bild in hoechster Qualitaet senden (als Dokument, nicht komprimiert)

### 4.2 Workflow-Automatisierung
- [ ] Woechentlicher Content-Reminder (Mo + Do)
- [ ] Automatische Post-Planung:
  - Ideen-Queue priorisieren
  - Cluster-Rotation sicherstellen
  - Beste Posting-Zeiten beruecksichtigen (Di-Do, 8-10 Uhr)
- [ ] Status-Uebersicht: /status zeigt Pipeline

### 4.3 Bot-Kommandos komplett
- [ ] /idee [text] - Neue Idee einsenden
- [ ] /post - Naechsten Post generieren
- [ ] /list - Alle Ideen anzeigen
- [ ] /queue - Post-Warteschlange
- [ ] /style - Stil-Profil anzeigen/anpassen
- [ ] /status - Pipeline-Status
- [ ] /cluster [name] - Themen-Cluster verwalten
- [ ] /plan - Redaktionsplan anzeigen

**Deliverable:** Kompletter Kreislauf: Idee rein, fertiger Post + Bild raus.

---

## Phase 5: Polish & Deployment (Woche 5)

### 5.1 Testing
- [ ] Unit Tests fuer alle Module
- [ ] Integration Tests fuer Bot-Workflow
- [ ] End-to-End Test: Idee → Post → Bild → Telegram

### 5.2 Deployment
- [ ] Docker-Container finalisieren
- [ ] Railway oder Render Deployment
- [ ] Umgebungsvariablen in Produktion setzen
- [ ] Health-Checks & Monitoring
- [ ] Automatischer Neustart bei Absturz

### 5.3 Dokumentation
- [ ] Setup-Anleitung
- [ ] API-Key Beschaffung (Telegram, Anthropic, DALL-E)
- [ ] Troubleshooting Guide

**Deliverable:** Produktionsreifes System, 24/7 erreichbar.

---

## API-Keys & Accounts benoetigt

| Service | Was | Wo beantragen |
|---|---|---|
| Telegram Bot | Bot Token | @BotFather in Telegram |
| Anthropic | Claude API Key | console.anthropic.com |
| OpenAI | DALL-E API Key | platform.openai.com |
| Canva (optional) | API Key | developers.canva.com |

---

## Kosten-Schaetzung (monatlich)

| Posten | Geschaetzt |
|---|---|
| Claude API (50 Posts/Monat) | ~5-10 EUR |
| DALL-E 3 (50 Bilder/Monat) | ~5-10 EUR |
| Hosting (Railway/Render) | ~5-7 EUR |
| PostgreSQL (managed) | 0 EUR (Render free tier) |
| **Gesamt** | **~15-27 EUR/Monat** |

---

## Redaktionsplan (erste 4 Wochen)

### Woche 1
| Tag | Cluster | Format | Thema |
|---|---|---|---|
| Dienstag | Skills-based Hiring | Meinungs-Post | "Der Lebenslauf hat ausgedient - warum Kompetenzen zaehlen" |
| Donnerstag | Stellenschaltung | Praxis-Tipp | "3 Fehler bei der Stellenschaltung, die dich Bewerber kosten" |

### Woche 2
| Tag | Cluster | Format | Thema |
|---|---|---|---|
| Dienstag | KI im Recruiting | Hype vs. Realitaet | "ChatGPT schreibt jetzt Stellenanzeigen - und das ist das Problem" |
| Donnerstag | Founder Einblicke | Story-Post | "Was mir niemand ueber Gruendung gesagt hat" |

### Woche 3
| Tag | Cluster | Format | Thema |
|---|---|---|---|
| Dienstag | Stellenschaltung | Kanal-Guide | "Wo erreichst du Pflegekraefte? Nicht auf StepStone." |
| Donnerstag | KI im Recruiting | Praxis-Post | "So nutze ich KI wirklich im taeglichen Recruiting" |

### Woche 4
| Tag | Cluster | Format | Thema |
|---|---|---|---|
| Dienstag | Skills-based Hiring | How-To | "Kompetenzen bewerten ohne Assessment Center - 3 einfache Methoden" |
| Donnerstag | Founder Einblicke | Ehrlicher Post | "Unser groesster Fehler bei NextStepHR - und was wir daraus gelernt haben" |

**Bonus-Slots:** Event-Posts (Speaker-Auftritte, Awards, Konferenzen) ersetzen bei Bedarf einen geplanten Post.

---

## Naechste Schritte

1. API-Keys besorgen (Telegram Bot, Anthropic, OpenAI)
2. 10-15 bestehende LinkedIn-Posts als Stil-Referenz sammeln
3. 5-10 bestehende LinkedIn-Bilder als Design-Referenz sammeln
4. Phase 1 starten: Bot-Grundgeruest + Datenbank
