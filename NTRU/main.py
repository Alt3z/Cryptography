import numpy as np
from sympy import Poly, symbols

# Символ переменной x для многочленов в sympy
x = symbols('x')

# Функция поэлементного взятия по модулю q
def poly_mod(poly, q):
    return np.array([x % q for x in poly])

# Сложение двух многочленов по модулю q
def poly_add(a, b, q):
    return poly_mod(a + b, q)

# Умножение двух многочленов по модулю (x^N - 1), затем по модулю q
def poly_mul(a, b, N, q):
    result = np.convolve(a, b)  # умножение многочленов
    for i in range(N, len(result)):
        # свёртка больше N - приводим по модулю (x^N - 1)
        result[i - N] += result[i]
    result = result[:N]  # оставляем только степень < N
    return poly_mod(result, q)

# Центрируем коэффициенты по модулю q в диапазон (-q/2, q/2]
def center_mod_q(poly, q):
    return np.array([(x + q//2) % q - q//2 for x in poly])

# Центрируем по модулю p в диапазон (-p/2, p/2]
def center_mod_p(poly, p):
    return np.array([(x + p//2) % p - p//2 for x in poly])

# Нахождение обратного многочлена f^-1 по модулю в кольце Z_mod[x]/(x^N - 1)
def invert_poly(f, mod, N):
    f_poly = Poly(list(f[::-1]), x, modulus=mod)  # создаем f(x)
    modulus_poly = Poly([1] + [0]*(N-1) + [-1], x, modulus=mod)  # x^N - 1
    f_inv = f_poly.invert(modulus_poly)  # ищем обратный многочлен
    coeffs = [int(c) for c in f_inv.all_coeffs()][::-1]  # переворачиваем список
    return np.array(coeffs + [0]*(N - len(coeffs)))  # дополняем нулями до N

# === ПАРАМЕТРЫ ===
N = 7        # степень кольца (x^N - 1)
p = 3        # малый модуль
q = 41       # большой модуль

# === МНОГОЧЛЕНЫ ===
# f(x): секретный ключ
f = np.array([-1, 1, 1, 0, -1, 0, 1])

# g(x): вспомогательный многочлен
g = np.array([-1, 0, 1, 1, 0, 0, -1])

# Находим f^-1 по модулю q и p
fq_inv = invert_poly(f, q, N)
fp_inv = invert_poly(f, p, N)

# Публичный ключ: h(x) = p * fq^-1 * g mod q
h = poly_mod(p * poly_mul(fq_inv, g, N, q), q)

print("h(x):", h)

# === СООБЩЕНИЕ и СЛУЧАЙНЫЙ ВЕКТОР ===
m = np.array([1, 1, 0, -1, 0, 0, 0])  # сообщение
r = np.array([-1, 0, 1, 0, 0, 0, 1])  # случайный шифрующий многочлен

# === ШИФРОВАНИЕ ===
# c(x) = r(x) * h(x) + m(x) mod q
c = poly_add(poly_mul(r, h, N, q), m, q)
print("Ciphertext c(x):", c)

# === РАСШИФРОВАНИЕ ===
# a(x) = f(x) * c(x) mod q
a = poly_mul(f, c, N, q)
a_centered = center_mod_q(a, q)
print("a(x) centered:", a_centered)

# b(x) = a(x) mod p
b = poly_mod(a_centered, p)
print("b(x):", b)

# Проверка: fp^-1 (по модулю p)
print("fp^-1(x):", fp_inv)

# Восстановление сообщения:
# M = b(x) * fp^-1(x) mod p
recovered = poly_mod(poly_mul(b, fp_inv, N, p), p)
recovered = center_mod_p(recovered, p)
print("Recovered M(x):", recovered)
