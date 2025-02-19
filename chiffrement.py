def décalage(char, shift, encrypt=True):
    return chr((ord(char) + shift) % 128) if encrypt else chr((ord(char) - shift) % 128)

def vigenere(text, cle, encrypt=True):
    return ''.join(décalage(text[i], ord(cle[i % len(cle)]), encrypt) for i in range(len(text)))

def cesar(text, shift, encrypt=True):
    if encrypt:
        for abcd in ["abcdefghijklmnopqrstuvwxyz", "ABCDEFGHIJKLMNOPQRSTUVWXYZ"]:
            text = "".join([abcd[(abcd.index(char) + shift) % 26] if char in abcd else char for char in text])
    else:
        for abcd in ["abcdefghijklmnopqrstuvwxyz", "ABCDEFGHIJKLMNOPQRSTUVWXYZ"]:
            text = "".join([abcd[(abcd.index(char) - shift) % 26] if char in abcd else char for char in text])
    return text
