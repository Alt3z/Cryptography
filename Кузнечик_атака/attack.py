import numpy as np
from grasshopper import encrypt_block, expand_keys, operation_s, operation_x, operation_l, hex_to_bytes, bytes_to_hex
from constants import reverse_Pi


def simulate_fault_injection(plaintext_block, round_keys, target_round, target_byte):
    """Симулирует внесение ошибки (обнуление байта) в указанном раунде и байте"""
    # Создаём копию входного блока, чтобы не изменять исходные данные
    state = plaintext_block.copy()

    # Выполняем шифрование до раунда, в котором будет внесена ошибка
    for i in range(target_round - 1):
        state = operation_x(state, round_keys[i])  # XOR текущего состояния с раундовым ключом
        state = operation_s(state)  # Применение S-преобразования
        state = operation_l(state)  # Применение L-преобразования

    # Выполняем шифрование в целевом раунде с внесением ошибки
    state = operation_x(state, round_keys[target_round - 1])  # XOR с раундовым ключом
    state = operation_s(state)  # Применение S-преобразования
    state[target_byte] = 0  # Вносим ошибку, обнуляя указанный байт состояния
    state = operation_l(state)  # Применение L-преобразования после внесения ошибки

    # Выполняем оставшиеся раунды шифрования
    for i in range(target_round, 9):
        state = operation_x(state, round_keys[i])  # XOR с раундовым ключом
        state = operation_s(state)  # Применение S-преобразования
        state = operation_l(state)  # Применение L-преобразования

    # Выполняем последний раунд шифрования (только XOR с последним ключом)
    fault_ciphertext = operation_x(state, round_keys[9])

    # Выполняем обычное шифрование без внесения ошибок для сравнения
    correct_ciphertext = encrypt_block(plaintext_block, round_keys)

    # Возвращаем зашифрованные тексты с ошибкой и без неё
    return correct_ciphertext, fault_ciphertext


def find_key_byte(round_keys, target_round, target_byte, num_attempts=1000):
    """Находит байт ключа K1 или K2 с помощью атаки внесением ошибок"""
    # Получаем значение S^{-1}(0), необходимое для восстановления байта ключа
    s_inv_0 = reverse_Pi[0]

    for attempt in range(num_attempts):
        # Генерируем случайный блок открытого текста (16 байт)
        plaintext = np.random.randint(0, 256, 16, dtype=np.uint8)

        # Симулируем внесение ошибки в шифрование
        correct_ct, fault_ct = simulate_fault_injection(plaintext, round_keys, target_round, target_byte)

        # Проверяем, вызвала ли ошибка изменения в шифротексте
        if np.array_equal(correct_ct, fault_ct):  # Ошибка не повлияла на результат
            if target_round == 1:
                # Восстанавливаем i-ый байт ключа K1
                key_byte = plaintext[target_byte] ^ s_inv_0
            else:
                # Для восстановления байта K2 необходимо учитывать результат первого раунда
                intermediate_state = operation_x(plaintext, round_keys[0])  # Первый XOR
                intermediate_state = operation_s(intermediate_state)  # Применение S-преобразования
                intermediate_state = operation_l(intermediate_state)  # Применение L-преобразования
                key_byte = intermediate_state[target_byte] ^ s_inv_0  # Восстанавливаем байт K2

            # Выводим результат и возвращаем найденный байт ключа
            print(f"Найден байт {target_byte} ключа K{target_round}: {hex(key_byte)} (попытка {attempt + 1})")
            return key_byte

    # Если за указанное число попыток байт ключа не найден, выводим сообщение об ошибке
    print(f"Не удалось восстановить байт {target_byte} ключа K{target_round} за {num_attempts} попыток")
    return None  # Возвращаем None в случае неудачи


def recover_k1_k2(master_key_hex):
    """Восстанавливает K1 и K2 с помощью атаки внесением ошибок"""
    # Преобразуем мастер-ключ из шестнадцатеричной строки в массив байт
    master_key = hex_to_bytes(master_key_hex)
    # Генерируем раундовые ключи из мастер-ключа
    round_keys = expand_keys(master_key)
    # Разделяем первые два раундовых ключа (они соответствуют K1 и K2)
    real_k1, real_k2 = round_keys[0], round_keys[1]

    print("=" * 50)
    print("Начало атаки на шифр 'Кузнечик'")
    print("=" * 50)

    # Восстанавливаем ключ K1 (по первому раунду)
    recovered_k1 = np.zeros(16, dtype=np.uint8)  # Инициализируем массив для K1
    for byte_pos in range(16):  # Для каждого байта ключа
        key_byte = find_key_byte(round_keys, target_round=1, target_byte=byte_pos)
        if key_byte is not None:
            recovered_k1[byte_pos] = key_byte  # Сохраняем восстановленный байт

    # Восстанавливаем ключ K2 (по второму раунду)
    recovered_k2 = np.zeros(16, dtype=np.uint8)  # Инициализируем массив для K2
    for byte_pos in range(16):  # Для каждого байта ключа
        key_byte = find_key_byte(round_keys, target_round=2, target_byte=byte_pos)
        if key_byte is not None:
            recovered_k2[byte_pos] = key_byte  # Сохраняем восстановленный байт

    print("=" * 50)
    print("Результаты атаки")
    print("Восстановленный K1:", bytes_to_hex(recovered_k1))
    print("Ожидаемый K1:     ", bytes_to_hex(real_k1))
    print("Совпадение:       ", np.array_equal(recovered_k1, real_k1))

    print("\nВосстановленный K2:", bytes_to_hex(recovered_k2))
    print("Ожидаемый K2:     ", bytes_to_hex(real_k2))
    print("Совпадение:       ", np.array_equal(recovered_k2, real_k2))

    recovered_master_key = np.concatenate((recovered_k2, recovered_k1))
    print("\nВосстановленный мастер-ключ:", bytes_to_hex(recovered_master_key))
    print("Ожидаемый мастер-ключ:    ", master_key_hex)
    print("Совпадение:               ", bytes_to_hex(recovered_master_key) == master_key_hex)
    print("=" * 50)


if __name__ == "__main__":
    master_key_hex = "efcdab89674523011032547698badcfe7766554433221100ffeeddccbbaa9988"
    recover_k1_k2(master_key_hex)

    #master_key_hex = "eeff112233445566778899aabbccddeeffeeddccbbaa99887766554433221100"
    #recover_k1_k2(master_key_hex)