import os, requests, time
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    filters, ContextTypes, ConversationHandler
)

TOKEN = os.environ.get("TOKEN")
LINKS = 0

def submit_group(link):
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Referer': 'https://groupsor.link/group/addgroup',
        'Origin': 'https://groupsor.link'
    }
    payload = {
        'grpLink': link,
        'grpCat': 'Entertainment/Masti',
        'grpCountry': 'India',
        'grpLang': 'Hindi',
        'grpTags': '',
        'grpDesc': ''
    }
    session = requests.Session()
    session.get("https://groupsor.link/group/addgroup", headers=headers)
    r = session.post("https://groupsor.link/group/addgroup", data=payload, headers=headers, timeout=15)
    return r.status_code == 200

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎭 *India Entertainment/Masti Bot*\n\n"
        "📌 Fixed Settings:\n"
        "🇮🇳 Country: India\n"
        "🗣️ Language: Hindi\n"
        "📂 Category: Entertainment/Masti\n\n"
        "Paste all your WhatsApp links below\n"
        "_(one link per line)_ and send!",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove()
    )
    return LINKS

async def get_links(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    links = [l.strip() for l in text.splitlines() if "chat.whatsapp.com" in l.strip()]

    if not links:
        await update.message.reply_text(
            "❌ No valid links found!\n\n"
            "Send links like:\n"
            "https://chat.whatsapp.com/xxxxx\n"
            "https://chat.whatsapp.com/yyyyy"
        )
        return LINKS

    total = len(links)
    msg = await update.message.reply_text(f"⏳ Submitting *{total}* groups...", parse_mode="Markdown")

    success, failed = 0, 0
    log = ""

    for i, link in enumerate(links, 1):
        try:
            ok = submit_group(link)
            if ok:
                success += 1
                log += f"✅ {i}. Submitted\n"
            else:
                failed += 1
                log += f"⚠️ {i}. Check manually\n"
        except:
            failed += 1
            log += f"❌ {i}. Error\n"
        time.sleep(1)

    result = (
        f"🎉 *Done!*\n\n"
        f"✅ Success: {success}\n"
        f"❌ Failed: {failed}\n"
        f"📊 Total: {total}\n\n"
        f"{log}\n"
        f"Send /start to submit more!"
    )
    await msg.edit_text(result, parse_mode="Markdown")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Cancelled. Send /start to begin.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            LINKS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_links)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    app.add_handler(conv)
    print("✅ Bot running...")
    app.run_polling()
