import os
import html
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

ID = "@progg_notebook"  # Заміни на свій канал

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привіт! Я працюю на новій версії бібліотеки 🤖")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Доступні команди:\n/start\n/help\n/post\n/article")

async def post_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = ' '.join(context.args)
    if not text:
        await update.message.reply_text("Напиши текст або додай фото з підписом після /post")
        return
    try:
        await context.bot.send_message(chat_id=ID, text=text)
        await update.message.reply_text("Текст опубліковано!")
    except Exception as e:
        await update.message.reply_text(f"Помилка: {e}")

async def post_photo_with_caption(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message.photo:
        await update.message.reply_text("Будь ласка, надішли фото з підписом, що починається з /post")
        return
    photo = message.photo[-1]
    caption = message.caption or ""
    if caption.lower().startswith("/post"):
        cleaned_caption = caption[len("/post"):].strip()
    else:
        cleaned_caption = caption

    try:
        await context.bot.send_photo(
            chat_id=ID,
            photo=photo.file_id,
            caption=cleaned_caption if cleaned_caption else ""
        )
        await message.delete()
        await update.message.reply_text("Фото з текстом опубліковано!")
    except Exception as e:
        await update.message.reply_text(f"Помилка: {e}")

async def article(update: Update, context: ContextTypes.DEFAULT_TYPE):
    raw_text = update.message.text
    parts = raw_text.replace("/article", "", 1).strip().split("|")
    if len(parts) < 5:
        await update.message.reply_text("Потрібно 5 частин у форматі:\nТема|Опис|Код|Джерела|Хештег")
        return
    topic = parts[0].strip()
    description = parts[1].strip()
    code = html.escape(parts[2].strip())
    sources = parts[3].strip()
    hashtag = parts[4].strip()
    message = (
        f"🏷️ <b>Тема:</b> {topic}\n"
        f"🧩 <b>Опис:</b> {description}\n\n"
        f"💡 <b>Код:</b>\n<pre><code>{code}</code></pre>\n\n"
        f"🔗 <b>Джерела:</b> {sources}\n\n"
        f"#️⃣ <b>Хештег:</b> #{hashtag}"
    )
    try:
        await context.bot.send_message(
            chat_id=ID,
            text=message,
            parse_mode="HTML"
        )
        await update.message.reply_text("Стаття опублікована!")
    except Exception as e:
        await update.message.reply_text(f"Помилка при публікації: {e}")

def main():
    TOKEN = os.environ.get("https://api.render.com/deploy/srv-d1fsid7fte5s73ftt47g?key=SlhdkpvHB1I")
    if not TOKEN:
        print("Помилка: не знайдено BOT_TOKEN в змінних оточення")
        return

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.PHOTO & filters.CaptionRegex(r'^/post'), post_photo_with_caption))
    app.add_handler(CommandHandler("post", post_text))
    app.add_handler(CommandHandler("article", article))

    app.run_polling()

if __name__ == "__main__":
    main()
