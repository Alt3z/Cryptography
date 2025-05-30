from quadratic_sieve_method import quadratic_sieve

if __name__ == "__main__":

    N = 1829
    factor = quadratic_sieve(N)
    print("Найден делитель:", factor)  #  (31, 59)

    N = 187
    factor = quadratic_sieve(N)
    print("Найден делитель:", factor)  #  (11, 17)

    N = 299
    factor = quadratic_sieve(N)
    print("Найден делитель:", factor)  #  (13, 23)

    N = 5959
    factor = quadratic_sieve(N)
    print("Найден делитель:", factor)  #  (59, 101)

    N = 24961
    factor = quadratic_sieve(N)
    print("Найден делитель:", factor)  #  (229, 109)

    N = 1098413
    factor = quadratic_sieve(N)
    print("Найден делитель:", factor)  #  (1951, 563)