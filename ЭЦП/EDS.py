from stribog import Stribog
import random
from typing import Tuple

# Параметры эллиптической кривой из ГОСТа
P1 = 0x8000000000000000000000000000000000000000000000000000000000000431  # Простое число > 3
A1 = 0x7  # Коэффициент определяющий кривую
B1 = 0x5FBFF498AA938CE739B8E022FBAFEF40563F6E6A3472FC2A514C0CE9DAE23B7E  # Коэффициент определяющий кривую
Q1 = 0x8000000000000000000000000000000150FE8A1892976154C59CFC193ACCF5B3  # Порядок группы точек эллиптической кривой
Gx1 = 0x2  # x-координата базовой точки G
Gy1 = 0x8E2A8A0E65147D4BD6316030E16D19C85C97F0A9CA267122B96ABBCEA7E8FC8  # y-координата базовой точки G

P2 = 0x4531ACD1FE0023C7550D267B6B2FEE80922B14B2FFB90F04D4EB7C09B5D2D15DF1D852741AF4704A0458047E80E4546D35B8336FAC224DD81664BBF528BE6373
A2 = 0x7
B2 = 0x1CFF0806A31116DA29D8CFA54E57EB748BC5F377E49400FDD788B649ECA1AC4361834013B2AD7322480A89CA58E0CF74BC9E540C2ADD6897FAD0A3084F302ADC
Q2 = 0x4531ACD1FE0023C7550D267B6B2FEE80922B14B2FFB90F04D4EB7C09B5D2D15DA82F2D7ECB1DBAC719905C5EECC423F1D86E25EDBE23C595D644AAF187E6E6DF
Gx2 = 0x24D19CC64572EE30F396BF6EBBFD7A6C5213B3B3D7057CC825F91093A68CD762FD60611262CD838DC6B60AA7EEE804E28BC849977FAC33B4B530F1B120248A9A
Gy2 = 0x2BB312A43BD2CE6E0D020613C857ACDDCFBF061E91E5F2C3F32447C259F39B2C83AB156D77F1496BF7EB3351E1EE4E43DC1A18B91B24640B6DBB92CB1ADD371E


def gost_hash(message: bytes, hash_size=256) -> int:
    """
    Получение хэша через стрибог
    """
    input_hex = message.hex()  # Преобразуем байты сообщения в шестнадцатеричную строку
    hash_result = Stribog(input_hex, hash_size)  # Вычисляем хеш, результат — массив байтов
    hash_str = ''.join(format(x, '02x') for x in hash_result)  # Преобразуем байты в строку
    return int(hash_str, 16)  # Преобразуем строку в число

def point_addition(P1, P2, P, A):
    """
    Сложение двух точек эллиптической кривой
    """
    if P1 == (0, 0):
        return P2  # Если P1 — нулевая точка, результатом будет P2
    if P2 == (0, 0):
        return P1  # Если P2 — нулевая точка, результатом будет P1
    x1, y1 = P1
    x2, y2 = P2
    if x1 == x2 and y1 == (-y2 % P):  # Если точки противоположны, возвращается нулевая точка
        return (0, 0)
    if P1 != P2:
        denominator = (x2 - x1) % P  # Вычисляем знаменатель лямбды для разных точек
    else:
        denominator = (2 * y1) % P  # Вычисляем знаменатель лямбды для одинаковых точек
    try:
        inv_denominator = pow(denominator, -1, P)  # Обратное значение знаменателя
    except ValueError:
        return (0, 0)  # Если знаменатель необратим, возвращаем нулевую точку
    if P1 != P2:
        lam = ((y2 - y1) * inv_denominator) % P  # Вычисляем лямбду
    else:
        lam = ((3 * x1**2 + A) * inv_denominator) % P
    x3 = (lam**2 - x1 - x2) % P  # Вычисляем x-координату результата
    y3 = (lam * (x1 - x3) - y1) % P  # Вычисляем y-координату результата
    return (x3, y3)  # Возвращаем новую точку

def point_multiplication(k, P, P_prime, A):
    """
    Умножение точки P на число k
    """
    R = (0, 0)  # Начальная точка — нулевая
    Q = P  # Копируем начальную точку
    while k > 0:
        if k % 2 == 1:
            R = point_addition(R, Q, P_prime, A)  # Добавляем Q к R
        Q = point_addition(Q, Q, P_prime, A)  # Удваиваем Q
        k //= 2  # Делим k на 2
    return R  # Возвращаем итоговую точку

def is_point_on_curve(x, y, P, A, B):
    """
    Проверка принадлежности точки кривой
    """
    return (y ** 2 - (x ** 3 + A * x + B)) % P == 0

def generate_keys(P, Q, Gx, Gy, A, B):
    """
    Генерация пары ключей: закрытого и открытого
    """
    while True:
        d = random.randint(1, Q - 1)  # Генерируем случайный секретный ключ
        Qd = point_multiplication(d, (Gx, Gy), P, A)  # Вычисляем открытый ключ
        if is_point_on_curve(Qd[0], Qd[1], P, A, B):  # Проверяем принадлежность точки кривой
            return d, Qd  # Возвращаем пару ключей

def sign(message: bytes, d: int, P, Q, Gx, Gy, A) -> Tuple[int, int]:
    """
    Подписывает сообщение
    """
    e = gost_hash(message) % Q  # Вычисляем хеш сообщения
    if e == 0:
        e = 1  # Если e = 0, устанавливаем его в 1
    while True:
        k = random.randint(1, Q - 1)
        R = point_multiplication(k, (Gx, Gy), P, A)  # Вычисляем точку R
        r = R[0] % Q  # r — это x-координата R по модулю Q
        if r == 0:
            continue
        s = (r * d + k * e) % Q  # Вычисляем s
        if s == 0:
            continue
        return r, s  # Возвращаем подпись


def verify(message: bytes, signature: Tuple[int, int], Q_pub: Tuple[int, int], P, Q, Gx, Gy, A) -> bool:
    """
    Проверяет подпись
    """
    r, s = signature
    if not (0 < r < Q and 0 < s < Q):
        return False
    e = gost_hash(message) % Q
    if e == 0:
        e = 1
    v = pow(e, -1, Q)  # Вычисляем v = e^(-1) mod Q
    z1 = (s * v) % Q
    z2 = (-r * v) % Q
    R = point_addition(
        point_multiplication(z1, (Gx, Gy), P, A),
        point_multiplication(z2, Q_pub, P, A),
        P,
        A
    )
    return R[0] % Q == r