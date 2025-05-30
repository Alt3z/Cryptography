from aes import (
    aes_encrypt_cbc, aes_decrypt_cbc,
    aes_encrypt_ecb, aes_decrypt_ecb
)

def first_example():
    plaintext = bytes.fromhex("00112233445566778899aabbccddeeff")
    key = bytes.fromhex("000102030405060708090a0b0c0d0e0f")

    ciphertext = aes_encrypt_ecb(plaintext, key)
    print("ECB Encrypted (hex):", ciphertext.hex())

    decrypted = aes_decrypt_ecb(ciphertext, key)
    print("ECB Decrypted:", decrypted.hex())


def second_example():
    plaintext = bytes.fromhex("3243f6a8885a308d313198a2e0370734")
    key = bytes.fromhex("2b7e151628aed2a6abf7158809cf4f3c")

    ciphertext = aes_encrypt_ecb(plaintext, key)
    print("ECB Encrypted (hex):", ciphertext.hex())

    decrypted = aes_decrypt_ecb(ciphertext, key)
    print("ECB Decrypted:", decrypted.hex())

def my_example():
    key = bytes.fromhex("2b7e151628aed2a6abf7158809cf4f3c")
    iv = bytes.fromhex("2b7e151628aed2a6abf7158809cf4f3c")
    message = b"Hello AES! This is a test message."

    # --- CBC ---
    ciphertext = aes_encrypt_cbc(message, key, iv)
    print("CBC Encrypted (hex):", ciphertext.hex())

    decrypted_message = aes_decrypt_cbc(ciphertext, key, iv)
    print("CBC Decrypted:", decrypted_message.decode())

    print()

    # --- ECB ---
    ciphertext_ecb = aes_encrypt_ecb(message, key)
    print("ECB Encrypted (hex):", ciphertext_ecb.hex())

    decrypted_ecb = aes_decrypt_ecb(ciphertext_ecb, key)
    print("ECB Decrypted:", decrypted_ecb.decode())

def main():
    first_example()
    print()
    second_example()
    print()
    my_example()

if __name__ == "__main__":
    main()

'''
def main():
    key = bytes.fromhex("2b7e151628aed2a6abf7158809cf4f3c")
    iv = bytes.fromhex("2b7e151628aed2a6abf7158809cf4f3c")
    message = b"Hello AES CBC! This is a test message."

    # --- CBC ---
    ciphertext = aes_encrypt_cbc(message, key, iv)
    print("CBC Encrypted (hex):", ciphertext.hex())

    decrypted_message = aes_decrypt_cbc(ciphertext, key, iv)
    print("CBC Decrypted:", decrypted_message.decode())

    print()

    # --- ECB ---
    ciphertext_ecb = aes_encrypt_ecb(message, key)
    print("ECB Encrypted (hex):", ciphertext_ecb.hex())

    decrypted_ecb = aes_decrypt_ecb(ciphertext_ecb, key)
    print("ECB Decrypted:", decrypted_ecb.decode())

if __name__ == "__main__":
    main()
'''