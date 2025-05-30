from Attack_of_Big_and_Small_Steps import attack_of_big_and_small_steps

if __name__ == "__main__":
    def run_tests():
        tests = [
            (6, 2, 19, 14),
            (67, 59, 113, 11),
            (62, 2, 181, 100),
            (22, 2, 29, 26),
            (13, 3, 17, 4),
            (3, 5, 23, 16),
            (11, 3, 17, 7),
            (28, 2, 37, 34),
            (62, 4, 181, 50),
        ]

        for y, a, s, expected in tests:
            result = attack_of_big_and_small_steps(y, a, s)  # Запускаем алгоритм
            print(f"log_{y}({a}) mod {s} = {result} (ожидалось: {expected})")
            assert result == expected, f"Ошибка в тесте: y={y}, a={a}, s={s}, ожидалось {expected}, но получили {result}"
        print("\nВсе тесты пройдены успешно!")

    run_tests()
