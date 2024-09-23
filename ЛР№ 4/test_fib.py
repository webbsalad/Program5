import pytest

# Функция, которая возвращает первые n элементов последовательности Фибоначчи
def fib(n):
    """Возвращает список первых n элементов последовательности Фибоначчи"""
    if n <= 0:
        return []
    elif n == 1:
        return [0]
    elif n == 2:
        return [0, 1]
    
    a, b = 0, 1
    result = [0, 1]
    for _ in range(2, n):
        a, b = b, a + b
        result.append(b)
    return result


# Тесты
def test_fib_1():
    """Тривиальный случай n = 1"""
    assert fib(1) == [0], "fib(1) должно быть [0]"

def test_fib_2():
    """Проверка fib(2)"""
    assert fib(2) == [0, 1], "fib(2) должно быть [0, 1]"

def test_fib_3():
    """Тест для случая n = 3"""
    assert fib(3) == [0, 1, 1], "fib(3) должно быть [0, 1, 1]"

def test_fib_5():
    """Тест для случая n = 5"""
    assert fib(5) == [0, 1, 1, 2, 3], "fib(5) должно быть [0, 1, 1, 2, 3]"

# Запуск тестов с помощью pytest
if __name__ == "__main__":
    pytest.main()
