import requests
from xml.etree import ElementTree as ET
from time import time
from decimal import Decimal
import matplotlib.pyplot as plt

class CurrenciesLst:
    def __init__(self):
        # Инициализация класса CurrenciesLst
        self.__cur_lst = []  
        self.timestamp = None  

    def __del__(self):
        print("Объект удалён")  

    def get_currencies(self, currencies_ids_lst: list) -> list:
        """Получает данные о валютах по заданным ID."""
        self.timestamp = time()  
        print(f"Вызов get_currencies с ID: {currencies_ids_lst}")

        try:
            # Запрашиваем данные о курсах валют с сайта ЦБ
            cur_res_str = requests.get('http://www.cbr.ru/scripts/XML_daily.asp')
            cur_res_str.raise_for_status()  
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при запросе: {e}")  
            return []

        print("Данные получены от ЦБ.")  
        root = ET.fromstring(cur_res_str.content)  
        valutes = root.findall("Valute")  

        result = []  
        for _v in valutes:
            # Обрабатываем каждую валюту
            valute_id = _v.get('ID')  
            if valute_id in currencies_ids_lst:  
                valute_name = _v.find('Name').text  
                valute_value = _v.find('Value').text  
                valute_charcode = _v.find('CharCode').text  
                valute_nominal = int(_v.find('Nominal').text)  

                print(f"  Обработана валюта: {valute_charcode} - {valute_name} - {valute_value} (Номинал: {valute_nominal})")

                # Рассчитываем курс валюты по отношению к рублю
                rub_val = Decimal(valute_value.replace(',', '.')) / valute_nominal
                rub_val_tuple = (str(rub_val.quantize(Decimal('1'))), str(rub_val % 1)[2:])  

                # Создаем словарь с информацией о валюте
                valute = {valute_charcode: (valute_name, rub_val_tuple)}
                result.append(valute)  

        self.__cur_lst = result  
        print(f"  Результат: {result}")  
        return result  

    def get_valute(self, valute_id: str) -> dict:
        """Геттер для получения данных по конкретной валюте."""
        for valute in self.__cur_lst:
            if valute_id in valute:
                return {valute_id: valute[valute_id]}  
        return {valute_id: None}  

    def get_all_valutes(self) -> list:
        """Возвращает список всех валют."""
        return self.__cur_lst  

    def add_valute(self, valute_charcode: str, valute_name: str, valute_value: str):
        """Добавляет новую валюту в список."""
        rub_val = Decimal(valute_value.replace(',', '.'))  
        rub_val_tuple = (str(rub_val.quantize(Decimal('1'))), str(rub_val % 1)[2:])  
        new_valute = {valute_charcode: (valute_name, rub_val_tuple)}  
        self.__cur_lst.append(new_valute)  

    def visualize_currencies(self):
        """Визуализирует курсы валют на графике."""
        fig, ax = plt.subplots()  
        currencies = [list(val.keys())[0] for val in self.__cur_lst]  
        values = [float(val[list(val.keys())[0]][1][0] + '.' + val[list(val.keys())[0]][1][1]) for val in self.__cur_lst]

        ax.bar(currencies, values)  
        ax.set_ylabel('Курс к рублю')  
        ax.set_title('Курсы валют')  
        plt.savefig('currencies.jpg')  
        plt.show()  


def test_invalid_id():
    """Тест для проверки обработки некорректного ID валюты."""
    cl = CurrenciesLst()  
    result = cl.get_valute('R9999')  
    assert result == {'R9999': None}, "Неправильный ID не должен возвращать данные"  
    print("Тест на некорректный ID пройден успешно.")

def test_valid_ids():
    """Тест для проверки корректных ID валют."""
    cl = CurrenciesLst()  
    cl.get_currencies(['R01035', 'R01335'])  

    # Тест для R01035
    result1 = cl.get_valute('GBP')  
    assert result1 is not None, "Полученные данные по ID GBP должны быть не None"  
    assert 'Фунт стерлингов Соединенного королевства' in result1['GBP'][0], "Неверное название валюты для GBP"  
    assert 0 <= float(result1['GBP'][1][0] + '.' + result1['GBP'][1][1]) <= 999, "Курс GBP вне допустимого диапазона"  
    print("Тест для R01035 пройден успешно.")

    # Тест для R01335
    result2 = cl.get_valute('KZT')  
    assert result2 is not None, "Полученные данные по ID KZT должны быть не None"  
    assert 'Казахстанских тенге' in result2['KZT'][0], "Неверное название валюты для KZT"  
    assert 0 <= float(result2['KZT'][1][0] + '.' + result2['KZT'][1][1]) <= 999, "Курс KZT вне допустимого диапазона"  
    print("Тест для R01335 пройден успешно.")


if __name__ == '__main__':
    cl = CurrenciesLst()  
    print("Получаем курсы валют:")
    res = cl.get_currencies(['R01035', 'R01335', 'R01700J'])  
    if res:
        print("Курсы валют получены:\n", res)  

    print("\nПолучаем информацию по валюте R01035:")
    valute_info = cl.get_valute('GBP')  
    if valute_info['GBP'] is not None:
        print(f"  {valute_info['GBP'][0]}: {valute_info['GBP'][1][0]},{valute_info['GBP'][1][1]}")  
    else:
        print("  Информация по валюте не найдена.")

    print("\nДобавляем новую валюту:")
    cl.add_valute('USD', 'Доллар США', '98,7565')  
    new_valute_info = cl.get_valute('USD')  
    print(f"  {new_valute_info['USD'][0]}: {new_valute_info['USD'][1][0]},{new_valute_info['USD'][1][1]}")  

    print("\nВизуализируем курсы валют:")
    cl.visualize_currencies()  

    print("\nЗапуск тестов:")
    test_invalid_id()  
    test_valid_ids()  
