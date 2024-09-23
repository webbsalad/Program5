class FibonacchiLst:
    def __init__(self, lst):
        """Инициализация списка и генерация чисел Фибоначчи до максимального элемента списка"""
        self.lst = lst
        self.fib_set = self._generate_fib_set(max(lst))

    def _generate_fib_set(self, max_value):
        # Генерация множества чисел Фибоначчи до максимального значения
        a, b = 0, 1
        fib_set = {a, b}
        while b <= max_value:
            a, b = b, a + b
            fib_set.add(b)
        return fib_set

    def __iter__(self):
        # Возвращаем итератор для перебора списка
        self.idx = 0
        return self

    def __next__(self):
        #Возвращаем следующий элемент из списка, если он принадлежит ряду Фибоначчи
        while self.idx < len(self.lst):
            value = self.lst[self.idx]
            self.idx += 1
            if value in self.fib_set:
                return value
        raise StopIteration

if __name__ == "__main__":
    lst = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 1]
    fib_iterator = FibonacchiLst(lst)

    print(list(fib_iterator))  
