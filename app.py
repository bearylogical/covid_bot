import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from util.configs import read_configs, create_updater
from telegram.ext import CommandHandler, MessageHandler, ConversationHandler, CallbackQueryHandler
from handlers.govsg_handler import FilterGovSG
from handlers.main_handlers import start, help, error, end, select_role, stop, start, save_data
from telegram.ext.filters import Filters



# init logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(funcName)s - %(name)s - %(levelname)s - %(message)s')

# State definitions for top level conversation
SELECTING_ACTION, ADDING_SELF, SELECTING_LANGUAGE,  EDIT_PROFILE = map(chr, range(4))
# State definitions for second level conversation
SELECTING_TRANSLATION_PROFILE, SELECTING_ROLE = map(chr, range(5, 7))
languages = ['bengali', 'hindi', 'tagalog']
END = ConversationHandler.END

# Different constants for this example
LANGUAGE, ROLE, SELF, NAME, START_OVER, CURRENT_LEVEL, TRANSLATOR, READER = map(chr, range(8, 16))

# Meta states
STOPPING, SHOWING = map(chr, range(17, 19))


def main():
    configs = read_configs('config.yml')
    updater = create_updater(configs['telegram']['token'])

    dp = updater.dispatcher

    # add handlers
    # Set up second level ConversationHandler (adding a person)

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            SELECTING_LANGUAGE: [CallbackQueryHandler(select_role, pattern='^' + 'bengali|hindi|tagalog' + '$'),
                                 CallbackQueryHandler(save_data, pattern='^' + 'translator|reader' + '$'),
                                 CallbackQueryHandler(end, pattern='^' + str(END) + '$')
            ]
        },
        fallbacks=[CommandHandler('start', start)]
    )
    dp.add_handler(Filters.user, translation_broadcast)
    dp.add_handler(conv_handler)

    dp.add_error_handler(error)
    # start the bot
    updater.start_polling()


if __name__ == "__main__":
    main()