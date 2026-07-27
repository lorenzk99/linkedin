from datetime import datetime

from sqlalchemy import String, Text, Integer, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Idea(Base):
    __tablename__ = "ideas"

    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    cluster: Mapped[str | None] = mapped_column(String(100))
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    post_generated: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    posts: Mapped[list["Post"]] = relationship(back_populates="idea")


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    idea_id: Mapped[int] = mapped_column(ForeignKey("ideas.id"), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    cluster: Mapped[str | None] = mapped_column(String(100))
    version: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[str] = mapped_column(String(20), default="draft")
    hashtags: Mapped[dict | None] = mapped_column(JSON)
    char_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    idea: Mapped["Idea"] = relationship(back_populates="posts")
    images: Mapped[list["GeneratedImage"]] = relationship(back_populates="post")


class StyleProfile(Base):
    __tablename__ = "style_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    summary: Mapped[str] = mapped_column(Text)
    tone: Mapped[str | None] = mapped_column(String(50))
    avg_length: Mapped[int | None] = mapped_column(Integer)
    emoji_usage: Mapped[str | None] = mapped_column(String(20))
    hook_patterns: Mapped[dict | None] = mapped_column(JSON)
    cta_patterns: Mapped[dict | None] = mapped_column(JSON)
    hashtag_strategy: Mapped[dict | None] = mapped_column(JSON)
    sample_posts: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class GeneratedImage(Base):
    __tablename__ = "generated_images"

    id: Mapped[int] = mapped_column(primary_key=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    prompt_used: Mapped[str] = mapped_column(Text)
    width: Mapped[int] = mapped_column(Integer, default=1200)
    height: Mapped[int] = mapped_column(Integer, default=627)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    post: Mapped["Post"] = relationship(back_populates="images")
