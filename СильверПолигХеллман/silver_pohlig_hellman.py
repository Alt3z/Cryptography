from sympy import factorint, mod_inverse


def silver_pohlig_hellman(a, b, q):
    """
    Реализация алгоритма Сильвера-Полига-Хеллмана для вычисления дискретного логарифма.
    Данный алгоритм используется для вычисления x в уравнении a^x ≡ b (mod q),
    когда (q - 1) имеет малые простые множители.

    Параметры:
    a - основание логарифма
    b - результат возведения в степень
    q - модуль

    Возвращает:
    x - дискретный логарифм, то есть такое число, что a^x ≡ b (mod q)
    """

    # Разложение q - 1 на простые множители с их степенями
    # Например, если q - 1 = 180, то factorint(180) вернет {2: 2, 3: 2, 5: 1}
    factors = factorint(q - 1)

    # Вспомогательная функция для построения таблицы значений r_p,j = a^((q-1)/p) mod q
    def compute_table(a, p, q):
        """
        Создает таблицу степеней a по модулю q, необходимых для поиска j.
        Таблица заполняется по правилу:
        r_p,j = a^((q-1)/p) mod q
        """
        table = []  # Таблица значений
        power = pow(a, (q - 1) // p, q)  # Вычисляем a^((q-1)/p) mod q
        current = 1  # Начальное значение (a^0 = 1)

        for j in range(p):  # Заполняем таблицу значениями степеней a
            table.append(current)
            current = (current * power) % q  # Умножаем на a^((q-1)/p) и берем по модулю q

        return table

    # Списки для остатков и модулей в КТО
    residues = []  # Остатки x_i (вычисленные логарифмы по модулю p^e)
    moduli = []  # Модули p^e

    # Обрабатываем каждый простой множитель p и его степень e в разложении q - 1
    for p, e in factors.items():
        # Вычисляем таблицу значений r_p,j для данного p
        table = compute_table(a, p, q)

        pe = p ** e
        moduli.append(pe)

        bi = b  # Текущее значение b_i, оно будет обновляться
        xi = 0  # Текущее значение логарифма x_i
        pe_k = 1  # Значение p^k

        # Вычисляем x_i по модулю p^e
        for k in range(e):
            pe_k *= p  # Вычисляем p^k
            bi_mod_pe = pow(bi, (q - 1) // pe_k, q)

            # Находим j, такое что r_p,j = bi_mod_pe
            j = next((idx for idx, val in enumerate(table) if val == bi_mod_pe), None)

            if j is None:
                # Если b == 1, то x должно быть равно порядку a (q-1) / p^e
                if bi == 1:
                    xi = (q - 1) // pe
                    break
                return None

            xi += j * (p ** k)
            bi = (bi * mod_inverse(pow(a, j * (p ** k), q), q)) % q

        # Добавляем остаток в список
        residues.append(xi)

    # Решаем систему сравнений с помощью КТО
    def chinese_remainder_theorem(residues, moduli):
        """
        Реализует Китайскую теорему об остатках (КТО) для решения системы сравнений:
        x ≡ residues[i] (mod moduli[i]) для всех i.

        Возвращает:
        x - наименьшее положительное решение системы сравнений.
        """
        total = 0  # Итоговое значение x
        prod = 1  # Общее произведение всех модулей

        # Вычисляем общее произведение модулей
        for modulus in moduli:
            prod *= modulus

        # Вычисляем сумму x_i * M_i * M_i^-1
        for residue, modulus in zip(residues, moduli):
            p = prod // modulus  # M_i = prod / modulus
            total += residue * mod_inverse(p, modulus) * p

        return total % prod  # Получаем окончательный x по модулю произведения всех модулей

    return chinese_remainder_theorem(residues, moduli)  # Возвращаем найденный x