import re


def verifica_username(username):
    pattern = r'^[^\s]+$'
    return re.match(pattern, username) is not None


def verifica_textul(text):
    pattern = r'^[a-zA-Z0-9_]+$'
    return re.match(pattern, text) is not None


# Exemple de utilizare
usernames = [" user123", "user 123", "user.name", "user@domain.com", "user_name", " use r @domain"]

for username in usernames:
    if verifica_username(username):
        print(f'"{username}" este valid.')
    else:
        print(f'"{username}" nu este valid.')