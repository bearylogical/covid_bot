import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler
from sqlalchemy.orm import sessionmaker
from res.models import db_connect, create_table, Person
from util.languages import language_dict


# Meta states
STOPPING, SHOWING = map(chr, range(17, 19))

logger = logging.getLogger(__name__)


engine = db_connect()
Session = sessionmaker(bind=engine)


#

def help(update, context):
    update.message.reply_text("Use /start to test this bot.")


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def start(update, context):
    text='Select Language:\n\n'
    selection_text = "\n".join(v['prompt_text'] for v in language_dict.values())

    context.bot.send_message(chat_id=update.effective_chat.id, text=text+selection_text)

#
# def select_role(update, context):
#     """Choose to add a parent or a child."""
#     query = update.callback_query
#     bot = context.bot
#     context.user_data['language'] = query.data
#     text = f'You have chosen : {query.data} \n Define your role: Translator or Reader?'
#     buttons = [[
#         InlineKeyboardButton(text='Translator', callback_data='translator'),
#         InlineKeyboardButton(text='Reader', callback_data='reader')
#     ], [
#         InlineKeyboardButton(text='Back', callback_data=str(END))
#     ]]
#     reply_markup = InlineKeyboardMarkup(buttons)
#     return bot.edit_message_text(
#         chat_id=query.message.chat_id,
#         message_id=query.message.message_id,
#         text=text,
#         reply_markup=reply_markup
#     )


#
#
# def save_data(update, context):
#     session = Session()
#     person = Person()
#     bot = context.bot
#     query = update.callback_query
#     context.user_data['role'] = query.data
#
#     person.telegram_id = query.from_user['id']
#     person.chat_id = query.message.chat_id
#     person.first_name = query.from_user['username']
#     person.role = context.user_data['role']
#     person.language = context.user_data['language']
#
#
#     exist_person = session.query(Person).filter_by(id=person.telegram_id).first()
#
#     if exist_person is None:
#         try:
#             session.add(person)
#             session.commit()
#             logger.info('Person added')
#             bot.edit_message_text(
#                 chat_id=query.message.chat_id,
#                 message_id=query.message.message_id,
#                 text="Information Saved"
#             )
#         except:
#             session.rollback()
#             raise
#
#         finally:
#             session.close()
#
#
#
#
# def end(update, context):
#     """End conversation from InlineKeyboardButton."""
#
#     return update.message.reply_text(text)
#
# def stop(update, context):
#     """End Conversation by command."""
#
#     return update.message.reply_text('Okay, bye.')
