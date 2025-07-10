import random
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackContext,
    ConversationHandler,
    MessageHandler,
    Filters,
    CallbackQueryHandler,
)
from dotenv import load_dotenv

# Carga el token desde .env
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

# Estados de la conversación
LENGTH, LABEL = range(2)

def generar_contraseña(longitud=12):
    caracteres = (
        "qwertyuiopasdfghjklñzxcvbnm"
        "QWERTYUIOPASDFGHJKLÑZXCVBNM"
        "1234567890!@#$%&*()_+-=[];,.<>?/"
    )
    return "".join(random.choice(caracteres) for _ in range(longitud))

def start(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("🔐 Generar contraseña", callback_data="gen")],
        [InlineKeyboardButton("📜 Ver guardadas", callback_data="view")],
    ]
    reply = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("¡Bienvenido! Elige una opción:", reply_markup=reply)

def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    if query.data == "gen":
        kb = [
            [
                InlineKeyboardButton("8", callback_data="8"),
                InlineKeyboardButton("12", callback_data="12")
            ],
            [
                InlineKeyboardButton("16", callback_data="16"),
                InlineKeyboardButton("Otra", callback_data="other")
            ],
        ]
        query.edit_message_text(
            "Selecciona la longitud deseada:", reply_markup=InlineKeyboardMarkup(kb)
        )
        return LENGTH

    elif query.data == "view":
        # Lee y muestra el archivo de contraseñas
        if os.path.isfile("contraseñas.txt"):
            with open("contraseñas.txt", "r", encoding="utf-8") as f:
                contenido = f.read().strip() or "– vacío –"
        else:
            contenido = "No se han guardado contraseñas aún."
        query.edit_message_text(f"📜 Contraseñas guardadas:\n{contenido}")
        return ConversationHandler.END

def length_handler(update: Update, context: CallbackContext):
    # Llega desde botón predefinido
    query = update.callback_query
    query.answer()
    if query.data == "other":
        query.edit_message_text("✏️ Escribe la longitud que quieres (un número):")
        return LENGTH
    else:
        context.user_data["length"] = int(query.data)
        query.edit_message_text("✏️ Ahora envía la etiqueta para la contraseña:")
        return LABEL

def length_text_handler(update: Update, context: CallbackContext):
    # Llega texto libre para longitud
    text = update.message.text.strip()
    if text.isdigit() and int(text) > 0:
        context.user_data["length"] = int(text)
        update.message.reply_text("✏️ Ahora envía la etiqueta para la contraseña:")
        return LABEL
    else:
        update.message.reply_text("❗️Por favor envía un número válido para la longitud:")
        return LENGTH

def label_handler(update: Update, context: CallbackContext):
    etiqueta = update.message.text.strip()
    length = context.user_data.get("length", 12)
    pwd = generar_contraseña(length)
    # Envía la contraseña formateada
    update.message.reply_text(
        f"🔑 Contraseña para *{etiqueta}*:\n`{pwd}`",
        parse_mode="Markdown"
    )
    # Guarda en el archivo
    with open("contraseñas.txt", "a", encoding="utf-8") as f:
        f.write(f"{etiqueta}: {pwd}\n")
    update.message.reply_text(
        "🎉 Hecho. Contraseña guardada.\nUsa /start para otra acción."
    )
    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext):
    update.message.reply_text("❌ Operación cancelada. Usa /start para comenzar.")
    return ConversationHandler.END

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    conv = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            CallbackQueryHandler(button_handler)
        ],
        states={
            LENGTH: [
                CallbackQueryHandler(length_handler),
                MessageHandler(Filters.text & ~Filters.command, length_text_handler)
            ],
            LABEL: [
                MessageHandler(Filters.text & ~Filters.command, label_handler)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True
    )

    dp.add_handler(conv)
    updater.start_polling()
    print("Bot en ejecución…")
    updater.idle()

if __name__ == "__main__":
    main()
1