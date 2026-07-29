import json
from dataclasses import dataclass

import anthropic

from app.config import settings
from app.ai.prompts import (
    POST_GENERATION_SYSTEM_PROMPT,
    POST_GENERATION_PROMPT,
    CLUSTER_DETECTION_PROMPT,
)
from app.ai.style_analyzer import StyleAnalyzer
from app.db.repository import PostRepository, IdeaRepository


@dataclass
class GeneratedPost:
    content: str
    cluster: str
    char_count: int


def _build_style_text(profile) -> str:
    if not profile:
        return (
            "Professionell, direkt, praxisnah. "
            "Kurze Absaetze, klare Sprache, Ich-Perspektive. "
            "Keine Floskeln, konkrete Beispiele bevorzugt."
        )

    parts = []
    if profile.summary:
        parts.append(f"Zusammenfassung: {profile.summary}")
    if profile.tone:
        parts.append(f"Tonalitaet: {profile.tone}")
    if profile.avg_length:
        parts.append(f"Durchschnittliche Laenge: {profile.avg_length} Zeichen")
    if profile.emoji_usage:
        parts.append(f"Emoji-Nutzung: {profile.emoji_usage}")
    if profile.hook_patterns:
        hooks = profile.hook_patterns
        if isinstance(hooks, list):
            parts.append(f"Hook-Muster: {', '.join(hooks[:5])}")
    if profile.cta_patterns:
        ctas = profile.cta_patterns
        if isinstance(ctas, list):
            parts.append(f"CTA-Muster: {', '.join(ctas[:5])}")
    if profile.hashtag_strategy:
        hs = profile.hashtag_strategy
        if isinstance(hs, dict):
            count = hs.get("avg_count", "?")
            placement = hs.get("placement", "?")
            parts.append(f"Hashtags: ~{count} Stueck, Platzierung: {placement}")

    return "\n".join(parts)


class PostGenerator:
    def __init__(self):
        self.client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
        self.style_analyzer = StyleAnalyzer()
        self.post_repo = PostRepository()
        self.idea_repo = IdeaRepository()

    async def detect_cluster(self, idea: str) -> str:
        prompt = CLUSTER_DETECTION_PROMPT.format(idea=idea)
        response = await self.client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=100,
            messages=[{"role": "user", "content": prompt}],
        )
        cluster = response.content[0].text.strip()
        valid_clusters = [
            "Stellenschaltung & Kanal-Strategie",
            "KI im Recruiting",
            "Skills-based Hiring",
            "Founder Einblicke",
        ]
        for vc in valid_clusters:
            if vc.lower() in cluster.lower() or cluster.lower() in vc.lower():
                return vc
        return cluster

    async def generate(self, idea: str, cluster: str | None = None) -> GeneratedPost:
        if not cluster:
            cluster = await self.detect_cluster(idea)

        profile = await self.style_analyzer.get_profile()
        style_text = _build_style_text(profile)

        example_text = ""
        if profile and profile.sample_posts:
            examples = profile.sample_posts[:3]
            example_text = "\n\n---\n\n".join(
                f"Beispiel {i+1}:\n{post}" for i, post in enumerate(examples)
            )

        prompt = POST_GENERATION_PROMPT.format(
            style_profile=style_text,
            cluster=cluster,
            idea=idea,
            example_posts=example_text or "Keine Beispiele verfuegbar.",
        )

        response = await self.client.messages.create(
            model="claude-sonnet-5",
            max_tokens=3000,
            system=POST_GENERATION_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )

        content = response.content[0].text.strip()
        return GeneratedPost(
            content=content,
            cluster=cluster,
            char_count=len(content),
        )

    async def generate_variants(self, idea: str, count: int = 3) -> list[GeneratedPost]:
        cluster = await self.detect_cluster(idea)

        angles = [
            "Schreibe den Post mit einem provokanten, kontraintuitiven Hook.",
            "Schreibe den Post als persoenliche Geschichte / Anekdote.",
            "Schreibe den Post mit konkreten Zahlen und Daten als Aufhaenger.",
        ]

        variants = []
        for i in range(min(count, len(angles))):
            enriched_idea = f"{idea}\n\n[Stil-Anweisung: {angles[i]}]"
            post = await self.generate(enriched_idea, cluster)
            variants.append(post)
        return variants
