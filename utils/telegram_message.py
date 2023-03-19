import os

from dotenv import load_dotenv
from telegram import Bot

load_dotenv()


def send_message(orders: str) -> None:
    """
    Sends a notification message to a Telegram chat specified by
    the `CHAT_ID` environment variable.

    :param orders: A string containing the numbers of the orders
                   that have passed their delivery deadline.
    :return: None
    """
    bot = Bot(token=os.getenv('TELEGRAM_TOKEN'))
    chat_id = os.getenv('CHAT_ID')
    text = f'Прошел срок поставки заказа(ов) № {orders}'
    bot.send_message(chat_id, text)
