import numpy as np
from constants import Pi, Tau, A, C


def GOSTHashX(a: np.ndarray, b: np.ndarray, c: np.ndarray) -> None:
    """
    Выполняет побитовый XOR для массивов a и b, результат записывается в c
    """
    np.bitwise_xor(a, b, out=c)


def GOSTHashAdd512(a, b, c)-> None:
    """
    Выполняет побитовое сложение двух массивов байтов размером 64 байта
    по модулю 512, результат записывается в c
    """

    # Переменная для учёта переноса
    internal = 0

    # Проходим по байтам в обратном порядке
    for i in range(63, -1, -1):
        # Сложение с учётом переноса
        internal = int(a[i]) + int(b[i]) + (internal >> 8)
        c[i] = internal & 0xFF  # Сохраняем только младшие 8 бит (результат сложения)


def GOSTHashS(state: np.ndarray) -> None:
    """
    Преобразует состояние с использованием таблицы Pi
    """
    # Создаем массив для промежуточного состояния
    internal = np.zeros(64, dtype=np.uint8)

    # Преобразуем состояние с использованием Pi
    for i in range(63, -1, -1):
        internal[i] = Pi[state[i]]

    # Копируем результат обратно в state
    np.copyto(state, internal)


def GOSTHashP(state: np.ndarray) -> None:
    """
    Преобразует состояние с использованием таблицы Tau
    """
    # Создаем временный массив для промежуточного состояния
    internal = np.zeros(64, dtype=np.uint8)

    # Выполняем перестановку состояния, используя Tau
    for i in range(63, -1, -1):
        internal[i] = state[Tau[i]]

    # Копируем результат обратно в state
    np.copyto(state, internal)


def GOSTHashL(state: np.ndarray) -> None:
    """
    Преобразует состояние с использованием матрицы A
    """
    # Делим исходный вектор на части по восемь байт
    internal_in = np.zeros(8, dtype=np.uint64)
    for i in range(8):
        # Берем срез из 8 байтов и преобразуем в 64-битное число
        internal_in[i] = int.from_bytes(state[i * 8:(i + 1) * 8], byteorder='big')

    internal_out = np.zeros(8, dtype=np.uint64)  # Инициализация массива для результата

    # Проходим по частям и выполняем операцию с побитовым сдвигом
    for i in range(7, -1, -1):
        # Если очередной бит равен 1, то XOR с соответствующим значением из A
        for j in range(63, -1, -1):
            if (internal_in[i] >> j) & 1:  # Проводим сдвиг на 64 бита
                internal_out[i] ^= A[63 - j]

    # Копируем результат обратно в state
    byte_idx = 0
    for value in internal_out:
        bytes_value = int(value).to_bytes(8, byteorder='big')
        state[byte_idx:byte_idx+8] = np.frombuffer(bytes_value, dtype=np.uint8)
        byte_idx += 8


class TGOSTHashContext:
    def __init__(self, hash_size: int):
        # Буфер для очередного блока хэшируемого сообщения
        self.buffer = np.zeros(64, dtype=np.uint8)

        # Итоговый результат вычислений
        self.hash = np.zeros(64, dtype=np.uint8)

        # Промежуточный результат вычислений
        self.h = np.zeros(64, dtype=np.uint8)

        # Прочие векторы
        self.N = np.zeros(64, dtype=np.uint8)
        self.Sigma = np.zeros(64, dtype=np.uint8)  # Контрольная сумма
        self.v_0 = np.zeros(64, dtype=np.uint8)  # Вектор инициализации
        self.v_512 = np.zeros(64, dtype=np.uint8)  # Вектор инициализации

        # Размер оставшейся части сообщения
        self.buf_size = 0

        # Размер хеш-суммы (512 или 256 бит)
        self.hash_size = hash_size


def GOSTHashGetKey(K: np.ndarray, i: int) -> None:
    """
    Применяет последовательность операций хеширования к ключу K
    """
    #hex_string = ''.join([format(x, '02x') for x in K])
    #print(f"K: {hex_string}")
    # Выполняем серию операций с ключом K
    GOSTHashX(K, C[i], K)
    #hex_string = ''.join([format(x, '02x') for x in C[i]])
    #print(f"C[i]: {hex_string}")
    #hex_string = ''.join([format(x, '02x') for x in K])
    #print(f"K^C: {hex_string}")

    GOSTHashS(K)
    #hex_string = ''.join([format(x, '02x') for x in K])
    #print(f"S(K^C): {hex_string}")

    GOSTHashP(K)
    #hex_string = ''.join([format(x, '02x') for x in K])
    #print(f"PS(K^C): {hex_string}")

    GOSTHashL(K)
    #hex_string = ''.join([format(x, '02x') for x in K])
    #print(f"LPS(K^C): {hex_string}")


def GOSTHashE(K: np.ndarray, m: np.ndarray, state: np.ndarray) -> None:
    """
    Выполняет хеширование по алгоритму с 12 раундами
    """
    # Первоначальное XOR между m и K, результат в state
    GOSTHashX(m, K, state)
    #hex_string = ''.join([format(x, '02x') for x in state])
    #print(f"X: {hex_string}")

    for i in range(12):
        # Применение преобразований S, P и L
        GOSTHashS(state)
        #hex_string = ''.join([format(x, '02x') for x in state])
        #print(f"SX: {hex_string}")

        GOSTHashP(state)
        #hex_string = ''.join([format(x, '02x') for x in state])
        #print(f"PSX: {hex_string}")

        GOSTHashL(state)
        #hex_string = ''.join([format(x, '02x') for x in state])
        #print(f"LPSX: {hex_string}")

        # Получаем новый ключ K для раунда
        GOSTHashGetKey(K, i)

        # XOR состояния с новым ключом K
        GOSTHashX(state, K, state)

        #print(f"Итерация {i+1} закончена\n")


def GOSTHashG(h: np.ndarray, N: np.ndarray, m: np.ndarray) -> None:
    """
    Выполняет хеширование по алгоритму, используя хеш, N и сообщение m
    """
    # Промежуточный массив K для хранения результата XOR
    K = np.zeros(64, dtype=np.uint8)
    internal = np.zeros(64, dtype=np.uint8)  # Промежуточный массив для результата

    # XOR между N и h, результат сохраняем в K
    GOSTHashX(N, h, K)

    # Применяем преобразования S, P, L к K
    GOSTHashS(K)
    GOSTHashP(K)
    GOSTHashL(K)

    ############################################
    # для первого примера ожидается b383fc2eced4a574b383fc2eced4a574b383fc2eced4a574b383fc2eced4a574b383fc2eced4a574b383fc2eced4a574b383fc2eced4a574b383fc2eced4a574.
    #hex_string = ''.join([format(x, '02x') for x in K])
    #print(f"LPS: {hex_string}")
    ############################################

    # Применяем GOSTHashE к K и m, результат сохраняем в internal
    GOSTHashE(K, m, internal)

    # XOR между internal и h, результат сохраняем в internal
    GOSTHashX(internal, h, internal)

    # XOR между internal и m, результат сохраняем в h
    GOSTHashX(internal, m, h)
    #hex_string = ''.join([format(x, '02x') for x in h])
    #print(f"Конец E: {hex_string}\n\n\n")


def GOSTHashPadding(CTX: TGOSTHashContext) -> None:
    """
    Функция добавляет паддинг в буфер.
    В начале массива добавляются нули, затем добавляется 0x01,
    а затем в конец записываются данные из буфера.
    """
    # Промежуточный массив размером 64 байта
    internal = np.zeros(64, dtype=np.uint8)

    # Количество свободных мест в начале массива
    padding_size = 64 - CTX.buf_size - 1

    # Добавляем 0x01 перед данными из буфера
    internal[padding_size] = 0x01

    # Копируем данные из буфера в конец массива
    internal[padding_size + 1: padding_size + 1 + CTX.buf_size] = CTX.buffer[:CTX.buf_size]

    # Копируем результат обратно в буфер
    CTX.buffer = internal

    #hex_string = ''.join([format(x, '02x') for x in internal])
    #print(f"После паддинга: {hex_string}")

def GOSTHashInit(CTX: TGOSTHashContext, hash_size: int) -> None:
    # Обнуляем все атрибуты контекста
    CTX.buffer.fill(0)
    CTX.hash.fill(0)
    CTX.h.fill(0)
    CTX.N.fill(0)
    CTX.Sigma.fill(0)
    CTX.v_0.fill(0)
    CTX.v_512.fill(0)

    # Если хеш 256 бит, то инициализируем CTX.h значением 0x01
    if hash_size == 256:
        CTX.h.fill(0x01)
    else:
        CTX.h.fill(0x00)

    # Устанавливаем размер хеша
    CTX.hash_size = hash_size

    # Инициализируем вектор v_512
    CTX.v_512[-2] = 0x02


def GOSTHashStage_2(CTX: TGOSTHashContext, data: np.ndarray) -> None:
    """
    Выполняет второй этап хеширования
    """
    GOSTHashG(CTX.h, CTX.N, data)

    #hex_string = ''.join([format(x, '02x') for x in CTX.v_512])
    #print(f"CTX.v_512: {hex_string}")
    # Добавляем результат в N
    GOSTHashAdd512(CTX.N, CTX.v_512, CTX.N)
    #hex_string = ''.join([format(x, '02x') for x in CTX.N])
    #print(f"N: {hex_string}")

    # Добавляем данные в Sigma
    GOSTHashAdd512(CTX.Sigma, data, CTX.Sigma)
    #hex_string = ''.join([format(x, '02x') for x in CTX.Sigma])
    #print(f"Sigma: {hex_string}\n\n\n")


def GOSTHashStage_3(CTX: TGOSTHashContext) -> None:
    """
    Выполняет третий этап хеширования
    """
    # Инициализация промежуточного вектора
    internal = np.zeros(64, dtype=np.uint8)

    # Формируем строку с размером сообщения в битах
    internal[-2] = ((CTX.buf_size * 8) >> 8) & 0xff
    internal[-1] = (CTX.buf_size * 8) & 0xff

    # Дополняем оставшуюся часть до полных 64 байт
    GOSTHashPadding(CTX)

    GOSTHashG(CTX.h, CTX.N, CTX.buffer)

    # Формируем контрольную сумму сообщения
    GOSTHashAdd512(CTX.N, internal, CTX.N)
    #hex_string = ''.join([format(x, '02x') for x in CTX.N])
    #print(f"N: {hex_string}")

    #hex_string = ''.join([format(x, '02x') for x in CTX.Sigma])
    #print(f"Sigma до : {hex_string}")
    #hex_string = ''.join([format(x, '02x') for x in CTX.buffer])
    #print(f"Буфер: {hex_string}")

    GOSTHashAdd512(CTX.Sigma, CTX.buffer, CTX.Sigma)
    #hex_string = ''.join([format(x, '02x') for x in CTX.Sigma])
    #print(f"Sigma : {hex_string}")

    GOSTHashG(CTX.h, CTX.v_0, CTX.N)
    GOSTHashG(CTX.h, CTX.v_0, CTX.Sigma)

    # Записываем результат в хеш
    np.copyto(CTX.hash, CTX.h)


def GOSTHashUpdate(CTX: TGOSTHashContext, data: np.ndarray, length: int) -> None:
    """
    Обновляет хеш-состояние с использованием входных данных
    """

    # Обрабатываем данные, пока длина больше 63 байтов и буфер пуст
    while length > 63 and CTX.buf_size == 0:
        GOSTHashStage_2(CTX, data[-64:])
        data = data[:-64]  # Убираем обработанные последние 64 байта
        length -= 64

    # Обрабатываем оставшиеся данные
    while length > 0:
        chk_size = 64 - CTX.buf_size  # Сколько еще можно поместить в буфер
        if chk_size > length:
            chk_size = length

        # Дописываем данные в буфер
        CTX.buffer[CTX.buf_size:CTX.buf_size + chk_size] = data[:chk_size]
        CTX.buf_size += chk_size
        length -= chk_size
        data = data[chk_size:]

        # Если буфер заполнился, выполняем второй этап хеширования
        if CTX.buf_size == 64:
            GOSTHashStage_2(CTX, CTX.buffer)
            CTX.buf_size = 0


def GOSTHashFinal(CTX: TGOSTHashContext) -> None:
    """
    Завершает вычисление хеша, выполняя третий этап
    """
    GOSTHashStage_3(CTX)
    CTX.buf_size = 0


def Stribog(input_string: str, hash_size: int):
    input_string = np.array([int(input_string[i:i + 2], 16) for i in range(0, len(input_string), 2)], dtype=np.uint8)
    #hex_string = ''.join([format(x, '02x') for x in input_string])
    #print(f"До паддинга: {hex_string}")

    CTX = TGOSTHashContext(hash_size=hash_size)

    GOSTHashInit(CTX, hash_size=hash_size)
    GOSTHashUpdate(CTX, input_string, len(input_string))
    GOSTHashFinal(CTX)

    if hash_size == 256:
        CTX.hash = CTX.hash[:32]

    return CTX.hash


def cheak_hash(hash_hex:str, expected_hash: str) -> bool:
    if (hash_hex == expected_hash):
        return True
    return False


C = np.array(C, dtype=np.uint8)
C  = np.flip(C , axis=1)


#################################       Первый пример       #################################
print(f"\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tПЕРВЫЙ ПРИМЕР")

input_string = ("323130393837363534333231303938373635343332313039383736353433323"
                "130393837363534333231303938373635343332313039383736353433323130")
print(f"Входные данные:      {input_string}\n")

hash_result = Stribog(input_string, 512)
hash_hex = ''.join(format(byte, '02x') for byte in hash_result)
expected_hash = ("486f64c1917879417fef082b3381a4e211c324f074654c38823a7b76f830ad00"
                 "fa1fbae42b1285c0352f227524bc9ab16254288dd6863dccd5b9f54a1ad0541b")
print(f"Хэш-512:             {hash_hex}")
print(f"Должен был быть:     {expected_hash}")
print(f"Совпадение: {cheak_hash(hash_hex, expected_hash)}\n")

hash_result = Stribog(input_string, 256)
hash_hex = ''.join(format(byte, '02x') for byte in hash_result)
expected_hash = "00557be5e584fd52a449b16b0251d05d27f94ab76cbaa6da890b59d8ef1e159d"
print(f"Хэш-256:             {hash_hex}")
print(f"Должен был быть:     {expected_hash}")
print(f"Совпадение: {cheak_hash(hash_hex, expected_hash)}\n")
#################################           Конец           #################################


#################################       Второй пример       #################################
print(f"\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tВТОРОЙ ПРИМЕР")

input_string = ("fbe2e5f0eee3c820fbeafaebef20fffbf0e1e0f0f520e0ed20e8ece0ebe5f0f2f120fff0eeec2"
                "0f120faf2fee5e2202ce8f6f3ede220e8e6eee1e8f0f2d1202ce8f0f2e5e220e5d1")
print(f"Входные данные:      {input_string}\n")

hash_result = Stribog(input_string, 512)
hash_hex = ''.join(format(byte, '02x') for byte in hash_result)
expected_hash = ("28fbc9bada033b1460642bdcddb90c3fb3e56c497ccd0f62b8a2ad4935e85f03"
                 "7613966de4ee00531ae60f3b5a47f8dae06915d5f2f194996fcabf2622e6881e")
print(f"Хэш-512:             {hash_hex}")
print(f"Должен был быть:     {expected_hash}")
print(f"Совпадение: {cheak_hash(hash_hex, expected_hash)}\n")

hash_result = Stribog(input_string, 256)
hash_hex = ''.join(format(byte, '02x') for byte in hash_result)
expected_hash = "508f7e553c06501d749a66fc28c6cac0b005746d97537fa85d9e40904efed29d"
print(f"Хэш-256:             {hash_hex}")
print(f"Должен был быть:     {expected_hash}")
print(f"Совпадение: {cheak_hash(hash_hex, expected_hash)}\n")
#################################           Конец           #################################
