import random
from enum import Enum


class MonthName(Enum):
    JAN = "Январь"
    FEB = "Февраль"
    MAR = "Март"
    APR = "Апрель"
    MAY = "Май"
    JUN = "Июнь"
    JUL = "Июль"
    AUG = "Август"
    SEP = "Сентябрь"
    OCT = "Октябрь"
    NOV = "Ноябрь"
    DEC = "Декабрь"


def get_random_food_emoji():
    return random.choice('🍏🍎🍐🍊🍋🍌🍉🍇🍓🍈🍒🍑🥭🍍🥥🥝🍅🍆🥑🌶🌽🥕🥐🍰🧁🍧🍨🍦🥧🥮🍕🥙🧆🌮🌯🍔🍟🌭🧀🥨🥖🍞')
