import hashlib  # Импортируем модуль для работы с хешами (SHA-256)


# Функция для перевода hex-строки в little-endian (обратный порядок байтов)
def little_endian(hex_str):
    # Разбиваем строку на байты (по 2 символа) и разворачиваем список
    return ''.join(reversed([hex_str[i:i+2] for i in range(0, len(hex_str), 2)]))


# Функция "майнинга": подбирает nonce так, чтобы хеш блока начинался с '0000'
def mine_block(header, target_prefix="0000"):
    nonce = 0  # Начинаем перебор с 0
    while True:
        # Представляем nonce как 4-байтное число в little-endian
        nonce_hex = nonce.to_bytes(4, byteorder='little').hex()

        # Собираем полный блок: заголовок + nonce
        block_data = header + nonce_hex

        # Дважды применяем SHA-256, как требует протокол Bitcoin
        block_hash = hashlib.sha256(hashlib.sha256(bytes.fromhex(block_data)).digest()).hexdigest()

        # Проверяем, начинается ли хеш с заданного префикса (например, "0000")
        if block_hash.startswith(target_prefix):
            print(f"Nonce найден: {nonce}")
            print(f"Хеш блока: {block_hash}")
            break  # Если найден — выходим
        nonce += 1  # Иначе продолжаем поиск



# --- ДАННЫЕ БЛОКА (упрощённые, как в задании) ---

# Версия блока (в 16-ричном формате): 0x20000000
# Преобразуем в little-endian: '00000020'
version = little_endian("20000000")

# Хеш предыдущего блока (первые 16 символов + дополняем до 64)
# Преобразуем в little-endian
prev_block = little_endian("00000000000000000001abcd0000000000000000000000000000000000000000")

# Merkle Root (первые 16 символов + дополняем до 64)
# Преобразуем в little-endian
merkle_root = little_endian("abcdef1234560000000000000000000000000000000000000000000000000000")

# Временная метка (timestamp): 1630000000 в десятичном виде
# Сначала переводим в hex → затем в little-endian
timestamp = little_endian("{:08x}".format(1630000000))  # 1630000000 = 0x612a05a0

# Сложность (Bits): 0x17001234 → little-endian: 34120017
bits = little_endian("17001234")

# Собираем заголовок блока без nonce (он будет добавлен позже)
header = version + prev_block + merkle_root + timestamp + bits

# Запускаем функцию поиска nonce
mine_block(header)
