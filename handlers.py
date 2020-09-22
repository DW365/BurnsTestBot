import datetime
import traceback

from dateutil.relativedelta import relativedelta
from dynaconf import settings
from loguru import logger
# noinspection PyPackageRequirements
from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler, Filters, CallbackContext

from messages import TestMessage, MainKBMessage, WelcomeMessage, StatsMessage, InfoMessage, SettingsMessage, \
    ResultMessage, InterpretationMessage
from models import User, Base, TestResult
from utils import get_random_food_emoji


# noinspection PyUnusedLocal
class Handlers:
    @staticmethod
    def dispatch(update, context):
        if update.effective_user.id == settings.ADMIN_ID:
            for user in User.all():
                try:
                    context.bot.send_message(user.id, text=update.message.text_html[10:], parse_mode='html')
                    user.bot_active = True
                except:
                    user.bot_active = False
            Base.session.commit()

    @staticmethod
    def close(update, context):
        update.callback_query.message.delete()

    @staticmethod
    def interpretation(update, context):
        update.callback_query.edit_message_text(text=update.callback_query.message.text_html, parse_mode='html')
        update.callback_query.message.reply_text(**InterpretationMessage())

    @staticmethod
    def start_test(update, context):
        context.user_data['answers'] = []
        message = update.message.reply_text(**TestMessage(0))
        context.user_data['active_test_message_id'] = message.message_id

    @staticmethod
    def get_stats(update, context):
        if update.message:
            now = datetime.datetime.utcnow() + datetime.timedelta(hours=3)
            from_time = now.date().replace(day=1)
            from_time = datetime.datetime(from_time.year, from_time.month, from_time.day)
            to_time = now
        else:
            month, year = update.callback_query.data.split('_')[-2:]
            from_time = datetime.datetime(int(year), int(month), 1)
            to_time = from_time + relativedelta(months=1, days=-1)
        items = TestResult.where(
            user_id=update.effective_user.id,
            created_on__ge=from_time,
            created_on__le=to_time,
        ).all()
        answer = StatsMessage(from_time, items)
        if update.message:
            update.message.reply_text(**answer)
        else:
            update.callback_query.edit_message_text(**answer)

    @staticmethod
    def process_answer(update, context):
        if update.callback_query.message.message_id != context.user_data.get('active_test_message_id'):
            update.callback_query.answer('Опрос неактивен т.к. был создан более новый')
            return
        context.user_data['answers'].append(int(update.callback_query.data.split('_')[-1]))
        if len(context.user_data['answers']) < 25:
            update.callback_query.edit_message_text(**TestMessage(len(context.user_data['answers'])))
        else:
            result = sum(context.user_data['answers'])
            status = None
            if 0 <= result <= 5:
                status = 'депрессия отсутствует'
            if 6 <= result <= 10:
                status = 'нормальное, но несчастливое состояние'
            if 11 <= result <= 25:
                status = 'слабо выраженная депрессия'
            if 26 <= result <= 50:
                status = 'умеренная депрессия'
            if 51 <= result <= 75:
                status = 'сильно выраженная депрессия'
            if 76 <= result <= 100:
                status = 'крайняя степень депрессии'
            update.callback_query.edit_message_text(**ResultMessage(result))
            TestResult.create(value=result, user_id=update.effective_user.id, data=context.user_data['answers'])
            Base.session.commit()

    @staticmethod
    def error(update, context):
        logger.warning('Update "%s" caused error "%s"', update, context.error)
        logger.error(traceback.format_exc())

    @staticmethod
    def start(update, context):
        user = User.find(update.effective_user.id)
        if not user:
            User.create(id=update.effective_user.id,
                        login=update.effective_user.username,
                        name=update.effective_user.full_name)
        update.message.reply_text(**WelcomeMessage())
        Base.session.commit()

    @staticmethod
    def info(update, context):
        update.message.reply_text(**InfoMessage())

    @staticmethod
    def settings(update, context):
        user = User.find(update.effective_user.id)
        if update.callback_query:
            if 'settings_period_set_' in update.callback_query.data:
                option = update.callback_query.data.split('_')[-1]
                user.last_notified = datetime.datetime.utcnow().date()
                user.notification_period = None if option == 'off' else int(option)
                Base.session.commit()
            if 'settings_time_digit_' in update.callback_query.data:
                option = update.callback_query.data.split('_')[-1]
                context.user_data['active_digit'] = int(option)
            if 'settings_export' in update.callback_query.data:
                update.callback_query.answer("Скоро будет")
            if 'settings_time' in update.callback_query.data:
                action, digit = update.callback_query.data.split('_')[-2:]
                t = datetime.datetime.now().replace(hour=user.notification_time.hour,
                                                    minute=user.notification_time.minute,
                                                    second=0, microsecond=0)
                delta = None
                if digit == '0':
                    delta = datetime.timedelta(hours=10)
                if digit == '1':
                    delta = datetime.timedelta(hours=1)
                if digit == '2':
                    delta = datetime.timedelta(minutes=10)
                if digit == '3':
                    delta = datetime.timedelta(minutes=1)

                if action == 'add':
                    t += delta
                else:
                    t -= delta
                user.notification_time = t.time()
                Base.session.commit()
        answer = SettingsMessage(user, context.user_data.get('active_digit'))
        if update.message:
            update.message.reply_text(**answer)
        else:
            # noinspection PyBroadException
            try:
                update.callback_query.edit_message_text(**answer)
            except:
                pass

    @staticmethod
    def placeholder(update, context):
        update.callback_query.answer(get_random_food_emoji())

    @staticmethod
    def send_reminds(context: CallbackContext):
        from messages import NotifyMessage
        now = datetime.datetime.utcnow() + datetime.timedelta(hours=3)
        for user in User.where(
                notification_period__isnull=False,
                notification_time__between=[(now - datetime.timedelta(minutes=5)).time(),
                                            now.time()]
        ).all():
            if (datetime.datetime.utcnow().date() - user.last_notified).days >= user.notification_period:
                context.bot.send_message(user.id, **NotifyMessage())
                user.last_notified = datetime.datetime.utcnow().date()
                Base.session.commit()

    @staticmethod
    def register(dp):
        dp.add_handler(CommandHandler('start', Handlers.start))
        dp.add_handler(CommandHandler('dispatch', Handlers.dispatch))
        dp.add_handler(MessageHandler(Filters.regex(MainKBMessage.markup.keyboard[0][0]), Handlers.start_test))
        dp.add_handler(MessageHandler(Filters.regex(MainKBMessage.markup.keyboard[1][0]), Handlers.get_stats))
        dp.add_handler(MessageHandler(Filters.regex(MainKBMessage.markup.keyboard[1][1]), Handlers.settings))
        dp.add_handler(MessageHandler(Filters.regex(MainKBMessage.markup.keyboard[1][2]), Handlers.info))
        dp.add_handler(CallbackQueryHandler(Handlers.process_answer, pattern='answer_.*'))
        dp.add_handler(CallbackQueryHandler(Handlers.get_stats, pattern='get_stats_.*'))
        dp.add_handler(CallbackQueryHandler(Handlers.close, pattern='close'))
        dp.add_handler(CallbackQueryHandler(Handlers.settings, pattern='settings_.*'))
        dp.add_handler(CallbackQueryHandler(Handlers.placeholder, pattern='placeholder'))
        dp.add_handler(CallbackQueryHandler(Handlers.interpretation, pattern='interpretation'))
        dp.add_error_handler(Handlers.error)
