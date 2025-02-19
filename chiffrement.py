text = input("Tapez le message: ")
cle = "Bonjour"

def décalage(char, shift, encrypt=True):
    return chr((ord(char) + shift) % 128) if encrypt else chr((ord(char) - shift) % 128)

def vigenere(text, cle, encrypt=True):
    return ''.join(décalage(text[i], ord(cle[i % len(cle)]), encrypt) for i in range(len(text)))

# Chiffrement
text = vigenere(text, cle)
print("Texte chiffré:", text)

# Déchiffrement
text_dechiffre = vigenere(text, cle, encrypt=False)
print("Texte déchiffré:", text_dechiffre)



# --------------- challenge 1 ---------------------