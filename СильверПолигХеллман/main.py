from silver_pohlig_hellman import silver_pohlig_hellman

if __name__ == "__main__":
    def run_tests():
        tests = [
            (2, 62, 181, 100),  # log_2(62) mod 181 = 100
            (2, 22, 29, 26),  # log_2(22) mod 29 = 26
            (3, 13, 17, 4),  # log_3(13) mod 17 = 4
            (5, 3, 23, 16),  # log_5(3) mod 23 = 16
            (59, 67, 113, 11),
            (3, 11, 17, 7),
            (2, 28, 37, 34),
            (4, 62, 181, 140),
        ]

        for a, b, q, expected in tests:
            result = silver_pohlig_hellman(a, b, q)  # Запускаем алгоритм
            print(f"log_{a}({b}) mod {q} = {result} (ожидалось: {expected})")
            assert result == expected, f"Ошибка в тесте: a={a}, b={b}, q={q}, ожидалось {expected}, но получили {result}"
        print("\nВсе тесты пройдены успешно!")


    # Запускаем тесты
    run_tests()
