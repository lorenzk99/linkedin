import functools
import logging

from telegram import Update
from telegram.ext import ContextTypes

from app.config import settings
from app.db.repository import IdeaRepository
from app.ai.post_generator import PostGenerator
from app.ai.style_analyzer import StyleAnalyzer

logger = logging.getLogger(__name__)


def authorized(func):
    @functools.wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        allowed = settings.allowed_user_ids
        if allowed and user_id not in allowed:
            await update.message.reply_text("Nicht autorisiert.")
            return
        return await func(update, context)
    return wrapper


@authorized
async def handle_idea(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if not text:
        await update.message.reply_text("Bitte sende mir eine Text-Nachricht mit deiner Idee.")
        return

    repo = IdeaRepository()
    idea = await repo.create(
        text=text,
        user_id=update.effective_user.id,
    )
    await update.message.reply_text(
        f"Idee gespeichert! (#{idea.id})\n\n"
        f"Nutze /post {idea.id} um daraus einen LinkedIn-Beitrag zu generieren."
    )


@authorized
async def handle_generate_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Bitte gib die Ideen-ID an: /post <id>")
        return

    idea_id = int(context.args[0])
    repo = IdeaRepository()
    idea = await repo.get(idea_id)
    if not idea:
        await update.message.reply_text(f"Idee #{idea_id} nicht gefunden.")
        return

    await update.message.reply_text("Generiere LinkedIn-Post... das dauert einen Moment.")

    generator = PostGenerator()
    post = await generator.generate(idea.text, idea.cluster)

    await update.message.reply_text(
        f"**LinkedIn-Post (Entwurf)**\n\n{post.content}\n\n"
        f"---\n"
        f"Cluster: {post.cluster}\n"
        f"Zeichen: {len(post.content)}",
        parse_mode="Markdown",
    )


@authorized
async def handle_list_ideas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    repo = IdeaRepository()
    ideas = await repo.list_recent(limit=10)
    if not ideas:
        await update.message.reply_text("Noch keine Ideen gespeichert. Sende mir einfach eine Nachricht!")
        return

    lines = ["**Deine letzten Ideen:**\n"]
    for idea in ideas:
        status = "✓" if idea.post_generated else "○"
        preview = idea.text[:60] + "..." if len(idea.text) > 60 else idea.text
        lines.append(f"{status} #{idea.id}: {preview}")
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


@authorized
async def handle_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    repo = IdeaRepository()
    stats = await repo.get_stats()
    await update.message.reply_text(
        f"**Pipeline-Status:**\n\n"
        f"Ideen gesamt: {stats['total']}\n"
        f"Posts generiert: {stats['generated']}\n"
        f"Offen: {stats['pending']}\n",
        parse_mode="Markdown",
    )


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data or ""

    if data.startswith("post_detail:"):
        post_id = int(data.split(":")[1])
        from app.db.repository import PostRepository
        repo = PostRepository()
        post = await repo.get(post_id)
        if post:
            await query.edit_message_text(
                f"<b>Post #{post.id}</b>\n\n"
                f"{post.content}\n\n"
                f"<i>Cluster: {post.cluster or '---'} | "
                f"Zeichen: {post.char_count}</i>",
                parse_mode="HTML",
            )
        else:
            await query.edit_message_text(f"Post #{post_id} nicht gefunden.")
    else:
        logger.warning("Unbekannter Callback: %s", data)
        await query.edit_message_text("Unbekannte Aktion.")
