from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import hashlib

def decalage(char, shift, encrypt=True):
    return chr((ord(char) + shift) % 128) if encrypt else chr((ord(char) - shift) % 128)

def vigenere(text, cle, encrypt=True):
    return ''.join(decalage(text[i], ord(cle[i % len(cle)]), encrypt) for i in range(len(text)))

def cesar(text, shift, encrypt=True):
    if encrypt:
        for abcd in ["abcdefghijklmnopqrstuvwxyz", "ABCDEFGHIJKLMNOPQRSTUVWXYZ"]:
            text = "".join([abcd[(abcd.index(char) + shift) % 26] if char in abcd else char for char in text])
    else:
        for abcd in ["abcdefghijklmnopqrstuvwxyz", "ABCDEFGHIJKLMNOPQRSTUVWXYZ"]:
            text = "".join([abcd[(abcd.index(char) - shift) % 26] if char in abcd else char for char in text])
    return text 

def xor(plain_text, key):
    """Chiffre un texte en clair en utilisant le chiffrement de Vigenère (support UTF-8)"""
    key_bytes = key.encode("utf-8")
    key_length = len(key_bytes)
    plain_bytes = plain_text.encode("utf-8")
    cipher_bytes = bytearray()

    for i, byte in enumerate(plain_bytes):
        shift = key_bytes[i % key_length]  # Décalage basé sur la clé en UTF-8
        cipher_bytes.append((byte + shift) % 256)  # Appliquer le décalage en UTF-8

    return cipher_bytes.hex()  # Retourne sous forme hexadécimale pour éviter les erreurs de décodage
    

def xor_dechiffrement(cipher_text, key):
    """Déchiffre un texte en utilisant le chiffrement de Vigenère (support UTF-8)"""
    key_bytes = key.encode("utf-8")
    key_length = len(key_bytes)
    cipher_bytes = bytes.fromhex(cipher_text)  # Convertir l'hexadécimal en bytes
    plain_bytes = bytearray()

    for i, byte in enumerate(cipher_bytes):
        shift = key_bytes[i % key_length]  # Décalage basé sur la clé en UTF-8
        plain_bytes.append((byte - shift) % 256)  # Appliquer le décalage en UTF-8

    return plain_bytes.decode("utf-8", errors="ignore")  # Convertir en texte UTF-8

def binaire(text):
    return ''.join(format(ord(char), '08b') for char in text)

def xor(bin_str1, bin_str2):
    if len(bin_str1) != len(bin_str2):
        raise ValueError("Les deux chaînes binaires doivent avoir la même longueur.")
    return ''.join(str(int(a) ^ int(b)) for a, b in zip(bin_str1, bin_str2))

def main():
    # Exemple de clé et de données
    cle = "clef"
    data = "donnees"

    # Convertir la clé et les données en binaire
    binary_key = binaire(cle)
    binary_data = binaire(data)

    print(f"Clé en binaire: {binary_key}")
    print(f"Données en binaire: {binary_data}")

    # Si les longueurs ne sont pas égales, on peut tronquer ou remplir les données
    min_length = min(len(binary_key), len(binary_data))
    binary_key = binary_key[:min_length]
    binary_data = binary_data[:min_length]

    # Effectuer l'opération XOR
    xor_result = xor(binary_key, binary_data)
    print(f"Résultat XOR en binaire: {xor_result}")

def aes(text, key, encrypt=True):
    # Genere une cle AES en SHA 256
    if type(key) == bytes:
        key = key.decode("utf-8")
    key_hash = hashlib.sha256(key.encode()).digest()[:16]
    
    cipher = AES.new(key_hash, AES.MODE_ECB)
    
    if encrypt:
        # Padding pour rendre compa avec AES
        padded_data = pad(text.encode('utf-8'), AES.block_size)
        encrypted_data = cipher.encrypt(padded_data).hex()
        return encrypted_data
    else:
        # Convertis et decrypte
        encrypted_data = bytes.fromhex(text)
        decrypted_data = cipher.decrypt(encrypted_data)
        # Retire le padding et met le texte original
        unpadded_data = unpad(decrypted_data, AES.block_size)
        return unpadded_data.decode('utf-8')
    
def generate_rsa_keys(key_size=2048):
    """Generate RSA public and private keys."""
    key = RSA.generate(key_size)
    private_key = key.export_key()
    public_key = key.publickey().export_key()
    return public_key, private_key

def rsa_encrypt(plaintext, public_key):
    """Encrypt a message using RSA public key."""
    rsa_key = RSA.import_key(public_key)
    cipher = PKCS1_OAEP.new(rsa_key)
    ciphertext = cipher.encrypt(plaintext.encode())
    return ciphertext.hex()

def rsa_decrypt(ciphertext_hex, private_key):
    """Decrypt a message using RSA private key."""
    rsa_key = RSA.import_key(private_key)
    cipher = PKCS1_OAEP.new(rsa_key)
    ciphertext = bytes.fromhex(ciphertext_hex)
    plaintext = cipher.decrypt(ciphertext)
    return plaintext.decode()