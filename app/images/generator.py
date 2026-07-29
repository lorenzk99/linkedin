from pathlib import Path

import httpx
from openai import AsyncOpenAI

from app.config import settings
from app.ai.prompts import IMAGE_PROMPT_TEMPLATE
from app.images.templates import CLUSTER_IMAGE_STYLES


class ImageGenerator:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.output_dir = Path("data/generated_images")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def generate(
        self,
        topic: str,
        post_id: int,
        colors: str | None = None,
        cluster: str | None = None,
    ) -> str:
        style_info = CLUSTER_IMAGE_STYLES.get(cluster or "", {})

        prompt = IMAGE_PROMPT_TEMPLATE.format(
            topic=topic,
            colors=colors or style_info.get("colors", "Blau, Weiss, dezentes Grau"),
            style=style_info.get("style", "Modern, clean, professionell, Business-Kontext"),
            elements=style_info.get("elements", "Professionelle, thematisch passende Elemente"),
        )

        response = await self.client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1792x1024",
            quality="hd",
            n=1,
        )

        image_url = response.data[0].url
        file_path = self.output_dir / f"post_{post_id}.png"

        async with httpx.AsyncClient() as http:
            img_response = await http.get(image_url)
            file_path.write_bytes(img_response.content)

        return str(file_path)
