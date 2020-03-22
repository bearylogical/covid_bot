import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler
from sqlalchemy.orm import sessionmaker
from res.models import db_connect, create_table, Person
# State definitions for top level conversation
SELECTING_ACTION, ADDING_SELF, SELECTING_LANGUAGE,  EDIT_PROFILE = map(chr, range(4))
# State definitions for second level conversation
SELECTING_TRANSLATION_PROFILE, SELECTING_ROLE = map(chr, range(5, 7))

END = ConversationHandler.END

# Different constants for this example
LANGUAGE, ROLE, SELF, NAME, START_OVER, CURRENT_LEVEL, TRANSLATOR, READER = map(chr, range(8, 16))

# Meta states
STOPPING, SHOWING = map(chr, range(17, 19))

logger = logging.getLogger(__name__)

languages = ['bengali', 'hindi', 'tagalog']

engine = db_connect()
Session = sessionmaker(bind=engine)


#

def help(update, context):
    update.message.reply_text("Use /start to test this bot.")


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def start(update, context):
    """Choose to add languages"""
    text = 'Please choose your language'

    buttons = [[
        InlineKeyboardButton(text=language.capitalize(), callback_data=str(language)) for language in languages
    ], [
        InlineKeyboardButton(text='Back', callback_data=str(END))
    ]]

    keyboard = InlineKeyboardMarkup(buttons)
    if context.user_data.get(START_OVER):
        update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    else:
        update.message.reply_text(text=text, reply_markup=keyboard)

    # tell ConversationHandler we are in state SELECT LANGUAGE now
    return SELECTING_LANGUAGE


def select_role(update, context):
    """Choose to add a parent or a child."""
    query = update.callback_query
    bot = context.bot
    context.user_data['language'] = query.data
    text = f'You have chosen : {query.data} \n Define your role: Translator or Reader?'
    buttons = [[
        InlineKeyboardButton(text='Translator', callback_data='translator'),
        InlineKeyboardButton(text='Reader', callback_data='reader')
    ], [
        InlineKeyboardButton(text='Back', callback_data=str(END))
    ]]
    reply_markup = InlineKeyboardMarkup(buttons)
    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text=text,
        reply_markup=reply_markup
    )

    return SELECTING_LANGUAGE


def save_data(update, context):
    session = Session()
    person = Person()
    bot = context.bot
    query = update.callback_query
    context.user_data['role'] = query.data

    person.telegram_id = query.from_user['id']
    person.chat_id = query.message.chat_id
    person.first_name = query.from_user['username']
    person.role = context.user_data['role']
    person.language = context.user_data['language']


    exist_person = session.query(Person).filter_by(id=person.telegram_id).first()

    if exist_person is None:
        try:
            session.add(person)
            session.commit()
            logger.info('Person added')
            bot.edit_message_text(
                chat_id=query.message.chat_id,
                message_id=query.message.message_id,
                text="Information Saved"
            )
        except:
            session.rollback()
            raise

        finally:
            session.close()

    return END


def end(update, context):
    """End conversation from InlineKeyboardButton."""
    text = 'See you around!'
    update.callback_query.edit_message_text(text=text)

    return END

def stop(update, context):
    """End Conversation by command."""
    update.message.reply_text('Okay, bye.')

    return END