import json
from dataclasses import dataclass

import anthropic

from app.config import settings
from app.ai.prompts import POST_GENERATION_PROMPT, CLUSTER_DETECTION_PROMPT
from app.ai.style_analyzer import StyleAnalyzer
from app.db.repository import PostRepository, IdeaRepository


@dataclass
class GeneratedPost:
    content: str
    cluster: str
    char_count: int


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
        return response.content[0].text.strip()

    async def generate(self, idea: str, cluster: str | None = None) -> GeneratedPost:
        if not cluster:
            cluster = await self.detect_cluster(idea)

        profile = await self.style_analyzer.get_profile()
        style_text = profile.summary if profile else "Professionell, direkt, praxisnah. DACH-Recruiting-Experte."
        example_text = ""
        if profile and profile.sample_posts:
            example_text = "\n\n---\n\n".join(profile.sample_posts[:3])

        prompt = POST_GENERATION_PROMPT.format(
            style_profile=style_text,
            cluster=cluster,
            idea=idea,
            example_posts=example_text or "Keine Beispiele verfuegbar.",
        )

        response = await self.client.messages.create(
            model="claude-sonnet-5",
            max_tokens=3000,
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
        variants = []
        for _ in range(count):
            post = await self.generate(idea, cluster)
            variants.append(post)
        return variants
