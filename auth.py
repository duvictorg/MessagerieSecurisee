import json
import bcrypt

USER_FILE = "users.json"


def load_users():
    """ Charge les utilisateurs depuis le fichier JSON """
    try:
        with open(USER_FILE, "r", encoding="utf-8") as f:
            return json.load(f)["users"]
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_users(users):
    """ Sauvegarde les utilisateurs dans le fichier JSON """
    with open(USER_FILE, "w", encoding="utf-8") as f:
        json.dump({"users": users}, f, indent=4)


def register_user(username, password):
    """ Enregistre un nouvel utilisateur avec un mot de passe haché """
    users = load_users()
    if username in users:
        return False, "❌ Utilisateur déjà existant !"

    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    users[username] = hashed_pw
    save_users(users)
    return True, "✅ Enregistrement réussi !"


def authenticate_user(username, password):
    """ Vérifie l'authentification de l'utilisateur """
    users = load_users()
    if username not in users:
        return False, "❌ Utilisateur non trouvé !"

    hashed_pw = users[username]
    if bcrypt.checkpw(password.encode(), hashed_pw.encode()):
        return True, "✅ Connexion réussie !"
    else:
        return False, "❌ Mot de passe incorrect !"
