import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from util.configs import read_configs, create_updater
from telegram.ext import CommandHandler, MessageHandler, ConversationHandler, CallbackQueryHandler, Updater, \
    CallbackContext
from telegram.ext import messagequeue as mq
from telegram.ext.filters import Filters
from sqlalchemy.orm import sessionmaker
from res.models import db_connect, create_table, Person, Message, AuthKeys
from util.languages import language_dict
from util.helpers import gen_code
import telegram.bot
from datetime import datetime

# init logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(funcName)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

# State definitions for top level conversation
SELECT_LANGUAGE, SEND_TRANSLATION, CHANGE_LANGUAGE, TRANSLATION_SENT, REGISTER_TRANSLATOR = map(chr, range(5))

END = ConversationHandler.END

# Meta states
STOPPING, SHOWING = map(chr, range(6, 8))

engine = db_connect()
Session = sessionmaker(bind=engine)


class MQBot(telegram.bot.Bot):

    def __init__(self, *args, is_queued_def=True, mqueue=None, **kwargs):
        super(MQBot, self).__init__(*args, **kwargs)
        self._is_messages_queued_default = is_queued_def
        self._msg_queue = mqueue or mq.MessageQueue()

    def __del__(self):
        try:
            self._msg_queue.stop()
        except:
            pass
        super(MQBot, self).__del__()

    @mq.queuedmessage
    def send_message(self, *args, **kwargs):
        return super(MQBot, self).send_message(*args, **kwargs)

    def help(update, context):
        update.message.reply_text("Use /start to test this bot.")


def error(bot, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

    return


def start(bot, context):
    text = 'Select Language:\n\n'
    selection_text = "\n".join(v['prompt_text'] for v in language_dict.values())

    bot.send_message(chat_id=context.effective_chat.id, text=text + selection_text)

    return SELECT_LANGUAGE


def register_translator_start(bot, context):
    text = 'Enter code'

    bot.send_message(chat_id=context.effective_chat.id, text=text)

    return REGISTER_TRANSLATOR


def register_translator(bot, context):
    session = Session()

    exist_code = session.query(AuthKeys).filter_by(code=context.message.text).first()

    if exist_code and exist_code.used_on is None:
        exist_code.used_by = context.effective_chat.id
        exist_code.used_on = datetime.now()
        exist_person = session.query(Person).filter_by(chat_id=context.effective_chat.id).first()
        if exist_person:
            exist_person.role = 'translator'
            try:
                session.add(exist_person)
                session.add(exist_code)
                session.commit()
                logger.info(f'{exist_code.code} used by {exist_person.chat_id}')
                bot.send_message(chat_id=context.effective_chat.id,
                                 text=f'You have successfully registered as a {exist_person.language} translator')
            except:
                session.rollback()
                bot.send_message(chat_id=context.effective_chat.id, text='Error, please try again')
                raise Exception('Error occured during saving')
            finally:
                session.close()
    else:
        bot.send_message(chat_id=context.effective_chat.id,
                         text=f'Unknown Code / Code has been used')

    return END


def translator_start(bot, context):
    session = Session()
    user = context.message.from_user

    exist_person = session.query(Person).filter_by(chat_id=user.id).first()
    if exist_person and exist_person.role == 'translator':
        bot.send_message(chat_id=context.effective_chat.id, text='Prease enter translation')
    else:
        bot.send_message(chat_id=context.effective_chat.id, text='Unauthorized')

    return SEND_TRANSLATION

def broadcast_message(message, language, bot):
    session = Session()

    readers = session.query(Person).filter_by(language=language)

    for reader in readers:
        bot.send_message(chat_id=reader.chat_id, text=message)



def send_translation(bot, context):
    session = Session()
    user = context.message.from_user

    exist_person = session.query(Person).filter_by(chat_id=user.id).first()
    if exist_person.role == 'translator':
        message = Message()
        message.message = context.message.text
        message.language = exist_person.language
        message.message_type = 'translation'

        try:
            session.add(message)
            session.commit()
            logger.info(f'Translation sending by {user.id} in {exist_person.language}')
            broadcast_message(message.message, message.language, bot)
        except:
            session.rollback()
            bot.send_message(chat_id=context.effective_chat.id, text='Error, try again')
            raise Exception('Error occured during saving')

        finally:
            session.close()
    else:
        bot.send_message(chat_id=context.effective_chat.id, text='Not Authorized')

    return END

# #TODO : functionality for changing preferences


def change_language_data(bot, context):
    session = Session()


def save_language_data(bot, context):
    session = Session()
    person = Person()

    person.chat_id = context.effective_chat.id
    person.role = 'reader'
    person.language = language_dict[int(context.message.text)]['language']

    exist_person = session.query(Person).filter_by(chat_id=person.chat_id).first()

    if exist_person is None:
        try:
            session.add(person)
            session.commit()
            logger.info('Person added')
            bot.message.reply_text('Information Saved')
        except:
            session.rollback()
            bot.send_message(chat_id=context.effective_chat.id, text='Error, please try again')
            raise Exception('Error occured during saving')

        finally:
            session.close()
    else:
        bot.send_message(chat_id=context.effective_chat.id, text='User already registered')

    return END


def cancel(bot, context):
    user = context.message.from_user
    logger.info("User %s canceled the conversation.", user.id)
    bot.send_message(chat_id=context.effective_chat.id, text='Thank you!')

    return END


def end(bot, context):
    """End conversation from InlineKeyboardButton."""

    return bot.send_message(chat_id=context.effective_chat.id, text='end')


def unknown(bot, context):
    bot.send_message(chat_id=context.effective_chat.id, text="Sorry, I didn't understand that command.")


def gen_translator_code(bot, context):
    authkeys = AuthKeys()

    user = context.message.from_user
    authkeys.created_by = user.id
    authkeys.code = gen_code()

    session = Session()

    try:
        session.add(authkeys)
        session.commit()
        logger.info('Person added')
        bot.send_message(chat_id=context.effective_chat.id, text=f'Use Key : {authkeys.code}')

    except:
        session.rollback()
        bot.send_message(chat_id=context.effective_chat.id, text='Error, please try again')
        raise Exception('Error occured during saving')


    finally:
        session.close()

    return END


#
# def stop(update, context):
#     """End Conversation by command."""
#
#     return update.message.reply_text('Okay, bye.')


def main():
    from telegram.utils.request import Request

    configs = read_configs('config.yml')
    token = configs['telegram']['token']

    q = mq.MessageQueue(all_burst_limit=3, all_time_limit_ms=3000)
    request = Request(con_pool_size=8)
    bot = MQBot(token=token, request=request, mqueue=q)
    updater = telegram.ext.updater.Updater(bot=bot)
    dp = updater.dispatcher
    # add handlers
    # Set up second level ConversationHandler (adding a person)

    basic_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            SELECT_LANGUAGE: [MessageHandler(Filters.text, save_language_data)],
            CHANGE_LANGUAGE: [MessageHandler(Filters.text, change_language_data)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    translator_handler = ConversationHandler(
        entry_points=[CommandHandler('translate', translator_start)],
        states={
            SEND_TRANSLATION: [MessageHandler(Filters.text, send_translation)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    upgrade_user_hander = ConversationHandler(
        entry_points=[CommandHandler('register', register_translator_start)],
        states={
            REGISTER_TRANSLATOR: [MessageHandler(Filters.text, register_translator)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    unknown_handler = MessageHandler(Filters.command, unknown)

    dp.add_handler(CommandHandler('gen_code', gen_translator_code))
    # dp.add_handler(CommandHandler('register_translator',register_translator))
    # dp.add_handler(Filters.user, translation_broadcast)
    dp.add_handler(basic_handler)

    dp.add_handler(translator_handler)
    # dp.add_handler(translator_handler)
    dp.add_handler(upgrade_user_hander)
    dp.add_handler(unknown_handler)
    dp.add_error_handler(error)
    # start the bot
    updater.start_polling()


if __name__ == "__main__":
    main()
