
def send_message(bot_token: str, chat_id: str, msg: str):
    """Simple sending telegram message via pyTelegramBotAPI

    Args:
        bot_token (str): _description_
        chat_id (str): _description_
        msg (str): _description_

    Returns:
        _type_: _description_
    """
    import telebot

    bot = telebot.TeleBot(bot_token)
    return bot.send_message(chat_id, msg)
