import requests
from xml.etree import ElementTree as ET
from decimal import Decimal
import time
import json
import csv
import io


class Component:
    def get_currencies(self, currencies_ids_lst):
        pass


class CurrenciesList(Component):
    """
    Класс для получения списка валют с сайта ЦБ.
    Возвращает данные в виде словаря: {'Код валюты': {'name': 'Название валюты', 'rate': ('Часть целая', 'Часть дробная')}}
    """
    def __init__(self):
        self.__cur_lst = []
        self.timestamp = None

    def get_currencies(self, currencies_ids_lst):
        """
        Получает данные о валютах по указанным ID.
        Возвращает словарь с курсами валют.
        """
        self.timestamp = time.time()  # Запоминаем время запроса

        try:
            cur_res_str = requests.get('http://www.cbr.ru/scripts/XML_daily.asp')
            cur_res_str.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при запросе: {e}")
            return {}

        root = ET.fromstring(cur_res_str.content)
        valutes = root.findall("Valute")
        result = {}

        # Обработка валюты и формирование словаря
        for _v in valutes:
            valute_id = _v.get('ID')
            if valute_id in currencies_ids_lst:
                valute_name = _v.find('Name').text
                valute_value = _v.find('Value').text
                valute_charcode = _v.find('CharCode').text
                valute_nominal = int(_v.find('Nominal').text)
                rub_val = Decimal(valute_value.replace(',', '.')) / valute_nominal
                rub_val_tuple = (str(rub_val.quantize(Decimal('1'))), str(rub_val % 1)[2:])
                result[valute_charcode] = {'name': valute_name, 'rate': rub_val_tuple}

        return result


class Decorator(Component):
    """
    Базовый класс для декораторов. Делегирует работу компоненту, который он оборачивает.
    """
    def __init__(self, component: Component):
        self._component = component

    def get_currencies(self, currencies_ids_lst):
        return self._component.get_currencies(currencies_ids_lst)


class ConcreteDecoratorJSON(Decorator):
    """
    Конкретный декоратор, форматирующий данные в JSON.
    """
    def get_currencies(self, currencies_ids_lst):
        # Получаем данные от оборачиваемого компонента
        data = super().get_currencies(currencies_ids_lst)
        # Преобразуем данные в JSON-строку
        return json.dumps(data, indent=4, ensure_ascii=False)


class ConcreteDecoratorCSV(Decorator):
    """
    Конкретный декоратор, форматирующий данные в CSV.
    Может работать как со словарём, так и с JSON
    """
    def get_currencies(self, currencies_ids_lst):
        data = super().get_currencies(currencies_ids_lst)
        
        # Проверяем, является ли data строкой (JSON), и преобразуем её обратно в словарь
        if isinstance(data, str):
            data = json.loads(data)
        
        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow(["Currency Code", "Currency Name", "Rate"])
        
        for code, info in data.items():
            writer.writerow([code, info['name'], '.'.join(info['rate'])])

        output.seek(0)
        return output.getvalue()


def client_code(component: Component, currencies_ids_lst):
    """
    Функция, которая работает с любым компонентом, используя его метод get_currencies.
    """
    result = component.get_currencies(currencies_ids_lst)
    print("Результат:\n", result)


if __name__ == "__main__":
    # Базовая версия
    currencies = CurrenciesList()
    print("Базовый компонент:")
    client_code(currencies, ['R01035', 'R01335'])
    print("\n")

    # Применение JSON-декоратора
    json_decorator = ConcreteDecoratorJSON(currencies)
    print("Данные в формате JSON:")
    client_code(json_decorator, ['R01035', 'R01335'])
    print("\n")

    # Применение CSV-декоратора
    csv_decorator = ConcreteDecoratorCSV(currencies)
    print("Данные в формате CSV:")
    client_code(csv_decorator, ['R01035', 'R01335'])
    print("\n")

    # Применение декоратора CSV поверх JSON-декоратора
    json_csv_decorator = ConcreteDecoratorCSV(json_decorator)
    print("Данные в формате CSV после JSON-декоратора:")
    client_code(json_csv_decorator, ['R01035', 'R01335'])
