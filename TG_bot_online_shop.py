from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler
import datetime

TOKEN = "8355137759:AAFIR-m5cToGXi5d8OWZskB42A6NsE-cxXA"

# База товаров
products = {
    "Книга": {"price": 500, "delivery": 2, "description": "Интересная книга 📖"},
    "Часы": {"price": 15000, "delivery": 5, "description": "Стильные часы ⌚"},
    "Наушники": {"price": 3000, "delivery": 3, "description": "Беспроводные наушники 🎧"}
}

# Праздники (день, месяц)
holidays = [(3, 8), (12, 31)]  # 8 марта, 31 декабря

# Меню
menu_buttons = [["📚 Каталог", "🔍 Поиск"], ["ℹ️ Помощь / Контакты", "🛒 Корзина"]]
menu_markup = ReplyKeyboardMarkup(menu_buttons, resize_keyboard=True)

# Корзина (память)
cart = {}

def check_holiday(date):
    return (date.month, date.day) in holidays

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я помощник магазина 🛍️. Выберите действие:", reply_markup=menu_markup)

# Показ каталога
async def show_catalog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for item_name, item in products.items():
        keyboard = [
            [InlineKeyboardButton("🛒 Купить", callback_data=f"buy_{item_name}")],
            [InlineKeyboardButton("ℹ️ Подробнее", callback_data=f"info_{item_name}")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(f"{item_name} — {item['price']}₸", reply_markup=reply_markup)

# Показ каталога через callback (для кнопки "Назад")
async def show_catalog_callback(query):
    for item_name, item in products.items():
        keyboard = [
            [InlineKeyboardButton("🛒 Купить", callback_data=f"buy_{item_name}")],
            [InlineKeyboardButton("ℹ️ Подробнее", callback_data=f"info_{item_name}")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(f"{item_name} — {item['price']}₸", reply_markup=reply_markup)

# Обработка inline-кнопок
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id

    if data.startswith("buy_"):
        item_name = data.replace("buy_", "")
        if user_id not in cart:
            cart[user_id] = []
        cart[user_id].append(item_name)
        await query.edit_message_text(f"✅ {item_name} добавлен в корзину. Напишите 🛒 Корзина для оформления заказа.")

    elif data.startswith("info_"):
        item_name = data.replace("info_", "")
        item = products[item_name]
        # Кнопки остаются
        keyboard = [
            [InlineKeyboardButton("🛒 Купить", callback_data=f"buy_{item_name}")],
            [InlineKeyboardButton("ℹ️ Подробнее", callback_data=f"info_{item_name}")],
            [InlineKeyboardButton("↩️ Назад", callback_data="back_to_catalog")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(f"{item_name} — {item['price']}₸\n{item['description']}", reply_markup=reply_markup)

    elif data == "back_to_catalog":
        await show_catalog_callback(query)

# Показ корзины и оформление заказа
async def show_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in cart or not cart[user_id]:
        await update.message.reply_text("🛒 Ваша корзина пуста.", reply_markup=menu_markup)
        return

    text = "🛒 Ваша корзина:\n"
    total = 0
    for item_name in cart[user_id]:
        price = products[item_name]["price"]
        text += f"- {item_name} — {price}₸\n"
        total += price
    text += f"💰 Итого: {total}₸\n\nВыберите дату доставки (YYYY-MM-DD):"
    await update.message.reply_text(text)

# Обработка текстовых сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    user_id = update.message.from_user.id

    if text.lower() == "📚 каталог":
        await show_catalog(update, context)
    elif text.lower() == "🔍 поиск":
        await update.message.reply_text("Напишите название товара, чтобы узнать цену и доставку.", reply_markup=menu_markup)
    elif text.lower() == "🛒 корзина":
        await show_cart(update, context)
    elif text.lower() == "ℹ️ помощь / контакты":
        await update.message.reply_text("Связь с менеджером: +7 777 777 77 77 📞", reply_markup=menu_markup)
    else:
        # Проверка на дату доставки
        try:
            delivery_date = datetime.datetime.strptime(text, "%Y-%m-%d").date()
            if check_holiday(delivery_date):
                note = " ⚠️ В этот день праздник, доставка может задержаться."
            else:
                note = ""
            cart_items = ", ".join(cart.get(user_id, []))
            await update.message.reply_text(f"Спасибо! Вы заказали: {cart_items}\nДоставка назначена на {delivery_date}{note}")
            cart[user_id] = []  # очищаем корзину после заказа
        except ValueError:
            await update.message.reply_text("Выберите действие с меню или напишите название товара.", reply_markup=menu_markup)

# Запуск бота
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.add_handler(CallbackQueryHandler(button))

print("Бот запущен...")
app.run_polling()