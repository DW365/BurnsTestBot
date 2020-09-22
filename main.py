from dynaconf import settings
from telegram.ext import Updater

from handlers import Handlers
from models import connect_to_db

updater = Updater(settings.BOT_TOKEN, use_context=True)
job_queue = updater.job_queue

connect_to_db()
Handlers.register(updater.dispatcher)
job_queue.run_repeating(Handlers.send_reminds, interval=60, first=0)
updater.start_polling()
updater.idle()
