from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.db.models import Idea, Post, StyleProfile

engine = create_async_engine(settings.database_url)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class IdeaRepository:
    async def create(self, text: str, user_id: int, cluster: str | None = None) -> Idea:
        async with async_session() as session:
            idea = Idea(text=text, user_id=user_id, cluster=cluster)
            session.add(idea)
            await session.commit()
            await session.refresh(idea)
            return idea

    async def get(self, idea_id: int) -> Idea | None:
        async with async_session() as session:
            return await session.get(Idea, idea_id)

    async def list_recent(self, limit: int = 10) -> list[Idea]:
        async with async_session() as session:
            result = await session.execute(
                select(Idea).order_by(Idea.created_at.desc()).limit(limit)
            )
            return list(result.scalars().all())

    async def get_stats(self) -> dict:
        async with async_session() as session:
            total = await session.scalar(select(func.count(Idea.id)))
            generated = await session.scalar(
                select(func.count(Idea.id)).where(Idea.post_generated.is_(True))
            )
            return {
                "total": total or 0,
                "generated": generated or 0,
                "pending": (total or 0) - (generated or 0),
            }

    async def mark_generated(self, idea_id: int):
        async with async_session() as session:
            idea = await session.get(Idea, idea_id)
            if idea:
                idea.post_generated = True
                await session.commit()


class PostRepository:
    async def create(self, idea_id: int, content: str, cluster: str | None = None) -> Post:
        async with async_session() as session:
            post = Post(
                idea_id=idea_id,
                content=content,
                cluster=cluster,
                char_count=len(content),
            )
            session.add(post)
            await session.commit()
            await session.refresh(post)
            return post

    async def get(self, post_id: int) -> Post | None:
        async with async_session() as session:
            return await session.get(Post, post_id)

    async def list_drafts(self, limit: int = 10) -> list[Post]:
        async with async_session() as session:
            result = await session.execute(
                select(Post)
                .where(Post.status == "draft")
                .order_by(Post.created_at.desc())
                .limit(limit)
            )
            return list(result.scalars().all())


class StyleProfileRepository:
    async def get_active(self) -> StyleProfile | None:
        async with async_session() as session:
            result = await session.execute(
                select(StyleProfile).order_by(StyleProfile.updated_at.desc()).limit(1)
            )
            return result.scalar_one_or_none()

    async def save(self, profile: StyleProfile) -> StyleProfile:
        async with async_session() as session:
            session.add(profile)
            await session.commit()
            await session.refresh(profile)
            return profile
