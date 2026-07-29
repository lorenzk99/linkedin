import json
import logging
import re
from pathlib import Path

import anthropic

from app.config import settings
from app.ai.prompts import STYLE_ANALYSIS_PROMPT
from app.db.models import StyleProfile
from app.db.repository import StyleProfileRepository

logger = logging.getLogger(__name__)


def _extract_json(text: str) -> dict:
    match = re.search(r"```(?:json)?\s*\n?(.*?)```", text, re.DOTALL)
    if match:
        return json.loads(match.group(1).strip())
    return json.loads(text.strip())


class StyleAnalyzer:
    def __init__(self):
        self.client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
        self.repo = StyleProfileRepository()

    async def analyze_posts(self, posts: list[str]) -> StyleProfile:
        posts_text = "\n\n---\n\n".join(
            f"Post {i+1}:\n{post}" for i, post in enumerate(posts)
        )
        prompt = STYLE_ANALYSIS_PROMPT.format(posts=posts_text)

        response = await self.client.messages.create(
            model="claude-sonnet-5",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
        )

        raw = response.content[0].text
        logger.info("Stil-Analyse Antwort erhalten (%d Zeichen)", len(raw))
        result = _extract_json(raw)

        profile = StyleProfile(
            name="default",
            summary=result["summary"],
            tone=result["tone"],
            avg_length=result.get("avg_length", 1500),
            emoji_usage=result.get("emoji_usage", "minimal"),
            hook_patterns=result.get("hook_patterns", []),
            cta_patterns=result.get("cta_patterns", []),
            hashtag_strategy=result.get("hashtag_strategy", {}),
            sample_posts=posts[:5],
        )
        return await self.repo.save(profile)

    async def get_profile(self) -> StyleProfile | None:
        return await self.repo.get_active()

    async def analyze_from_files(self, directory: str = "data/sample_posts") -> StyleProfile:
        posts_dir = Path(directory)
        if not posts_dir.exists():
            raise FileNotFoundError(f"Verzeichnis {directory} nicht gefunden.")

        posts = []
        for file in sorted(posts_dir.glob("*.txt")):
            posts.append(file.read_text(encoding="utf-8"))

        if not posts:
            raise ValueError("Keine Posts gefunden. Speichere Posts als .txt-Dateien.")

        return await self.analyze_posts(posts)
