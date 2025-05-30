import math

def attack_of_big_and_small_steps(y: int, a: int, ss: int) -> int:
    s = math.ceil(math.sqrt(ss))

    small_steps = []
    for i in range(s):
        small_steps.append((y, i))  # Запоминаем значение y и соответствующий индекс i
        y = (y * a) % ss  # Вычисляем следующее значение y по модулю ss
    # Сортируем список малых шагов по значению y (первый элемент кортежа)
    small_steps.sort(key=lambda x: x[0])

    big_steps = []
    for i in range(1, s+1):
        result = pow(a, i * s, ss)  # Вычисляем a^(i*s) mod ss
        big_steps.append((result, i * s))  # Сохраняем результат и индекс
    # Сортируем список больших шагов по значению результата
    big_steps.sort(key=lambda x: x[0])

    # Поиск совпадения между малыми и большими шагами
    found = False
    x = None
    for i in range(s):
        for j in range(s):
            if small_steps[i][0] == big_steps[j][0]:  # Если найдено совпадение
                x = abs(small_steps[i][1] - big_steps[j][1])
                found = True
                break
        if found:
            break

    return x  # Возвращаем найденное значение x
