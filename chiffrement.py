text = input("Tapez le message: ")
clé = "Bonjour"

def taille_clé(clé, length):
    clé_répété = (clé * (length // len(clé))) + clé[:length % len(clé)]
    return clé_répété

def décalage(char, shift, encrypt=True):
    if char.isupper():
        base = 65
    elif char.islower():
        base = 97
    else:
        return char

    if encrypt:
        return chr((ord(char) - base + shift) % 26 + base)
    else:
        return chr((ord(char) - base - shift) % 26 + base)

def vigenere(plain_text, key):
    """Chiffre le texte clair en utilisant la clé de Vigenère."""
    key = key.upper()
    plain_text = plain_text.upper()
    repeated_key = repeat_key(key, len(plain_text))
    encrypted_text = ''.join(shift_char(plain_text[i], ord(repeated_key[i]) - 65) for i in range(len(plain_text)))
    return encrypted_text

def vigenere_decrypt(encrypted_text, key):
    """Déchiffre le texte chiffré en utilisant la clé de Vigenère."""
    key = key.upper()
    encrypted_text = encrypted_text.upper()
    repeated_key = repeat_key(key, len(encrypted_text))
    decrypted_text = ''.join(shift_char(encrypted_text[i], ord(repeated_key[i]) - 65, encrypt=False) for i in range(len(encrypted_text)))
    return decrypted_text



# Chiffrement
encrypted_text = vigenere_encrypt(plain_text, key)
print("Texte chiffré:", encrypted_text)

# Déchiffrement
decrypted_text = vigenere_decrypt(encrypted_text, key)
print("Texte déchiffré:", decrypted_text)
