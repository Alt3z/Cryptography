from aes_constants import S_BOX, INV_S_BOX, RCON, Nk, Nb, Nr, mix_matrix, inv_mix_matrix


def sub_bytes(state):
    # Заменяет каждый байт состояния по таблице S-Box
    return [S_BOX[byte] for byte in state]


def shift_rows(state):
    # Выполняет циклический сдвиг строк в матрице состояния:
    # - 2-я строка сдвигается на 1 влево
    # - 3-я на 2
    # - 4-я на 3
    return [
        state[0], state[5], state[10], state[15], # строка 0 (без сдвига)
        state[4], state[9], state[14], state[3], # строка 1 (сдвиг на 1)
        state[8], state[13], state[2], state[7], # строка 2 (сдвиг на 2)
        state[12], state[1], state[6], state[11] # строка 3 (сдвиг на 3)
    ]


def galois_multiplication(byte_a, byte_b):
    # Умножение в поле Галуа GF(2^8) используется в MixColumns
    result = 0
    for _ in range(8):  # По каждому биту
        if byte_b & 1:  # Если младший бит b равен 1
            result ^= byte_a  # XOR byte_a в результат
        carry = byte_a & 0x80  # Проверка переполнения (старший бит)
        byte_a <<= 1  # Умножение на x (сдвиг влево)
        if carry:
            byte_a ^= 0x1b  # При переполнении применяем модуль (редуцируем по полиному AES)
        byte_b >>= 1  # Сдвигаем byte_b вправо
    return result & 0xFF  # Обрезаем до 1 байта (8 бит)


def mix_columns(state, mix_matrix):
    # Преобразует каждый столбец состояния, умножая его на матрицу mix_matrix
    mixed = [0] * 16  # Инициализируем выходной список
    for col in range(4):  # Проходим по каждому столбцу
        for row in range(4):  # Каждый элемент столбца
            # Вычисляем результат умножения и сложения в GF(2^8)
            mixed[col * 4 + row] = (
                galois_multiplication(state[col * 4 + 0], mix_matrix[row][0]) ^
                galois_multiplication(state[col * 4 + 1], mix_matrix[row][1]) ^
                galois_multiplication(state[col * 4 + 2], mix_matrix[row][2]) ^
                galois_multiplication(state[col * 4 + 3], mix_matrix[row][3])
            )
    return mixed


def add_round_key(state, round_key):
    # Применяет ключ раунда: XOR каждого байта состояния с байтом ключа
    return [s_byte ^ k_byte for s_byte, k_byte in zip(state, round_key)]


def key_expansion(cipher_key):
    key_bytes = list(cipher_key)  # Преобразуем ключ в список байтов

    # Начальное расширение: разбиваем ключ на 4 слова
    expanded_key = [key_bytes[i * 4:(i + 1) * 4] for i in range(Nk)]

    for i in range(Nk, Nb * (Nr + 1)):
        temp = expanded_key[i - 1]
        if i % Nk == 0:
            temp = temp[1:] + temp[:1]  # Циклический сдвиг влево
            temp = [S_BOX[b] for b in temp]  # Преобразование через S-Box
            temp[0] ^= RCON[i // Nk]  # XOR с соответствующей Rcon-константой
        # Сохраняем новое слово как XOR текущего temp и слова Nk позади
        expanded_key.append([
            expanded_key[i - Nk][j] ^ temp[j] for j in range(4)
        ])

    # Преобразуем список слов обратно в линейный список байтов
    return [byte for word in expanded_key for byte in word]


def aes_encrypt_block(block, key):
    state = list(block)  # Преобразуем блок в список байтов
    round_keys = key_expansion(key)  # Генерируем все ключи раундов

    state = add_round_key(state, round_keys[:16])  # Начальный раунд

    for round_num in range(1, 10):  # Основные 9 раундов
        state = sub_bytes(state)
        state = shift_rows(state)
        state = mix_columns(state, mix_matrix)
        state = add_round_key(state, round_keys[round_num * 16:(round_num + 1) * 16])

    # Финальный раунд без MixColumns
    state = sub_bytes(state)
    state = shift_rows(state)
    state = add_round_key(state, round_keys[160:176])
    return bytes(state)  # Возвращаем байты


def inv_sub_bytes(state):
    return [INV_S_BOX[byte] for byte in state]  # Обратная замена байтов


def inv_shift_rows(state):
    # Обратный сдвиг строк (направо)
    return [
        state[0], state[13], state[10], state[7],
        state[4], state[1], state[14], state[11],
        state[8], state[5], state[2], state[15],
        state[12], state[9], state[6], state[3]
    ]


def aes_decrypt_block(block, key):
    state = list(block)
    round_keys = key_expansion(key)

    state = add_round_key(state, round_keys[160:176])  # Начальный раунд

    for round_num in range(9, 0, -1):  # Обратные раунды
        state = inv_shift_rows(state)
        state = inv_sub_bytes(state)
        state = add_round_key(state, round_keys[round_num * 16:(round_num + 1) * 16])
        state = mix_columns(state, inv_mix_matrix)

    state = inv_shift_rows(state)
    state = inv_sub_bytes(state)
    state = add_round_key(state, round_keys[:16])
    return bytes(state)


def pad(data):
    padding_len = 16 - (len(data) % 16)  # Сколько байт добавить до кратности 16
    return data + bytes([padding_len] * padding_len)  # Добавляем паддинг


def unpad(data):
    padding_len = data[-1]  # Последний байт содержит значение паддинга
    return data[:-padding_len]  # Удаляем паддинг


def aes_encrypt_cbc(plaintext, key, iv):
    if len(plaintext) % 16 != 0:
        plaintext = pad(plaintext)
    #plaintext = pad(plaintext)  # Добавляем паддинг
    ciphertext = b""
    previous_block = iv  # Первый блок XOR'ится с IV

    for i in range(0, len(plaintext), 16):
        block = plaintext[i:i + 16]
        block = bytes([b ^ p for b, p in zip(block, previous_block)])  # XOR с предыдущим
        encrypted_block = aes_encrypt_block(block, key)
        ciphertext += encrypted_block
        previous_block = encrypted_block

    return ciphertext


def aes_decrypt_cbc(ciphertext, key, iv):
    plaintext = b""
    previous_block = iv

    for i in range(0, len(ciphertext), 16):
        block = ciphertext[i:i + 16]
        decrypted_block = aes_decrypt_block(block, key)
        plaintext += bytes([b ^ p for b, p in zip(decrypted_block, previous_block)])
        previous_block = block

    #return unpad(plaintext)
    unpad_plaintext = unpad(plaintext)

    if len(unpad_plaintext) == 0:
        return plaintext

    return unpad(plaintext)


def aes_encrypt_ecb(plaintext, key):
    if len(plaintext) % 16 != 0:
        plaintext = pad(plaintext)
    ciphertext = b""

    for i in range(0, len(plaintext), 16):
        block = plaintext[i:i + 16]
        ciphertext += aes_encrypt_block(block, key)

    return ciphertext


def aes_decrypt_ecb(ciphertext, key):
    plaintext = b""

    for i in range(0, len(ciphertext), 16):
        block = ciphertext[i:i + 16]
        plaintext += aes_decrypt_block(block, key)

    unpad_plaintext = unpad(plaintext)

    if len(unpad_plaintext) == 0:
        return plaintext

    return unpad(plaintext)