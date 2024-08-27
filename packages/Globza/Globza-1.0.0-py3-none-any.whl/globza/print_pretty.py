# print_pretty.py

import json


def print_pretty_json(data):
    """
    Функция для красивого вывода данных JSON в консоль.
    :param data: Словарь или список, который будет преобразован в форматированный JSON.
    """
    pretty_json = json.dumps(data, indent=4, ensure_ascii=False)
    print(pretty_json)
