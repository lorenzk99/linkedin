import functools
import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from app.config import settings
from app.db.repository import IdeaRepository, PostRepository
from app.ai.post_generator import PostGenerator
from app.images.generator import ImageGenerator
from app.images.templates import CLUSTER_IMAGE_STYLES

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Auth decorator
# ---------------------------------------------------------------------------

def authorized(func):
    @functools.wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        allowed = settings.allowed_user_ids
        if allowed and user_id not in allowed:
            if update.message:
                await update.message.reply_text("Nicht autorisiert.")
            elif update.callback_query:
                await update.callback_query.answer("Nicht autorisiert.")
            return
        return await func(update, context)
    return wrapper


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _post_keyboard(post_id: int) -> InlineKeyboardMarkup:
    """Build the inline keyboard for post review actions."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "Nochmal generieren",
                callback_data=f"regenerate:{post_id}",
            ),
            InlineKeyboardButton(
                "Neues Bild",
                callback_data=f"newimage:{post_id}",
            ),
        ],
        [
            InlineKeyboardButton(
                "Fertig",
                callback_data=f"approve:{post_id}",
            ),
        ],
    ])


async def _edit_callback_message(
    query,
    text: str,
    reply_markup: InlineKeyboardMarkup | None = None,
) -> None:
    """Edit the message that triggered a callback query.

    Picks ``edit_message_caption`` for document messages and
    ``edit_message_text`` for plain text messages.  Pass
    ``InlineKeyboardMarkup([])`` (or omit *reply_markup*) to strip the
    inline keyboard.
    """
    markup = reply_markup if reply_markup is not None else InlineKeyboardMarkup([])
    if query.message.document:
        await query.edit_message_caption(caption=text, reply_markup=markup)
    else:
        await query.edit_message_text(text=text, reply_markup=markup)


def _cluster_colors(cluster: str | None) -> str:
    """Return cluster-specific image colors or a neutral fallback."""
    if cluster:
        style = CLUSTER_IMAGE_STYLES.get(cluster, {})
        if "colors" in style:
            return style["colors"]
    return "Blau, Weiss, dezentes Grau"


# ---------------------------------------------------------------------------
# Message handler: new idea
# ---------------------------------------------------------------------------

@authorized
async def handle_idea(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save an incoming text message as a post idea with auto-detected cluster."""
    text = update.message.text
    if not text:
        await update.message.reply_text(
            "Bitte sende mir eine Text-Nachricht mit deiner Idee."
        )
        return

    # Auto-detect cluster via Claude Haiku
    generator = PostGenerator()
    cluster = None
    try:
        cluster = await generator.detect_cluster(text)
    except Exception as e:
        logger.error("Cluster-Erkennung fehlgeschlagen: %s", e)

    # Persist idea with cluster
    repo = IdeaRepository()
    idea = await repo.create(
        text=text,
        user_id=update.effective_user.id,
        cluster=cluster,
    )

    cluster_info = f"\nCluster: <b>{cluster}</b>" if cluster else ""
    await update.message.reply_text(
        f"Idee gespeichert! (#{idea.id}){cluster_info}\n\n"
        f"Nutze /post {idea.id} um daraus einen LinkedIn-Beitrag zu generieren.",
        parse_mode="HTML",
    )


# ---------------------------------------------------------------------------
# Command handler: /post <id>
# ---------------------------------------------------------------------------

@authorized
async def handle_generate_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generate a full LinkedIn post (text + image) from a stored idea."""
    if not context.args:
        await update.message.reply_text(
            "Bitte gib die Ideen-ID an: /post &lt;id&gt;",
            parse_mode="HTML",
        )
        return

    try:
        idea_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("Ungueltige ID. Bitte eine Zahl angeben.")
        return

    idea_repo = IdeaRepository()
    idea = await idea_repo.get(idea_id)
    if not idea:
        await update.message.reply_text(f"Idee #{idea_id} nicht gefunden.")
        return

    await update.message.reply_text(
        "Generiere LinkedIn-Post... das dauert einen Moment."
    )

    # 1. Generate post text via Anthropic Claude ---------------------------
    generator = PostGenerator()
    try:
        generated = await generator.generate(idea.text, idea.cluster)
    except Exception as e:
        logger.error("Post-Generierung fehlgeschlagen: %s", e)
        await update.message.reply_text(
            "Fehler bei der Post-Generierung. Bitte versuche es spaeter erneut."
        )
        return

    # 2. Save post to DB ---------------------------------------------------
    post_repo = PostRepository()
    post = await post_repo.create(
        idea_id=idea.id,
        content=generated.content,
        cluster=generated.cluster,
    )

    # 3. Generate image via DALL-E with cluster-specific colors ------------
    colors = _cluster_colors(generated.cluster)
    image_gen = ImageGenerator()
    image_path = None
    try:
        image_path = await image_gen.generate(idea.text, post.id, colors=colors)
        await post_repo.save_image(post.id, image_path)
    except Exception as e:
        logger.error("Bild-Generierung fehlgeschlagen: %s", e)

    # 4. Mark idea as generated --------------------------------------------
    await idea_repo.mark_generated(idea.id)

    # 5. Send post text ----------------------------------------------------
    await update.message.reply_text(
        f"<b>LinkedIn-Post (Entwurf #{post.id})</b>\n\n"
        f"{generated.content}\n\n"
        f"---\n"
        f"Cluster: {generated.cluster}\n"
        f"Zeichen: {generated.char_count}",
        parse_mode="HTML",
    )

    # 6. Send image as DOCUMENT with inline keyboard -----------------------
    keyboard = _post_keyboard(post.id)
    if image_path:
        try:
            with open(image_path, "rb") as f:
                await update.message.reply_document(
                    document=f,
                    filename=f"linkedin_post_{post.id}.png",
                    caption=f"Bild fuer Post #{post.id}",
                    reply_markup=keyboard,
                )
        except Exception as e:
            logger.error("Bild-Versand fehlgeschlagen: %s", e)
            await update.message.reply_text(
                "Bild konnte nicht gesendet werden.",
                reply_markup=keyboard,
            )
    else:
        await update.message.reply_text(
            "Bild-Generierung fehlgeschlagen. Du kannst ein neues Bild anfordern.",
            reply_markup=keyboard,
        )


# ---------------------------------------------------------------------------
# Callback query router
# ---------------------------------------------------------------------------

@authorized
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Route inline keyboard button presses to their action handlers."""
    query = update.callback_query
    await query.answer()

    data = query.data or ""
    if ":" not in data:
        logger.warning("Unbekannter Callback: %s", data)
        return

    action, post_id_str = data.split(":", 1)
    try:
        post_id = int(post_id_str)
    except ValueError:
        logger.warning("Ungueltige Post-ID im Callback: %s", data)
        return

    if action == "regenerate":
        await _handle_regenerate(query, post_id)
    elif action == "newimage":
        await _handle_new_image(query, post_id)
    elif action == "approve":
        await _handle_approve(query, post_id)
    else:
        logger.warning("Unbekannte Callback-Aktion: %s", action)


# ---------------------------------------------------------------------------
# Callback actions
# ---------------------------------------------------------------------------

async def _handle_regenerate(query, post_id: int) -> None:
    """Generate a completely new post variant (text + image)."""
    post_repo = PostRepository()
    post = await post_repo.get(post_id)
    if not post:
        await _edit_callback_message(query, "Post nicht gefunden.")
        return

    idea_repo = IdeaRepository()
    idea = await idea_repo.get(post.idea_id)
    if not idea:
        await _edit_callback_message(query, "Zugehoerige Idee nicht gefunden.")
        return

    # Remove old keyboard and show progress
    await _edit_callback_message(query, "Generiere neuen Post-Entwurf...")

    # Generate new post text
    generator = PostGenerator()
    try:
        generated = await generator.generate(idea.text, post.cluster)
    except Exception as e:
        logger.error("Re-Generierung fehlgeschlagen: %s", e)
        await query.message.reply_text(
            "Fehler bei der Generierung. Bitte versuche es erneut.",
            reply_markup=_post_keyboard(post_id),
        )
        return

    # Save as new post record
    new_post = await post_repo.create(
        idea_id=idea.id,
        content=generated.content,
        cluster=generated.cluster,
    )

    # Send new post text
    await query.message.reply_text(
        f"<b>LinkedIn-Post (Neuer Entwurf #{new_post.id})</b>\n\n"
        f"{generated.content}\n\n"
        f"---\n"
        f"Cluster: {generated.cluster}\n"
        f"Zeichen: {generated.char_count}",
        parse_mode="HTML",
    )

    # Generate new image with cluster-specific colors
    colors = _cluster_colors(generated.cluster)
    image_gen = ImageGenerator()
    image_path = None
    try:
        image_path = await image_gen.generate(idea.text, new_post.id, colors=colors)
        await post_repo.save_image(new_post.id, image_path)
    except Exception as e:
        logger.error("Bild-Generierung fehlgeschlagen: %s", e)

    # Send new image (or fallback text) with fresh keyboard
    keyboard = _post_keyboard(new_post.id)
    if image_path:
        try:
            with open(image_path, "rb") as f:
                await query.message.reply_document(
                    document=f,
                    filename=f"linkedin_post_{new_post.id}.png",
                    caption=f"Bild fuer Post #{new_post.id}",
                    reply_markup=keyboard,
                )
        except Exception as e:
            logger.error("Bild-Versand fehlgeschlagen: %s", e)
            await query.message.reply_text(
                "Bild konnte nicht gesendet werden.",
                reply_markup=keyboard,
            )
    else:
        await query.message.reply_text(
            "Bild konnte nicht generiert werden.",
            reply_markup=keyboard,
        )


async def _handle_new_image(query, post_id: int) -> None:
    """Generate only a new image for an existing post."""
    post_repo = PostRepository()
    post = await post_repo.get(post_id)
    if not post:
        await _edit_callback_message(query, "Post nicht gefunden.")
        return

    idea_repo = IdeaRepository()
    idea = await idea_repo.get(post.idea_id)

    # Remove old keyboard and show progress
    await _edit_callback_message(query, "Generiere neues Bild...")

    colors = _cluster_colors(post.cluster)
    image_gen = ImageGenerator()
    topic = idea.text if idea else "LinkedIn Post"
    try:
        image_path = await image_gen.generate(topic, post_id, colors=colors)
        await post_repo.save_image(post_id, image_path)
    except Exception as e:
        logger.error("Bild-Generierung fehlgeschlagen: %s", e)
        await query.message.reply_text(
            "Fehler bei der Bild-Generierung. Bitte versuche es erneut.",
            reply_markup=_post_keyboard(post_id),
        )
        return

    # Send new image with keyboard
    keyboard = _post_keyboard(post_id)
    try:
        with open(image_path, "rb") as f:
            await query.message.reply_document(
                document=f,
                filename=f"linkedin_post_{post_id}.png",
                caption=f"Neues Bild fuer Post #{post_id}",
                reply_markup=keyboard,
            )
    except Exception as e:
        logger.error("Bild-Versand fehlgeschlagen: %s", e)
        await query.message.reply_text(
            "Bild konnte nicht gesendet werden.",
            reply_markup=keyboard,
        )


async def _handle_approve(query, post_id: int) -> None:
    """Mark the post as approved and remove the inline keyboard."""
    post_repo = PostRepository()
    post = await post_repo.get(post_id)
    if not post:
        await _edit_callback_message(query, "Post nicht gefunden.")
        return

    await post_repo.update_status(post_id, "approved")
    await _edit_callback_message(query, f"Post #{post_id} freigegeben!")


# ---------------------------------------------------------------------------
# Command handler: /list
# ---------------------------------------------------------------------------

@authorized
async def handle_list_ideas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List recent ideas with cluster tags."""
    repo = IdeaRepository()
    ideas = await repo.list_recent(limit=10)
    if not ideas:
        await update.message.reply_text(
            "Noch keine Ideen gespeichert. Sende mir einfach eine Nachricht!"
        )
        return

    lines = ["<b>Deine letzten Ideen:</b>\n"]
    for idea in ideas:
        check = "&#10003;" if idea.post_generated else "&#9675;"
        cluster_tag = f" [{idea.cluster}]" if idea.cluster else ""
        preview = idea.text[:60] + "..." if len(idea.text) > 60 else idea.text
        lines.append(f"{check} #{idea.id}{cluster_tag}: {preview}")
    await update.message.reply_text("\n".join(lines), parse_mode="HTML")


# ---------------------------------------------------------------------------
# Command handler: /status
# ---------------------------------------------------------------------------

@authorized
async def handle_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show pipeline statistics including post queue count."""
    idea_repo = IdeaRepository()
    post_repo = PostRepository()
    stats = await idea_repo.get_stats()
    drafts = await post_repo.list_drafts()

    await update.message.reply_text(
        f"<b>Pipeline-Status:</b>\n\n"
        f"Ideen gesamt: {stats['total']}\n"
        f"Posts generiert: {stats['generated']}\n"
        f"Offen: {stats['pending']}\n"
        f"Posts in Warteschlange: {len(drafts)}",
        parse_mode="HTML",
    )
