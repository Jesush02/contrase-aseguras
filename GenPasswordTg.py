import os
import random
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ConversationHandler, ContextTypes
)

# Estados
LENGTH, LABEL = range(2)

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

def generar_contraseña(longitud=12):
    caracteres = (
        "qwertyuiopasdfghjklñzxcvbnm"
        "QWERTYUIOPASDFGHJKLÑZXCVBNM"
        "1234567890!@#$%&*()_+-=[];,.<>?/"
    )
    return "".join(random.choice(caracteres) for _ in range(longitud))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔐 Generar contraseña", callback_data="gen")],
        [InlineKeyboardButton("📜 Ver guardadas", callback_data="view")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("¡Bienvenido! Elige una opción:", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "gen":
        kb = [
            [InlineKeyboardButton("8", callback_data="8"), InlineKeyboardButton("12", callback_data="12")],
            [InlineKeyboardButton("16", callback_data="16"), InlineKeyboardButton("Otra", callback_data="other")]
        ]
        await query.edit_message_text("Selecciona la longitud deseada:", reply_markup=InlineKeyboardMarkup(kb))
        return LENGTH
    elif query.data == "view":
        if os.path.isfile("contraseñas.txt"):
            with open("contraseñas.txt", "r", encoding="utf-8") as f:
                contenido = f.read().strip() or "– vacío –"
        else:
            contenido = "No se han guardado contraseñas aún."
        await query.edit_message_text(f"📜 Contraseñas guardadas:\n{contenido}")
        return ConversationHandler.END

async def length_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "other":
        await query.edit_message_text("✏️ Escribe la longitud que quieres (número):")
        return LENGTH
    else:
        context.user_data["length"] = int(query.data)
        await query.edit_message_text("✏️ Ahora escribe la etiqueta:")
        return LABEL

async def length_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if text.isdigit() and int(text) > 0:
        context.user_data["length"] = int(text)
        await update.message.reply_text("✏️ Ahora escribe la etiqueta:")
        return LABEL
    else:
        await update.message.reply_text("❗️Por favor envía un número válido:")
        return LENGTH

async def label_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    etiqueta = update.message.text.strip()
    length = context.user_data.get("length", 12)
    pwd = generar_contraseña(length)
    await update.message.reply_text(f"🔑 Contraseña para *{etiqueta}*:\n`{pwd}`", parse_mode="Markdown")
    with open("contraseñas.txt", "a", encoding="utf-8") as f:
        f.write(f"{etiqueta}: {pwd}\n")
    await update.message.reply_text("🎉 Hecho. Usa /start para otra acción.")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Operación cancelada. Usa /start para comenzar.")
    return ConversationHandler.END

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            LENGTH: [
                CallbackQueryHandler(length_handler, pattern="^(8|12|16|other)$"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, length_text_handler),
            ],
            LABEL: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, label_handler)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv)
    app.add_handler(CallbackQueryHandler(button_handler, pattern="^(gen|view)$"))

    print("✅ Bot corriendo…")
    app.run_polling()

if __name__ == "__main__":
    main()
