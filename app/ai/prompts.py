STYLE_ANALYSIS_PROMPT = """Analysiere die folgenden LinkedIn-Posts und erstelle ein detailliertes Stil-Profil.

Posts:
{posts}

Analysiere folgende Aspekte:
1. **Tonalitaet**: Ist der Stil direkt, motivierend, provokant, sachlich, persoenlich?
2. **Textstruktur**: Wie lang sind die Posts? Wie viele Absaetze? Kurze oder lange Saetze?
3. **Hook-Patterns**: Wie beginnen die Posts? Was zieht Aufmerksamkeit?
4. **CTA-Patterns**: Wie enden die Posts? Gibt es Handlungsaufforderungen?
5. **Emoji-Nutzung**: Werden Emojis verwendet? Wie oft? Welche Art?
6. **Hashtag-Strategie**: Wie viele Hashtags? Wo platziert? Welche Themen?
7. **Besondere Stilmittel**: Rhetorische Fragen, Listen, Zitate, persoenliche Anekdoten?

Antworte als JSON mit folgender Struktur:
{{
    "summary": "Zusammenfassung des Stils in 2-3 Saetzen",
    "tone": "hauptsaechliche Tonalitaet",
    "avg_length": geschaetzte durchschnittliche Zeichenzahl,
    "emoji_usage": "none|minimal|moderate|heavy",
    "hook_patterns": ["Pattern 1", "Pattern 2", ...],
    "cta_patterns": ["Pattern 1", "Pattern 2", ...],
    "hashtag_strategy": {{
        "avg_count": Zahl,
        "placement": "end|inline|mixed",
        "common_tags": ["tag1", "tag2", ...]
    }},
    "style_notes": ["Besonderheit 1", "Besonderheit 2", ...]
}}"""

POST_GENERATION_PROMPT = """Du bist ein LinkedIn-Ghostwriter fuer einen HR-Tech-Gruender und Recruiting-Experten.

**Stil-Profil:**
{style_profile}

**Themen-Cluster:** {cluster}

**Idee/Input:**
{idea}

**Beispiel-Posts im gleichen Stil:**
{example_posts}

Schreibe einen LinkedIn-Post basierend auf der Idee. Beachte:
- Schreibe EXAKT im Stil des Profils (Tonalitaet, Laenge, Struktur)
- Starte mit einem starken Hook (erste Zeile entscheidet ueber Klicks auf "mehr anzeigen")
- Optimale Laenge: 1200-1800 Zeichen
- Ende mit einer klaren Handlungsaufforderung oder Frage
- 3-5 relevante Hashtags am Ende
- Der Post soll authentisch und persoenlich klingen, nicht wie Marketing
- Zielgruppe: Recruiter, HR-Verantwortliche, Geschaeftsfuehrer im DACH-Raum

Antworte NUR mit dem fertigen Post-Text, keine Erklaerungen drumherum."""

IMAGE_PROMPT_TEMPLATE = """Erstelle ein professionelles LinkedIn-Post-Bild zum Thema: {topic}

Stil-Vorgaben:
- Modern, clean, professionell
- Passend fuer HR/Recruiting/Tech-Branche
- Farbpalette: {colors}
- Format: {width}x{height}px
- Kein Text im Bild (Text wird separat hinzugefuegt)
- Fotorealistisch oder moderne Illustration
- Business-Kontext, aber nicht langweilig

Das Bild soll als Eye-Catcher im LinkedIn-Feed funktionieren."""

CLUSTER_DETECTION_PROMPT = """Ordne die folgende Idee einem dieser Themen-Cluster zu:

Cluster:
1. Stellenschaltung & Kanal-Strategie
2. KI im Recruiting
3. Skills-based Hiring
4. Founder Einblicke

Idee: {idea}

Antworte NUR mit dem Cluster-Namen, nichts anderes."""
