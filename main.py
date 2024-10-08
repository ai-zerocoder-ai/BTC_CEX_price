import telebot
import datetime
import time
import threading
import random
import requests
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация бота с вашим токеном
bot = telebot.TeleBot('TELEGRAM_BOT_TOKEN')
@bot.message_handler(commands=['start'])
def start_message(message):
    bot.reply_to(message, 'Привет! Я чат-бот, который будет напоминать тебе курс BTC на CEX Bybit')
    reminder_thread = threading.Thread(target=send_reminders, args=(message.chat.id,), daemon=True)
    reminder_thread.start()

@bot.message_handler(commands=['fact'])
def fact_message(message):
    facts = [
        "Биткоин был запущен в 2009 году неизвестным разработчиком или группой под псевдонимом Сатоши Накамото.",
        "Биткоин работает на технологии блокчейн, которая обеспечивает децентрализованное управление без центрального органа.",
        "Общее количество биткоинов ограничено 21 миллионом монет, что делает его дефицитным активом."
    ]
    random_fact = random.choice(facts)
    bot.reply_to(message, f'Лови факт о BTC: {random_fact}')

def get_crypto_prices():
    url = 'https://api.bybit.com/v5/market/tickers'
    params = {'category': 'spot'}
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()  # Проверка на успешный ответ
        data = response.json()

        tickers = data.get('result', {}).get('list', [])
        prices = {}
        for ticker in tickers:
            symbol = ticker.get('symbol')
            if symbol == 'BTCUSDT':
                last_price = ticker.get('lastPrice')
                prices[symbol] = last_price

        return prices
    except requests.RequestException as e:
        logger.error(f'Ошибка при получении цен: {e}')
        return None

def send_reminders(chat_id):
    reminder_times = ["09:00", "14:00", "00:16"]
    while True:
        now = datetime.datetime.now().strftime("%H:%M")
        if now in reminder_times:
            prices = get_crypto_prices()
            if prices and 'BTCUSDT' in prices:
                price = prices['BTCUSDT']
                message = f"📈 Текущий курс BTC: {price} USDT"
            else:
                message = "❌ Не удалось получить курс BTC. Пожалуйста, попробуйте позже."

            bot.send_message(chat_id, message)
            # Ждем 61 секунду, чтобы избежать повторной отправки в ту же минуту
            time.sleep(61)
        else:
            # Проверяем каждую секунду
            time.sleep(1)

# Запуск бота
if __name__ == '__main__':
    bot.polling(none_stop=True)
