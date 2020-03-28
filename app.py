import logging
from util.configs import read_configs
from telegram.ext import CommandHandler, Updater
from telegram.ext import messagequeue as mq
from handlers.main_handlers import gen_translator_code, basic_handler, translator_handler, upgrade_user_hander, \
    unknown_handler, error

# init logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(funcName)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

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


def main():
    from telegram.utils.request import Request

    configs = read_configs('config.yml')
    token = configs['telegram']['token']

    q = mq.MessageQueue(all_burst_limit=3, all_time_limit_ms=3000)
    request = Request(con_pool_size=8)
    bot = MQBot(token=token, request=request, mqueue=q)
    updater = Updater(bot=bot)
    dp = updater.dispatcher
    # add handlers
    # Set up second level ConversationHandler (adding a person)

    dp.add_handler(CommandHandler('gen_code', gen_translator_code))
    dp.add_handler(CommandHandler('register_translator',register_translator))
    dp.add_handler(Filters.user, translation_broadcast)
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
