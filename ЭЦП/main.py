from EDS import generate_keys, sign, verify
from EDS import P1, Q1, Gx1, Gy1, A1, B1
from EDS import P2, Q2, Gx2, Gy2, A2, B2

if __name__ == "__main__":
    message = b"I love EDS"
    d, Qd = generate_keys(P1, Q1, Gx1, Gy1, A1, B1)
    signature = sign(message, d, P1, Q1, Gx1, Gy1, A1)
    print("Подпись:", signature)
    print("Проверка подписи:", verify(message, signature, Qd, P1, Q1, Gx1, Gy1, A1))

    print()

    d, Qd = generate_keys(P2, Q2, Gx2, Gy2, A2, B2)
    signature = sign(message, d, P2, Q2, Gx2, Gy2, A2)
    print("Подпись:", signature)
    print("Проверка подписи:", verify(message, signature, Qd, P2, Q2, Gx2, Gy2, A2))