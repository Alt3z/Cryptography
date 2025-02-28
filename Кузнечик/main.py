from grasshopper import encrypt_cbc, decrypt_cbc

if __name__ == "__main__":
    message = "HELLO WORLD! 15 31 4 ПриВет мир!!?%1 "
    master_key = "efcdab89674523011032547698badcfe7766554433221100ffeeddccbbaa9988"
    iv = "000102030405060708090a0b0c0d0e0f"

    print(f"Исходный текст:       {message}")

    ciphertext = encrypt_cbc(message, master_key, iv)
    print(f"Зашифрованный текст:  {ciphertext}")

    decrypted_text = decrypt_cbc(ciphertext, master_key, iv)
    print(f"Расшифрованный текст: {decrypted_text}")