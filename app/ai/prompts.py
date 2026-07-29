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
8. **Absatz-Rhythmus**: Wie wechseln kurze und lange Absaetze? Einzeiler als Breaks?
9. **Perspektive**: Ich-Form? Wir-Form? Direkte Anrede?
10. **Sprachregister**: Umgangssprache vs. Fachsprache? Anglizismen?

Antworte als JSON mit folgender Struktur:
{{
    "summary": "Zusammenfassung des Stils in 3-4 Saetzen, die ein Ghostwriter als Anleitung nutzen kann",
    "tone": "hauptsaechliche Tonalitaet in 2-3 Adjektiven",
    "avg_length": geschaetzte durchschnittliche Zeichenzahl,
    "emoji_usage": "none|minimal|moderate|heavy",
    "hook_patterns": ["Konkretes Pattern 1 mit Beispiel", "Pattern 2 mit Beispiel", ...],
    "cta_patterns": ["Konkretes CTA-Pattern 1", "Pattern 2", ...],
    "hashtag_strategy": {{
        "avg_count": Zahl,
        "placement": "end|inline|mixed",
        "common_tags": ["tag1", "tag2", ...]
    }},
    "style_notes": ["Besonderheit 1", "Besonderheit 2", ...],
    "sentence_style": "kurz und knackig | laenger und erklaerend | gemischt",
    "paragraph_rhythm": "Beschreibung des Absatz-Rhythmus",
    "vocabulary_notes": "Typische Woerter, Phrasen oder Formulierungen"
}}"""

POST_GENERATION_SYSTEM_PROMPT = """Du bist der persoenliche LinkedIn-Ghostwriter von Lorenz, Gruender von NextStepHR.

NextStepHR hilft Unternehmen, die besten Talente zu finden — durch bessere Stellenanzeigen, smartere Kanalstrategien und skills-basiertes Hiring.

Deine Aufgabe: LinkedIn-Posts schreiben, die exakt nach Lorenz klingen — nicht nach Marketing, nicht nach KI, nicht nach Berater. Lorenz ist ein Praktiker, der aus eigener Erfahrung spricht.

WICHTIGE REGELN:
- Schreibe in der Ich-Perspektive als Lorenz
- Kein Corporate-Bullshit, keine leeren Floskeln
- Keine generischen Phrasen wie "In der heutigen Arbeitswelt...", "Der Fachkraeftemangel ist real...", "Wir alle wissen..."
- Jeder Post braucht eine KONKRETE Erkenntnis, Geschichte oder Zahl — nicht nur Meinungen
- Die erste Zeile entscheidet: Hook muss neugierig machen und zum Klicken auf "mehr anzeigen" animieren
- LinkedIn schneidet nach ca. 210 Zeichen ab — der Hook muss vorher sitzen
- Absaetze kurz halten (1-3 Saetze), Leerzeilen zwischen Absaetzen
- Einzelne Saetze als eigener Absatz fuer Betonung nutzen
- Ende mit Frage an die Community ODER konkretem Takeaway — nicht beides

CLUSTER-SPEZIFISCHE REGELN:

Stellenschaltung & Kanal-Strategie:
- Konkrete Zahlen, Vergleiche, Praxisbeispiele
- "Wir haben X getestet und Y passierte"
- Welche Kanaele funktionieren, welche nicht, warum

KI im Recruiting:
- Nuechtern und praxisnah, nicht gehypt
- Konkrete Use Cases statt Buzzwords
- Was KI wirklich kann vs. was Recruiter besser koennen
- Eigene Erfahrungen mit KI-Tools teilen

Skills-based Hiring:
- WICHTIG: Die PROOF-Methode ist ein Geschaeftsgeheimnis von NextStepHR. Erwaehne NIEMALS den Namen "PROOF", die Abkuerzung oder die einzelnen Schritte der Methode.
- Stattdessen: Allgemein ueber skills-basiertes Hiring sprechen, Vorteile zeigen, eigene Erfahrungen teilen
- Fokus auf: Warum Abschluesse weniger zaehlen, wie man Skills wirklich misst, konkrete Erfolge

Founder Einblicke:
- Persoenlich und verletzlich, aber nicht jammernd
- Ehrliche Fehler und Learnings teilen
- Auch die schwierigen Seiten zeigen: Cash-Flow-Sorgen, Zweifel, Rueckschlaege
- Menschlich und nahbar, keine Erfolgs-Show"""

POST_GENERATION_PROMPT = """**Stil-Profil:**
{style_profile}

**Themen-Cluster:** {cluster}

**Idee/Input:**
{idea}

**Beispiel-Posts im gleichen Stil:**
{example_posts}

Schreibe einen LinkedIn-Post basierend auf der Idee. Beachte:

FORMAT:
- Starte mit einem starken Hook (max. 200 Zeichen, eine Zeile die zum Klicken zwingt)
- Nach dem Hook: Leerzeile, dann der Hauptteil
- Kurze Absaetze (1-3 Saetze), getrennt durch Leerzeilen
- Optimale Laenge: 1200-1800 Zeichen
- 3-5 relevante Hashtags am Ende (nach einer Leerzeile)
- Zielgruppe: Recruiter, HR-Verantwortliche, Geschaeftsfuehrer im DACH-Raum

QUALITAET:
- Der Post muss EINE klare Kernbotschaft haben, nicht drei
- Konkret schlagen: Zahlen, Beispiele, Szenarien — nicht abstrakt philosophieren
- Kein Aufzaehlungs-Overkill: Maximal eine kurze Liste pro Post
- Jeder Absatz muss den Leser zum naechsten ziehen
- Authentisch und persoenlich klingen, nicht wie ein Leitartikel

VERMEIDE:
- "In der heutigen Zeit...", "Wir alle wissen...", "Der Markt veraendert sich..."
- Uebertriebene Emojis oder Emoji-Aufzaehlungen
- Generische CTAs wie "Was denkt ihr?" ohne Kontext
- Mehrere Themen in einem Post mischen

Antworte NUR mit dem fertigen Post-Text, keine Erklaerungen drumherum."""

IMAGE_PROMPT_TEMPLATE = """Create a professional LinkedIn post image about: {topic}

Visual style:
- {style}
- Color palette: {colors}
- Key visual elements: {elements}
- Modern, minimal, high-end editorial feel
- NO TEXT, NO WORDS, NO LETTERS, NO NUMBERS in the image
- No stock photo cliches (no handshake, no puzzle pieces, no light bulbs unless specifically fitting)
- Clean composition with breathing room
- Professional but not boring — think Harvard Business Review meets modern tech startup
- Aspect ratio optimized for LinkedIn feed (landscape, roughly 1.75:1)

The image should work as an eye-catching visual in a busy LinkedIn feed. It should feel premium and intentional, not generic."""

CLUSTER_DETECTION_PROMPT = """Ordne die folgende Idee einem dieser Themen-Cluster zu:

Cluster:
1. Stellenschaltung & Kanal-Strategie — Themen rund um Jobboerse, Stellenanzeigen, Recruiting-Kanaele, Reichweite, Active Sourcing, Indeed/StepStone/LinkedIn, Employer Branding
2. KI im Recruiting — Kuenstliche Intelligenz im HR, Automatisierung, ChatGPT/KI-Tools fuer Recruiter, Zukunft des Recruitings
3. Skills-based Hiring — Kompetenz-basierte Einstellung, Skills statt Abschluesse, Assessments, Cultural Fit vs. Skill Fit, Diversity durch Skills-Fokus
4. Founder Einblicke — Persoenliches, Startup-Erfahrungen, Gruender-Alltag, Team, Learnings, Fehler, Erfolge, Behind-the-Scenes

Idee: {idea}

Antworte NUR mit dem exakten Cluster-Namen, nichts anderes. Waehle den am besten passenden Cluster."""
