import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, ContextTypes, filters

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Simple in-memory DB (replace with SQLite/PostgreSQL for persistence)
file_db = {}

# Index uploaded files
async def index_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    document = update.message.document
    if document:
        file_id = document.file_id
        file_name = document.file_name
        file_db[file_name.lower()] = file_id
        await update.message.reply_text(f"Indexed file: {file_name}")

# Search files by keyword
async def search_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /search <keyword>")
        return
    query = " ".join(context.args).lower()
    results = [name for name in file_db if query in name]
    if results:
        response = "\n".join(results[:10])
        await update.message.reply_text(f"Found files:\n{response}")
    else:
        await update.message.reply_text("No files found.")

# Get a file by exact name
async def get_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /get <file name>")
        return
    file_name = " ".join(context.args).lower()
    file_id = file_db.get(file_name)
    if file_id:
        await update.message.reply_document(file_id)
    else:
        await update.message.reply_text("File not found.")

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Send files to this bot to index them, or use /search <keyword> to find files.")

# Main
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("search", search_file))
    app.add_handler(CommandHandler("get", get_file))
    app.add_handler(MessageHandler(filters.Document.ALL, index_file))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
