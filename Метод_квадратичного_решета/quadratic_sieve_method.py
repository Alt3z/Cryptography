import sympy
import numpy as np
from itertools import combinations

def find_factor_base(N, bound):
    """
    Создает факторную базу — список малых простых чисел,
    для которых символ Лежандра (N/p) равен 1.
    """
    return [p for p in sympy.primerange(3, bound) if sympy.legendre_symbol(N, p) == 1]

def quadratic_sieve(N, initial_bound=30, max_attempts=10):
    """
    Реализует метод квадратичного решета для разложения числа N на множители.
    """
    bound = initial_bound  # Начальное значение границы факторной базы
    attempts = 0  # Счетчик попыток увеличения bound

    while attempts < max_attempts:
        factor_base = find_factor_base(N, bound)  # Находим факторную базу
        if len(factor_base) < 2:  # Если слишком мало чисел в базе — увеличиваем границу
            bound *= 2
            attempts += 1
            continue  # Пробуем снова

        x_values = []  # Список значений x
        factorization_matrix = []  # Матрица факторизации
        for x in range(int(N ** 0.5) + 1, int(N ** 0.5) + bound * 2):  # Перебираем x начиная с sqrt(N)
            Qx = x ** 2 - N  # Вычисляем Q(x) = x^2 - N
            factorization = [0] * len(factor_base)  # Массив степеней разложения
            num = Qx  # Копируем значение Q(x)
            for i, p in enumerate(factor_base):  # Перебираем простые числа факторной базы
                while num % p == 0:  # Пока число делится на p без остатка
                    num //= p  # Делим число
                    factorization[i] += 1  # Увеличиваем степень

            if num == 1:  # Если после разложения осталось 1, значит число B-гладкое
                x_values.append(x)  # Сохраняем x
                factorization_matrix.append([exp % 2 for exp in factorization])  # Записываем степени по модулю 2

            if len(x_values) > len(factor_base):  # Если набрали достаточно B-гладких чисел, прекращаем
                break

        if len(x_values) <= len(factor_base):  # Если не хватает чисел, увеличиваем bound
            bound *= 2
            attempts += 1
            continue

        matrix = np.array(factorization_matrix)  # Преобразуем список в массив NumPy
        null_space = find_null_space(matrix)  # Ищем ненулевое подпространство (линейные зависимости)

        for combination in null_space:  # Перебираем найденные комбинации
            x_prod = 1  # Перемноженные x
            y_prod = 1  # Перемноженные значения Q(x)
            for idx in combination:
                x_prod *= x_values[idx]  # Перемножаем x из найденных комбинаций
                y_prod *= x_values[idx] ** 2 - N  # Перемножаем Q(x)
            y_prod = int(y_prod ** 0.5)  # Берем корень из произведения Q(x)
            factor = sympy.gcd(x_prod - y_prod, N)  # Вычисляем наибольший общий делитель
            if 1 < factor < N:  # Если нашли нетривиальный делитель
                return factor, N // factor  # Возвращаем пару множителей

        bound *= 2  # Если не получилось разложить, увеличиваем bound
        attempts += 1

    return None  # Если после max_attempts попыток ничего не нашли

def find_null_space(matrix):
    """
    Находит ненулевые строки в ядре матрицы (нулевое пространство).
    """
    matrix = np.array(matrix)  # Преобразуем список в массив NumPy
    _, _, vh = np.linalg.svd(matrix, full_matrices=True)  # Разложение SVD
    null_mask = np.abs(vh[-1]) > 1e-10  # Определяем ненулевые элементы
    null_space_indices = np.where(null_mask)[0]  # Индексы ненулевых строк
    return [list(comb) for comb in combinations(null_space_indices, 2)]  # Создаем комбинации индексов