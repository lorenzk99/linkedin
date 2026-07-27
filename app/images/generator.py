from pathlib import Path

import httpx
from openai import AsyncOpenAI

from app.config import settings
from app.ai.prompts import IMAGE_PROMPT_TEMPLATE


class ImageGenerator:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.output_dir = Path("data/generated_images")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def generate(self, topic: str, post_id: int) -> str:
        prompt = IMAGE_PROMPT_TEMPLATE.format(
            topic=topic,
            colors="Blau, Weiss, dezentes Grau",
            width=settings.linkedin_image_width,
            height=settings.linkedin_image_height,
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
