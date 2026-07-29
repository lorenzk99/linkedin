import functools
from datetime import datetime, timedelta

from telegram import Update, BotCommand, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, Application

import logging

from app.bot.handlers import authorized
from app.db.repository import PostRepository, StyleProfileRepository

logger = logging.getLogger(__name__)

CLUSTERS = [
    "Stellenschaltung & Kanal-Strategie",
    "KI im Recruiting",
    "Skills-based Hiring",
    "Founder Einblicke",
]

COMMANDS = [
    BotCommand("start", "Bot starten & Hilfe anzeigen"),
    BotCommand("post", "Post aus Idee generieren: /post <id>"),
    BotCommand("list", "Letzte Ideen anzeigen"),
    BotCommand("queue", "Post-Warteschlange anzeigen"),
    BotCommand("status", "Pipeline-Status"),
    BotCommand("style", "Stil-Profil anzeigen"),
    BotCommand("style_import", "Posts fuer Stil-Analyse einsenden"),
    BotCommand("style_done", "Stil-Analyse starten"),
    BotCommand("cluster", "Themen-Cluster anzeigen"),
    BotCommand("plan", "Redaktionsplan anzeigen"),
]


async def post_init(application: Application):
    await application.bot.set_my_commands(COMMANDS)


@authorized
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "<b>Hey! Ich bin dein LinkedIn-Content-Bot.</b>\n\n"
        "Schick mir einfach eine Nachricht mit deiner Post-Idee "
        "und ich mache daraus einen fertigen LinkedIn-Beitrag.\n\n"
        "<b>Kommandos:</b>\n"
        "/post &lt;id&gt; - Post aus Idee generieren\n"
        "/list - Deine Ideen anzeigen\n"
        "/queue - Post-Warteschlange\n"
        "/status - Pipeline-Status\n"
        "/style - Dein Stil-Profil\n"
        "/style_import - Posts fuer Stil-Analyse einsenden\n"
        "/cluster - Themen-Cluster anzeigen\n"
        "/plan - Redaktionsplan\n",
        parse_mode="HTML",
    )


@authorized
async def cmd_queue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    repo = PostRepository()
    drafts = await repo.list_drafts(limit=10)

    if not drafts:
        await update.message.reply_text(
            "Post-Queue ist leer. Generiere zuerst Posts mit /post &lt;id&gt;.",
            parse_mode="HTML",
        )
        return

    lines = ["<b>Post-Warteschlange:</b>\n"]
    for post in drafts:
        preview = post.content[:80].replace("\n", " ")
        if len(post.content) > 80:
            preview += "..."
        cluster_tag = f" [{post.cluster}]" if post.cluster else ""
        created = post.created_at.strftime("%d.%m.%Y") if post.created_at else "?"
        lines.append(
            f"<b>#{post.id}</b>{cluster_tag} <i>({created})</i>\n"
            f"  {preview}\n"
        )

    lines.append(f"<i>Gesamt: {len(drafts)} Entwuerfe</i>")
    await update.message.reply_text("\n".join(lines), parse_mode="HTML")


@authorized
async def cmd_style(update: Update, context: ContextTypes.DEFAULT_TYPE):
    repo = StyleProfileRepository()
    profile = await repo.get_active()

    if not profile:
        await update.message.reply_text(
            "Noch kein Stil-Profil vorhanden.\n\n"
            "Nutze /style_import um deine bestehenden LinkedIn-Posts einzusenden. "
            "Kopiere 10-15 deiner besten Posts und sende sie mir einzeln als Nachrichten. "
            "Danach /style_done und ich analysiere deinen Stil.",
            parse_mode="HTML",
        )
        return

    def _format_json_field(value):
        if value is None:
            return "---"
        if isinstance(value, list):
            return ", ".join(str(v) for v in value[:5])
        if isinstance(value, dict):
            return ", ".join(f"{k}: {v}" for k, v in value.items())
        return str(value)

    hooks = _format_json_field(profile.hook_patterns)
    ctas = _format_json_field(profile.cta_patterns)
    hashtags = _format_json_field(profile.hashtag_strategy)
    sample_count = len(profile.sample_posts) if profile.sample_posts else 0

    text = (
        f"<b>Stil-Profil: {profile.name}</b>\n\n"
        f"<b>Zusammenfassung:</b>\n{profile.summary or '---'}\n\n"
        f"<b>Tonalitaet:</b> {profile.tone or '---'}\n"
        f"<b>Durchschn. Laenge:</b> {profile.avg_length or '---'} Zeichen\n"
        f"<b>Emoji-Nutzung:</b> {profile.emoji_usage or '---'}\n"
        f"<b>Hook-Muster:</b> {hooks}\n"
        f"<b>CTA-Muster:</b> {ctas}\n"
        f"<b>Hashtag-Strategie:</b> {hashtags}\n"
        f"<b>Beispiel-Posts:</b> {sample_count} gespeichert\n"
    )

    await update.message.reply_text(text, parse_mode="HTML")


@authorized
async def cmd_style_import(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["importing_style"] = True
    context.user_data["style_posts"] = []
    await update.message.reply_text(
        "<b>Stil-Import gestartet!</b>\n\n"
        "Kopiere jetzt deine bestehenden LinkedIn-Posts und sende sie mir "
        "einzeln als Nachrichten (ein Post pro Nachricht).\n\n"
        "Ideal: 10-15 Posts, die deinen typischen Stil zeigen.\n\n"
        "Wenn du fertig bist: /style_done",
        parse_mode="HTML",
    )


@authorized
async def cmd_style_done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("importing_style"):
        await update.message.reply_text(
            "Kein Import aktiv. Starte mit /style_import.",
        )
        return

    posts = context.user_data.get("style_posts", [])
    context.user_data["importing_style"] = False

    if len(posts) < 3:
        await update.message.reply_text(
            f"Nur {len(posts)} Posts erhalten. Bitte mindestens 3 Posts einsenden.\n"
            f"Starte erneut mit /style_import.",
        )
        context.user_data["style_posts"] = []
        return

    await update.message.reply_text(
        f"{len(posts)} Posts erhalten. Analysiere deinen Stil... "
        f"das dauert einen Moment."
    )

    from app.ai.style_analyzer import StyleAnalyzer
    analyzer = StyleAnalyzer()
    try:
        profile = await analyzer.analyze_posts(posts)
        await update.message.reply_text(
            f"<b>Stil-Profil erstellt!</b>\n\n"
            f"<b>Zusammenfassung:</b>\n{profile.summary}\n\n"
            f"<b>Tonalitaet:</b> {profile.tone}\n"
            f"<b>Emoji-Nutzung:</b> {profile.emoji_usage}\n\n"
            f"Deine Posts werden jetzt in diesem Stil generiert. "
            f"Nutze /style um das Profil jederzeit anzuzeigen.",
            parse_mode="HTML",
        )
    except Exception as e:
        logger.error("Stil-Analyse fehlgeschlagen: %s", e)
        await update.message.reply_text(
            "Fehler bei der Stil-Analyse. Bitte versuche es erneut mit /style_import."
        )

    context.user_data["style_posts"] = []


def _next_post_slots(start_date, count=4):
    slots = []
    current = start_date
    while len(slots) < count:
        if current.weekday() in (1, 3):
            slots.append(current)
        current += timedelta(days=1)
    return slots


@authorized
async def cmd_plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    today = datetime.now().date()
    slots = _next_post_slots(today, count=4)

    day_labels = {1: "Di", 3: "Do"}

    lines = ["<b>Redaktionsplan --- naechste Posts:</b>\n"]
    for i, slot_date in enumerate(slots):
        day_name = day_labels[slot_date.weekday()]
        cluster = CLUSTERS[i % len(CLUSTERS)]
        date_str = slot_date.strftime("%d.%m.%Y")
        lines.append(f"  {day_name} {date_str}:  <i>{cluster}</i>")

    lines.append("\nNutze /post um den naechsten Post zu generieren.")
    await update.message.reply_text("\n".join(lines), parse_mode="HTML")


@authorized
async def cmd_cluster(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from sqlalchemy import select, func
    from app.db.repository import async_session
    from app.db.models import Post

    async with async_session() as session:
        result = await session.execute(
            select(Post.cluster, func.count(Post.id)).group_by(Post.cluster)
        )
        cluster_counts = {row[0]: row[1] for row in result.all()}

    lines = ["<b>Themen-Cluster:</b>\n"]
    total = 0
    for cluster in CLUSTERS:
        count = cluster_counts.get(cluster, 0)
        total += count
        bar = "+" * count if count else "---"
        lines.append(f"  <b>{cluster}</b>\n    {count} Posts  {bar}\n")

    uncategorized = cluster_counts.get(None, 0)
    if uncategorized:
        total += uncategorized
        lines.append(f"  <b>Ohne Cluster:</b> {uncategorized} Posts\n")

    lines.append(f"<i>Gesamt: {total} Posts</i>")
    await update.message.reply_text("\n".join(lines), parse_mode="HTML")
