import numpy as np
from constants import Pi, reverse_Pi, l_vec


def str_to_bytes(text: str) -> np.ndarray:
    """Преобразует строку в массив байтов"""
    return np.frombuffer(text.encode('utf-8'), dtype=np.uint8)

def bytes_to_str(byte_arr: np.ndarray) -> str:
    """Преобразует массив байтов обратно в строку"""
    return byte_arr.tobytes().decode('utf-8', errors='ignore')

def hex_to_bytes(hex_str):
    """Функция для преобразования hex-строки в массив байт"""
    return np.array([int(hex_str[i:i+2], 16) for i in range(0, len(hex_str), 2)], dtype=np.uint8)

def bytes_to_hex(byte_arr):
    """Функция для преобразования массива байт в hex-строку"""
    return ''.join(f'{x:02x}' for x in byte_arr)

def pad_message(message: np.ndarray) -> np.ndarray:
    """Добавляет паддинг к сообщению"""
    # Рассчитываем количество байтов, которые нужно добавить, чтобы длина сообщения стала кратной 16
    padding_length = 16 - (len(message) % 16)
    # Создаем массив байтов паддинга, каждый из которых содержит значение длины паддинга
    padding = np.full(padding_length, padding_length, dtype=np.uint8)
    return np.concatenate((message, padding))

def unpad_message(padded_message: np.ndarray) -> np.ndarray:
    """Удаляет паддинг после расшифрования"""
    padding_length = int(padded_message[-1])  # Последний байт указывает длину паддинга
    return padded_message[:-padding_length]  # Убираем паддинг

def operation_x(a: np.ndarray, b: np.ndarray):
    return np.bitwise_xor(a, b)

def operation_s(m: np.ndarray):
    res = np.zeros(16, dtype=np.uint8)
    for i in range(16):
        res[i] = Pi[m[i]]
    return res

def operation_s_inv(m: np.ndarray) -> np.ndarray:
    res = np.zeros(16, dtype=np.uint8)
    for i in range(16):
        res[i] = reverse_Pi[m[i]]
    return res

def gf_mult(a: np.uint8, b: np.uint8) -> np.uint8:
    """
    Выполняет умножение двух элементов в поле Галуа GF(2^8) с неприводимым полиномом x^8 + x^7 + x^6 + x + 1 (0xC3).
    """
    c = np.uint8(0)  # Итоговый результат умножения
    for i in range(8):  # Цикл выполняется 8 раз, так как умножаем байты (8 бит)
        if b & 1:  # Если младший бит b равен 1, выполняем XOR с a
            c ^= a
        hi_bit = a & 0x80  # Проверяем старший бит a (если он 1, нужен XOR с 0xC3)
        a = (a << 1) & 0xFF  # Сдвигаем a влево на 1 бит и обрезаем до 8 бит
        if hi_bit:  # Если старший бит был 1, выполняем XOR с 0xC3 (полином)
            a ^= 0xC3
        b >>= 1  # Сдвигаем b вправо, убирая уже обработанный бит
    return np.uint8(c)

def operation_r(m: np.ndarray):
    """
    Выполняет R-преобразование: циклический сдвиг влево на 1 байт + умножение каждого байта на соответствующий коэффициент l_vec.

    :param m: Входной 16-байтовый блок.
    :return: 16-байтовый блок после R-преобразования.
    """
    res_byte = np.uint8(0)  # Аккумулятор для XOR всех произведений
    res = np.zeros(16, dtype=np.uint8)  # Выходной массив (результат преобразования)

    # Циклический сдвиг влево: байт i переходит на позицию i-1 (кроме последнего)
    for i in range(15, -1, -1):
        if i != 0:
            res[i - 1] = m[i]  # Сдвигаем байты влево

        # Выполняем умножение i-го байта на коэффициент из l_vec и XOR-им в res_byte
        res_byte ^= gf_mult(m[i], l_vec[i])

    res[15] = res_byte  # Последний байт заменяем на res_byte

    return res

def operation_r_inv(m: np.ndarray):
    """
    Выполняет обратное R-преобразование: циклический сдвиг вправо на 1 байт + обратное умножение.
    """
    a_0 = m[15]  # Последний байт становится первым (используется в XOR)
    res = np.zeros(16, dtype=np.uint8)  # Выходной массив

    # Циклический сдвиг вправо: байт i переходит на позицию i+1 (кроме первого)
    for i in range(16):
        if i != 15:
            res[i + 1] = m[i]  # Сдвигаем байты вправо

        # XOR-им результат умножения каждого байта на коэффициент l_vec[i]
        a_0 ^= gf_mult(res[i], l_vec[i])

    res[0] = a_0  # Первый байт заменяем на итоговое значение

    return res

def operation_l(m: np.ndarray) -> np.ndarray:
    for i in range(16):
        m = operation_r(m)
    return m

def operation_l_inv(m: np.ndarray) -> np.ndarray:
    for i in range(16):
        m = operation_r_inv(m)
    return m

def generate_constants():
    C = []
    for i in range(32):
        ci = np.zeros(16, dtype=np.uint8)  # 128-битный блок (16 байт)
        ci[0] = i + 1  # Первый байт содержит номер итерации
        C.append(operation_l(ci))  # Применяем L-преобразование
    return C

def operation_f(k1: np.ndarray, k2: np.ndarray, c: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    temp = operation_x(k1, c)  # X(K1, C_i)
    temp = operation_s(temp)  # S-преобразование
    temp = operation_l(temp)  # L-преобразование
    new_k1 = operation_x(temp, k2)  # X(L(S(X(K1, C_i))), K2)
    return new_k1, k1  # Возвращаем новые K1 и K2

def expand_keys(master_key: np.ndarray):
    """ Развертывание ключей по ГОСТ 34.12-2018 (Кузнечик) """

    # Разделение мастер-ключа на K1 и K2
    k1, k2 = master_key[16:], master_key[:16]

    # Генерация 32 констант C
    C = generate_constants()

    # Итерационные ключи (первые два — это K1, K2)
    round_keys = [k1, k2]

    # Развертывание по 4 блока (8 операций F на каждую группу)
    for i in range(4):
        for j in range(8):
            k1, k2 = operation_f(k1, k2, C[i * 8 + j])

        # После 8 итераций сохраняем пару ключей
        round_keys.append(k1)
        round_keys.append(k2)

    return round_keys

def encrypt_block(m: np.ndarray, round_keys: list[np.ndarray]) -> np.ndarray:
    """
    Зашифровывает 128-битный блок (16 байт) с использованием развернутых ключей.

    :param m: Входной блок данных (массив из 16 байт).
    :param round_keys: Список из 10 раундовых ключей (по 16 байт каждый).
    :return: Зашифрованный блок (массив из 16 байт).
    """
    for i in range(9):
        m = operation_x(round_keys[i], m)  # XOR блока с ключом
        m = operation_s(m)  # S-преобразование (байтовая подстановка)
        m = operation_l(m)  # L-преобразование (линейное преобразование)

    # 10-й раунд: только XOR с последним ключом
    return operation_x(m, round_keys[9])

def decrypt_block(ciphertext: np.ndarray, round_keys: list[np.ndarray]) -> np.ndarray:
    """
    Расшифровывает 128-битный блок (16 байт) с использованием развернутых ключей.

    :param ciphertext: Входной зашифрованный блок (массив из 16 байт).
    :param round_keys: Список из 10 раундовых ключей (по 16 байт каждый).
    :return: Расшифрованный блок (массив из 16 байт).
    """
    # Первый шаг: XOR с последним раундовым ключом
    m = operation_x(ciphertext, round_keys[9])

    # Обратные 9 раундов шифрования
    for i in range(8, -1, -1):
        m = operation_l_inv(m)  # Обратное L-преобразование
        m = operation_s_inv(m)  # Обратное S-преобразование
        m = operation_x(round_keys[i], m)  # XOR с раундовым ключом

    return m

def encrypt_cbc(message: str, master_key_hex: str, iv_hex: str) -> str:
    """
    Зашифровывает строку в режиме сцепления блоков (CBC).

    :param message: Обычный текст для шифрования.
    :param master_key_hex: Ключ шифрования (32-байтовая hex-строка).
    :param iv_hex: Вектор инициализации (16-байтовая hex-строка).
    :return: Зашифрованный текст в hex-формате.
    """
    # Конвертируем мастер-ключ из hex в массив байтов
    master_key = hex_to_bytes(master_key_hex)

    # Разворачиваем мастер-ключ в 10 раундовых ключей
    round_keys = expand_keys(master_key)

    # Преобразуем текст в массив байтов и дополняем его до кратности 16 байтам
    message = bytes_to_hex(str_to_bytes(message))  # Преобразуем текст в hex
    message = hex_to_bytes(message)  # Переводим hex в байты
    message = pad_message(message)  # Дополняем до 16 байт

    # Конвертируем вектор инициализации (IV) из hex в байты
    iv = hex_to_bytes(iv_hex)

    # Разбиваем сообщение на блоки по 16 байт
    blocks = [message[i:i + 16] for i in range(0, len(message), 16)]
    encrypted_blocks = []
    prev_block = iv  # Инициализируем первый блок IV

    # Шифруем каждый блок с учетом предыдущего (режим CBC)
    for block in blocks:
        block = operation_x(block, prev_block)  # XOR текущего блока с предыдущим
        encrypted_block = encrypt_block(block, round_keys)  # Шифруем блок
        encrypted_blocks.append(encrypted_block)  # Добавляем в список
        prev_block = encrypted_block  # Обновляем prev_block для следующего цикла

    # Конвертируем зашифрованные блоки в hex-строку и объединяем
    return ''.join(bytes_to_hex(b) for b in encrypted_blocks)

def decrypt_cbc(ciphertext_hex: str, master_key_hex: str, iv_hex: str) -> str:
    """
    Расшифровывает строку в режиме сцепления блоков (CBC).

    :param ciphertext_hex: Зашифрованный текст в hex-формате.
    :param master_key_hex: Ключ шифрования (32-байтовая hex-строка).
    :param iv_hex: Вектор инициализации (16-байтовая hex-строка).
    :return: Расшифрованный текст.
    """
    # Конвертируем ключ из hex в байты и разворачиваем раундовые ключи
    master_key = hex_to_bytes(master_key_hex)
    round_keys = expand_keys(master_key)

    # Конвертируем зашифрованный текст и IV из hex в массив байтов
    ciphertext = hex_to_bytes(ciphertext_hex)
    iv = hex_to_bytes(iv_hex)

    # Разбиваем зашифрованное сообщение на блоки по 16 байт
    blocks = [ciphertext[i:i + 16] for i in range(0, len(ciphertext), 16)]
    decrypted_blocks = []
    prev_block = iv  # Первый блок — это IV

    # Расшифровываем каждый блок
    for block in blocks:
        decrypted_block = decrypt_block(block, round_keys)  # Расшифровываем блок
        decrypted_block = operation_x(decrypted_block,
                                      prev_block)  # XOR с предыдущим блоком (IV или предыдущим шифроблоком)
        decrypted_blocks.append(decrypted_block)  # Добавляем в список
        prev_block = block  # Текущий зашифрованный блок становится prev_block

    # Объединяем расшифрованные блоки в один массив
    decrypted_message = np.concatenate(decrypted_blocks)

    # Убираем дополнение (padding) и конвертируем обратно в текст
    result = bytes_to_hex(unpad_message(decrypted_message))  # Убираем padding
    result = bytes_to_str(hex_to_bytes(result))  # Конвертируем из hex в строку

    return result