from telegram import Update, BotCommand
from telegram.ext import ContextTypes, Application

from app.bot.handlers import authorized

COMMANDS = [
    BotCommand("start", "Bot starten & Hilfe anzeigen"),
    BotCommand("post", "Post aus Idee generieren: /post <id>"),
    BotCommand("list", "Letzte Ideen anzeigen"),
    BotCommand("queue", "Post-Warteschlange anzeigen"),
    BotCommand("status", "Pipeline-Status"),
    BotCommand("style", "Stil-Profil anzeigen"),
    BotCommand("cluster", "Themen-Cluster verwalten"),
    BotCommand("plan", "Redaktionsplan anzeigen"),
]


async def post_init(application: Application):
    await application.bot.set_my_commands(COMMANDS)


@authorized
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hey! Ich bin dein LinkedIn-Content-Bot.\n\n"
        "Schick mir einfach eine Nachricht mit deiner Post-Idee "
        "und ich mache daraus einen fertigen LinkedIn-Beitrag.\n\n"
        "**Kommandos:**\n"
        "/post <id> - Post aus Idee generieren\n"
        "/list - Deine Ideen anzeigen\n"
        "/queue - Post-Warteschlange\n"
        "/status - Pipeline-Status\n"
        "/style - Dein Stil-Profil\n"
        "/plan - Redaktionsplan\n",
        parse_mode="Markdown",
    )


@authorized
async def cmd_queue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Post-Queue ist noch leer. Generiere zuerst Posts mit /post <id>."
    )


@authorized
async def cmd_style(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from app.ai.style_analyzer import StyleAnalyzer
    analyzer = StyleAnalyzer()
    profile = await analyzer.get_profile()
    if not profile:
        await update.message.reply_text(
            "Noch kein Stil-Profil vorhanden.\n"
            "Speichere bestehende LinkedIn-Posts in data/sample_posts/ "
            "und starte die Analyse."
        )
        return
    await update.message.reply_text(
        f"**Dein Stil-Profil:**\n\n{profile.summary}",
        parse_mode="Markdown",
    )


@authorized
async def cmd_plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "**Redaktionsplan - naechste Posts:**\n\n"
        "Di: Skills-based Hiring (Meinungs-Post)\n"
        "Do: Stellenschaltung (Praxis-Tipp)\n\n"
        "Nutze /post um den naechsten Post zu generieren.",
        parse_mode="Markdown",
    )
