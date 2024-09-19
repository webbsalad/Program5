import functools

def fib_elem_gen():
    """Генератор, возвращающий элементы ряда Фибоначчи"""
    a = 0
    b = 1

    while True:
        yield a
        res = a + b
        a = b
        b = res

# Пример с генератором
g = fib_elem_gen()

while True:
    el = next(g)
    print(el)
    if el > 10:
        break

# Сопрограмма для вычисления чисел Фибоначчи
def my_genn():
    """Сопрограмма"""
    while True:
        number_of_fib_elem = yield
        a, b = 0, 1
        l = [str(number_of_fib_elem) + ":"]  # Чтобы сохранять результаты
        for _ in range(number_of_fib_elem):
            l.append(a)
            a, b = b, a + b
        yield l

# Декоратор для сопрограммы
def fib_coroutine(g):
    @functools.wraps(g)
    def inner(*args, **kwargs):
        gen = g(*args, **kwargs)
        gen.send(None)  # "Подготовка" сопрограммы
        return gen
    return inner

# Применяем декоратор
my_genn = fib_coroutine(my_genn)
gen = my_genn()

# Отправляем число, и получаем результат
print(gen.send(3))  # Вернет первые 5 чисел Фибоначчи
