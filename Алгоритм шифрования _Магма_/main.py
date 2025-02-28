def string_to_bits_array(data_string): # Функция для преобразования строки в байты
    byte_data = data_string.encode('utf-8') # Преобразуем строку в байты с использованием UTF-8

    bits = ''.join(f'{byte:08b}' for byte in byte_data) # Преобразуем байты в битовое представление

    # Разбиваем строку битов на блоки по 64 бита
    block_size = 64
    data = []
    for i in range(0, len(bits), block_size):
        block = bits[i:i + block_size]
        # Преобразуем каждый блок в число и добавляем в массив
        data.append(int(block.ljust(block_size, '0'), 2))  # Дополняем нулями до 64 бит при необходимости

    return data

def bits_array_to_string(data): # Функция для байтов в строку
    bits = ''.join(f'{num:064b}' for num in data) # Объединяем массив целых чисел в одну строку битов

    # Разбиваем строку битов на 8-битные байты
    byte_size = 8
    byte_list = []
    for i in range(0, len(bits), byte_size):
        byte = bits[i:i + byte_size]
        byte_list.append(int(byte, 2))

    # Преобразуем байты обратно в строку с использованием UTF-8
    byte_data = bytearray(byte_list)
    text = byte_data.decode('utf-8')

    # Удаляем нулевые символы в конце
    return text.rstrip('\x00')

def read_text_from_file(file_path): # Функция для чтения из файла
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    return text

def write_text_to_file(file_path, text): # Функция для записи в файл
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(text)

def sbox_transform(value): # Функция для применения s-box
    result = 0
    for i in range(8): # Разбиваем 32-битное число на 8 частей по 4 бита
        part = (value >> (4 * i)) & 0xF # Берем текущие 4 бита
        transformed_part = S_BOX[i][part] # Применяем соответствующую строку S_BOX
        result |= transformed_part << (4 * i) # Объединяем обратно в результат
    return result

def division_into_parts(data): # Функция для разделения исходного блока на 2 части
    L = (data >> 32) & 0xFFFFFFFF  # Старшие 32 бита
    R = data & 0xFFFFFFFF  # Младшие 32 бита
    return L, R

def module_by_add(part, key): # Функция для вычисления сложения по модулю
    part = (part + key) % (2 ** 32)
    return part

def cyclic_shift(part): # Функция для циклического сдвига
    part = ((part << 11) & 0xFFFFFFFF) | (part >> 21)  # Циклический сдвиг на 11 битов
    return part

def encryption_magma(data, keys): # Функция для шифрования алгоритмом Магма
    L, R = division_into_parts(data) # Делим на 2 части

    for i in range(3): # Первые 24 раунда
        for j in range(8):
            new_R = module_by_add(R, keys[j]) # Сложение с ключом по модулю
            new_R = sbox_transform(new_R)  # Применяем s-box
            new_R = cyclic_shift(new_R)  # Циклический сдвиг на 11 битов
            new_R ^= L

            L = R
            R = new_R

    for j in range(7, -1, -1): # Последние 8 раундов
        new_R = module_by_add(R, keys[j])
        new_R = sbox_transform(new_R)
        new_R = cyclic_shift(new_R)
        new_R ^= L

        if (j != 0):
            L = R
            R = new_R
        else: # Последний раунд
            L = new_R

    encrypted_data = (L << 32) | R  # Объединяем в 64-битное число
    return encrypted_data

def decryption_magma(data, keys):
    L, R = division_into_parts(data)

    for j in range(8):
        if (j != 0):
            new_R = module_by_add(L, keys[j])
            new_R = sbox_transform(new_R)
            new_R = cyclic_shift(new_R)
            new_L = new_R ^ R

            R = L
            L = new_L
        else: # первый раунд
            new_R = module_by_add(R, keys[j])
            new_R = sbox_transform(new_R)
            new_R = cyclic_shift(new_R)
            new_L = new_R ^ L

            L = new_L

    for i in range(3):
        for j in range(7, -1, -1):
            new_R = module_by_add(L, keys[j])
            new_R = sbox_transform(new_R)
            new_R = cyclic_shift(new_R)
            new_L = new_R ^ R

            R = L
            L = new_L

    decrypted_data = (L << 32) | R  # Объединяем в 64-битное число
    return decrypted_data

S_BOX = [
    [0xC, 0x4, 0x6, 0x2, 0xA, 0x5, 0xB, 0x9, 0xE, 0x8, 0xD, 0x7, 0x0, 0x3, 0xF, 0x1],
    [0x6, 0x8, 0x2, 0x3, 0x9, 0xA, 0x5, 0xC, 0x1, 0xE, 0x4, 0x7, 0xB, 0xD, 0x0, 0xF],
    [0xB, 0x3, 0x5, 0x8, 0x2, 0xF, 0xA, 0xD, 0xE, 0x1, 0x7, 0x4, 0xC, 0x9, 0x6, 0x0],
    [0xC, 0x8, 0x2, 0x1, 0xD, 0x4, 0xF, 0x6, 0x7, 0x0, 0xA, 0x5, 0x3, 0xE, 0x9, 0xB],
    [0x7, 0xF, 0x5, 0xA, 0x8, 0x1, 0x6, 0xD, 0x0, 0x9, 0x3, 0xE, 0xB, 0x4, 0x2, 0xC],
    [0x5, 0xD, 0xF, 0x6, 0x9, 0x2, 0xC, 0xA, 0xB, 0x7, 0x8, 0x1, 0x4, 0x3, 0xE, 0x0],
    [0x8, 0xE, 0x2, 0x5, 0x6, 0x9, 0x1, 0xC, 0xF, 0x4, 0xB, 0x0, 0xD, 0xA, 0x3, 0x7],
    [0x1, 0x7, 0xE, 0xD, 0x0, 0x5, 0x8, 0x3, 0x4, 0xF, 0xA, 0x6, 0x9, 0xC, 0xB, 0x2],
]

keys = [
    0b10101111000001011010101011110000,  # K1
    0b01111000111100001111000011110000,  # K2
    0b11000001110000011100000111000001,  # K3
    0b00000101111101011111010111110101,  # K4
    0b11100011001100111100110011001100,  # K5
    0b01010101010101010101010101010101,  # K6
    0b11111111000000001111111100000000,  # K7
    0b10101010101010101010101010101010   # K8
]

input_file = 'input.txt'  # Путь к файлу с текстом, который нужно зашифровать
output_file = 'output.txt'  # Путь к файлу для записи шифрованного текста

text = read_text_from_file(input_file) # Читаем текст из файла
print(f"Шифруемые данные: {text}")

data = string_to_bits_array(text) # Преобразовываем строку в биты

iv = 0b1100100000110000100011000000011110111111000000110000001100011101 # Вектор смещения
vector = iv

cr_data = [] # Массив для зашифрованных блоков
decr_data = [] # Массив для расшифрованных блоков

for i in range(len(data)): # Шифруем каждый блок
    vec_data = data[i] ^ vector # Применяем вектор смещения
    encrypted_data = encryption_magma(vec_data, keys) # Выполняем шифровку

    vector = encrypted_data # Изменяем вектор смещения
    cr_data.append(encrypted_data) # Добавляем шифрованный блок

cr_text = '0b' + ''.join(f'{num:b}' for num in cr_data)
print(f"Зашифрованный текст: {cr_text}")
write_text_to_file(output_file, cr_text)

vector = iv
for i in range(len(cr_data)): # Дешифровка
    decrypted_data = decryption_magma(cr_data[i], keys)
    vec_data = decrypted_data ^ vector
    vector = cr_data[i]
    decr_data.append(vec_data)

decr_text = bits_array_to_string(decr_data)
print(f"Зашифрованный текст: {decr_text}")