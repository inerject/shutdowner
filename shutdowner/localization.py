from enum import IntEnum


class Lang(IntEnum):
    EN = 0
    UA = 1
    RU = 2


_COLLECTION = {
    "lang": ["English", "Українська", "Русский"],
    "hh": ["hh", "гг", "чч"],
    "mm": ["mm", "хх", "мм"],
    "ss": ["ss", "сс", "сс"],
    "Power off": ["Power off", "Відключення", "Выключение"],
    "Hibernate": ["Hibernate", "Гібернація", "Гибернация"],
    "Restart": ["Restart", "Рестарт", "Рестарт"],
    "Only int values!":
        ["Only int values!", "Тільки цілі числа!", "Только целые числа!"],
    "Enter time!": ["Enter time!", "Введіть час!", "Введите время!"],
    "Start": ["Start", "Старт", "Старт"],
    "Stop": ["Stop", "Стоп", "Стоп"],
}


class Str:
    @staticmethod
    def set_curr_lang(lang_id: Lang):
        if lang_id not in Lang:
            raise ValueError()
        Str._curr_lang = lang_id

    @staticmethod
    def get_curr_lang() -> Lang:
        return Str._curr_lang

    @staticmethod
    def get(key):
        if key in _COLLECTION:
            return _COLLECTION[key][Str._curr_lang]
        return key

    _curr_lang = Lang.UA
