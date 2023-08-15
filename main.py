import logging
import telebot
from telebot import types

TOKEN = '6351474332:AAHJsqllMMyUBbQRmCP9tUUBAnm0Pa1oi3g'

products = {
    'item1': {'name': 'NEW BALANCE 530 БЕЛЫЕ С СИНИМ', 'price': 25, 'image_url': 'https://imgur.com/a/SGGdfHr'}
}

bot = telebot.TeleBot(TOKEN)

user_carts = {}

exchange_rate = 100

@bot.message_handler(commands=['start'])
def start(message):
    user_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    user_markup.add(types.KeyboardButton("Витрина"), types.KeyboardButton("Моя корзина"))
    bot.send_message(message.from_user.id, f"Добро пожаловать, {message.from_user.first_name}! Выберите пункт меню:", reply_markup=user_markup)


@bot.message_handler(func=lambda message: message.text == "Витрина")
def show_catalog(message):
    user_markup = types.InlineKeyboardMarkup(row_width=2)

    for item_id, item_info in products.items():
        price_rub = item_info['price'] * exchange_rate  # Переводим цену из долларов в рубли
        button = types.InlineKeyboardButton(f"{item_info['name']} ({price_rub} руб.)", callback_data=f'add_to_cart_{item_id}')
        user_markup.add(button)

    bot.send_message(message.from_user.id, "Выберите товар для добавления в корзину:", reply_markup=user_markup)

    for item_id, item_info in products.items():
        item_name = item_info['name']
        price_rub = item_info['price'] * exchange_rate
        item_image_url = item_info['image_url']
        bot.send_photo(message.chat.id, item_image_url, caption=f"{item_name} ({price_rub} руб.)", reply_markup=user_markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith('add_to_cart_'))
def add_to_cart(call):
    item_id = call.data.split('_')[3]
    user_id = call.from_user.id

    if item_id in products:
        user_carts.setdefault(user_id, {})
        user_carts[user_id].setdefault(item_id, 0)
        user_carts[user_id][item_id] += 1

        price_rub = products[item_id]['price'] * exchange_rate
        bot.send_message(user_id, f"Товар {products[item_id]['name']} добавлен в корзину. Теперь у вас {user_carts[user_id][item_id]} шт. (Цена: {price_rub} руб.)")


@bot.message_handler(func=lambda message: message.text == "Моя корзина")
def view_cart(message):
    user_id = message.from_user.id
    cart = user_carts.get(user_id, {})

    if not cart:
        bot.send_message(user_id, "Ваша корзина пуста.")
        return

    cart_text = ""
    total_price = 0

    for item_id, quantity in cart.items():
        item_name = products[item_id]['name']
        item_price = products[item_id]['price']
        total_item_price = item_price * exchange_rate * quantity  # Учитываем количество и переводим в рубли
        total_price += total_item_price
        cart_text += f"{item_name} - {quantity} шт. ({total_item_price} руб.)\n"

    cart_text += f"\nИтого: {total_price} руб."
    bot.send_message(user_id, f"Содержимое вашей корзины:\n{cart_text}")


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    bot.polling(none_stop=True)
