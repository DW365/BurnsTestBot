import datetime
from typing import List

from dateutil.relativedelta import relativedelta
from dynaconf import settings
from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, Message
from tqdm import tqdm

from models import TestResult
from questions import QUESTIONS, get_paragraph
from utils import MonthName, get_random_food_emoji


class MainKBMessage(dict):
    markup = ReplyKeyboardMarkup([['📝 Пройти тест'], ['📊 Динамика', '⚙️ Настройки', 'ℹ️ Инфо']],
                                 resize_keyboard=True)

    def __init__(self, text):
        super().__init__(text=text, reply_markup=self.markup, parse_mode='html')


class StatsMessage(dict):
    @staticmethod
    def format_item(item: TestResult, max_value: int = 100):
        bar = tqdm.format_meter(item.value, max_value, 0, ncols=20, bar_format='{bar}')
        return f"<b>{item.created_on + datetime.timedelta(hours=3):%d}</b><code>|{item.value:<3}{bar}</code>\n"

    def __init__(self, date: datetime.date, items: List[TestResult] = None):
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton('⬅️', callback_data=f"get_stats_{date - relativedelta(months=1):%m_%Y}"),
             InlineKeyboardButton('➡️', callback_data=f"get_stats_{date + relativedelta(months=1):%m_%Y}")],
            [InlineKeyboardButton('❌ Закрыть', callback_data='close')]
        ])
        month_name = list(MonthName.__members__.values())[date.month - 1].value
        message = f"{get_random_food_emoji()} <b>{month_name} {date.year}</b>\n\n"
        if items:
            max_value = max([i.value for i in items])
            for item in items:
                message += StatsMessage.format_item(item, max_value=max_value)
        else:
            message += "В этом месяце пока нет записей"
        super().__init__(text=message, parse_mode='html', reply_markup=markup)


class SettingsMessage(dict):
    def __init__(self, user, active_digit=None):
        def is_active(value):
            return "✅ " if user.notification_period == value else "☑️ "

        def get_time_digit(i):
            digit = user.notification_time.strftime("%H%M")[i]
            if active_digit == i:
                return f"[ {digit} ]"
            else:
                return digit

        markup = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton('📆 Периодичность напоминания', callback_data='placeholder')],
                [InlineKeyboardButton(f'{is_active(1)}1 день',
                                      callback_data='settings_period_set_1'),
                 InlineKeyboardButton(f'{is_active(3)}3 дня', callback_data='settings_period_set_3'),
                 InlineKeyboardButton(f'{is_active(7)}7 дней', callback_data='settings_period_set_7'),
                 InlineKeyboardButton(f'{is_active(None)}Откл.', callback_data='settings_period_set_off')],
                [InlineKeyboardButton('⏰ Время для напоминания', callback_data='placeholder')],

                [InlineKeyboardButton('🔼', callback_data='settings_time_add_0'),
                 InlineKeyboardButton('🔼', callback_data='settings_time_add_1'),
                 InlineKeyboardButton('∙', callback_data='placeholder'),
                 InlineKeyboardButton('🔼', callback_data='settings_time_add_2'),
                 InlineKeyboardButton('🔼', callback_data='settings_time_add_3')],
                [InlineKeyboardButton(get_time_digit(0), callback_data='placeholder'),
                 InlineKeyboardButton(get_time_digit(1), callback_data='placeholder'),
                 InlineKeyboardButton(':', callback_data='placeholder'),
                 InlineKeyboardButton(get_time_digit(2), callback_data='placeholder'),
                 InlineKeyboardButton(get_time_digit(3), callback_data='placeholder')],
                [InlineKeyboardButton('🔽', callback_data='settings_time_sub_0'),
                 InlineKeyboardButton('🔽', callback_data='settings_time_sub_1'),
                 InlineKeyboardButton('∙', callback_data='placeholder'),
                 InlineKeyboardButton('🔽', callback_data='settings_time_sub_2'),
                 InlineKeyboardButton('🔽', callback_data='settings_time_sub_3')],
                [InlineKeyboardButton('💾 Экспорт результатов', callback_data='settings_export')],
                [InlineKeyboardButton('❌ Закрыть', callback_data='close')]
            ]
        )
        super().__init__(text='∙', reply_markup=markup)


class TestMessage(dict):
    def __init__(self, question_number):
        markup = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton('🙅‍♂️ Ни разу', callback_data='answer_0')],
                [InlineKeyboardButton('🙍‍♂️ Иногда', callback_data='answer_1')],
                [InlineKeyboardButton('💁‍♂️ Умеренно', callback_data='answer_2')],
                [InlineKeyboardButton('🤷‍♂️ Часто', callback_data='answer_3')],
                [InlineKeyboardButton('🙇‍♂️ Крайне часто', callback_data='answer_4')],
                [InlineKeyboardButton('❌ Отмена', callback_data='close')]
            ]
        )
        super().__init__(
            text=f"<code>[{question_number + 1}/25]</code> <b>{get_paragraph(question_number)}</b>\n\n{QUESTIONS[question_number]}",
            reply_markup=markup, parse_mode='html')


class WelcomeMessage(MainKBMessage):
    def __init__(self):
        super().__init__(settings.WELCOME_MSG)


class InfoMessage(MainKBMessage):
    def __init__(self):
        super().__init__(settings.INFO_MSG)


class NotifyMessage(MainKBMessage):
    def __init__(self):
        super().__init__(settings.NOTIFY_MSG)
