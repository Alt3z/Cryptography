import random
from collections import Counter
import matplotlib.pyplot as plt

def linear_congruential_generator(a, b, N, start_x, num_values):
    random_numbers = []
    x = start_x

    for i in range(num_values):
        x = (a * x + b) % N
        random_numbers.append((x % 100) + 1)  # Генерация чисел от 1 до 100

    return random_numbers

def frequency_spread(counter):
    frequencies = list(counter.values())
    return max(frequencies) - min(frequencies)

def find_best_parameters(start_x, num_values, num_trials, coverage_threshold):
    best_a, best_b, best_N = None, None, None
    best_spread = float('inf')

    for i in range(num_trials):
        a = random.randint(1, 50000000)
        b = random.randint(1, 50000000)
        N = random.randint(1000000, 10000000)

        random_numbers = linear_congruential_generator(a, b, N, start_x, num_values)
        counter = Counter(random_numbers)

        if len(counter) < coverage_threshold:
            continue

        spread = frequency_spread(counter)

        if spread < best_spread:
            best_a, best_b, best_N = a, b, N
            best_spread = spread

    return best_a, best_b, best_N, best_spread

start_x = 42
num_values = 10000
num_trials = 1000  # Увеличим количество попыток для поиска оптимальных параметров
coverage_threshold = 100

best_a, best_b, best_N, best_spread = find_best_parameters(start_x, num_values, num_trials, coverage_threshold)

print(f"Наилучшие параметры: a = {best_a}, b = {best_b}, N = {best_N}")
print(f"Максимальный разброс в частоте чисел: {best_spread}\n")

random_numbers = linear_congruential_generator(5777001, 40103169, 1540800, start_x, num_values)
counter = Counter(random_numbers)

for number, frequency in sorted(counter.items()):
    print(f"Число {number} встречается {frequency} раз")

# Построение графика частоты чисел
numbers = list(counter.keys())
frequencies = list(counter.values())

plt.bar(numbers, frequencies)
plt.xlabel('Числа')
plt.ylabel('Частота')
plt.title('Распределение частоты чисел')
plt.show()