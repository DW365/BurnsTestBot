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
                [InlineKeyboardButton('🙅‍♂️ Совсем нет', callback_data='answer_0')],
                [InlineKeyboardButton('🙍‍♂️ Немного', callback_data='answer_1')],
                [InlineKeyboardButton('💁‍♂️ Умеренно', callback_data='answer_2')],
                [InlineKeyboardButton('🤷‍♂️ Сильно', callback_data='answer_3')],
                [InlineKeyboardButton('🙇‍♂️ Крайне', callback_data='answer_4')],
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


class ResultMessage(dict):
    def __init__(self, result):
        markup = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton('ℹ О результатах', callback_data='interpretation')],
            ]
        )
        super().__init__(text=f'<b>Вы набрали <code>{result}</code> баллов.</b>', parse_mode='html', reply_markup=markup)


class InterpretationMessage(dict):
    def __init__(self):
        markup = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton('❌ Закрыть', callback_data='close')],
            ]
        )
        super().__init__(text=f'❗️<b>Дисклеймер:</b>\n'
                              '\n'
                              'Данный тест не претендует на истину в последней инстанции. Скорее это инструмент для периодической самодиагностики (раз в 3-7 дней) и отслеживания динамики своего психологического состояния. Однако если вы на протяжении нескольких недель набираете высокий балл, то это может быть поводом для обращения к компетентному специалисту.\n'
                              'И да, текст интерпретации выглядит довольно &quot;продающим&quot;, но полагаю психологам надо на что-то жить. А у автора бота лапки 🐾 и ему было лень творчески переписать текст.\n'
                              '\n'
                              '<b>📚 Отрывок из книги &quot;Терапия настроения&quot; по интерпретации результата:</b>\n'
                              '\n'
                              '🔘 Если ваш балл от <b>0</b> до <b>5</b>, вы, вероятно, уже чувствуете себя хорошо. Этот балл находится в диапазоне нормального состояния, и большинство людей с оценкой такого низкого уровня чувствуют себя счастливыми и довольными.\n'
                              '\n'
                              '🔘 Если ваш балл в промежутке от <b>6</b> до <b>10</b>, ваше состояние все еще в пределах нормы, но вы можете ощущать некоторую нестабильность. В таком случае не помешает улучшение, небольшая психическая &quot;настройка&quot;. У всех возникают проблемы в повседневной жизни, и небольшое изменение взгляда на жизнь часто может сильно повлиять в лучшую сторону на то, как вы себя чувствуете.\n'
                              '\n'
                              '🔘 Если ваш балл между <b>11</b> и <b>25</b>, то ваша депрессия, по крайней мере в данный момент, протекает в легкой форме и не должна быть причиной для тревог. Вам определенно захочется улучшить свое состояние, и вы сможете добиться существенных успехов без посторонней помощи. Но, если ваша оценка остается в этом диапазоне несколько недель, следует задуматься о профессиональной помощи. Терапия или курс антидепрессантов может значительно ускорить выздоровление.\n'
                              '\n'
                              '<i>Некоторые из самых трудных для лечения депрессий я наблюдал у людей, чей балл не превышал диапазона &quot;слабо выраженной депрессии&quot;. Часто эти люди страдали от небольшой подавленности в течение многих лет, иногда на протяжении большей части своей жизни. Легкая хроническая депрессия, которая длится и длится, в настоящее время называется &quot;дистимическое расстройство&quot;. Этот на первый взгляд сложный термин имеет простой смысл. Он означает &quot;этот человек ужасно мрачен и негативен большую часть времени&quot;. Вы, наверное, знаете подобных людей, да и сами, возможно, попадали под темные чары пессимизма.</i>\n'
                              '\n'
                              '🔘 Если вы набрали от <b>26</b> до <b>50</b> по опроснику Бернса, это означает, что у вас депрессия умеренной тяжести. Но не обманывайтесь термином &quot;умеренный&quot;. Если ваш балл в данном диапазоне, вы можете испытывать довольно сильные страдания. Большинство из нас в какой-то момент могут чувствовать себя очень расстроенными, но обычно мы быстро выходим из этого состояния. Если ваша оценка остается в этом диапазоне более двух недель, вам необходима профессиональная помощь.\n'
                              '\n'
                              '🔘 Если ваш балл превышает <b>50</b>, это указывает на то, что ваша депрессия имеет сильную выраженность или даже достигает крайней степени тяжести. Настолько сильные страдания могут быть почти невыносимыми, особенно когда оценка выше 75. Ваше настроение постоянно причиняет неудобство и, возможно, представляет опасность, потому что чувство отчаяния и безнадежности может даже вызвать суицидальные побуждения.\n'
                              '\n'
                              'К счастью, прогноз выздоровления превосходный. На самом деле иногда пациенты с самыми тяжелыми депрессиями реагируют быстрее всего. Однако неразумно пытаться лечить тяжелую депрессию самостоятельно. Вам обязательно следует обратиться за профессиональной консультацией.',
                         parse_mode='html', reply_markup=markup)
