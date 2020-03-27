from telegram.ext import BaseFilter
from telegram import InlineKeyboardButton, InlineKeyboardMarkup



def receive_translation(update, context):

    context.bot.send_message(chat_id=update.effective_chat.id, text="Gov.sg Message Received, sending to translators")

def send_translation(update, context):


    context.bot.send_message(chat_id=update.effective_chat.id, text="Gov.sg Message Received, sending to translators")

def translation_broadcast(update, context):

    pass

class FilterGovSG(BaseFilter):
    def filter(self, message):
        return '[Sent by Gov.sg' in message.text

