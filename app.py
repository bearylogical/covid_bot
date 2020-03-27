import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from util.configs import read_configs, create_updater
from telegram.ext import CommandHandler, MessageHandler, ConversationHandler, CallbackQueryHandler
from handlers.govsg_handler import FilterGovSG
from handlers.main_handlers import start, help, error
from telegram.ext.filters import Filters



# init logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(funcName)s - %(name)s - %(levelname)s - %(message)s')


def main():
    configs = read_configs('config.yml')
    updater = create_updater(configs['telegram']['token'])

    dp = updater.dispatcher

    start_handler = CommandHandler('start', start)
    # translator_handler = CommandHandler('translate', send_translation)
    dp.add_handler(start_handler)


    # dp.add_handler(Filters.user, translation_broadcast)


    dp.add_error_handler(error)
    # start the bot
    updater.start_polling()


if __name__ == "__main__":
    main()