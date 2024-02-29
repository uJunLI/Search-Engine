import json
from werkzeug.security import generate_password_hash, check_password_hash

json_file_path = "login_users_historys/user_data.json"

def login_check(username, password):
    user_data = get_user_data(username)

    if user_data:
        hashed_password = user_data.get('password_hash')
        if check_password_hash(hashed_password, password):
            return True
        else:
            return False
    else:
        create_new_user(username, password)
        return True


def get_user_data(username):
    try:
        with open(json_file_path, 'r') as file:
            data = json.load(file)
            return data.get(username)
    except FileNotFoundError:
        return None


def create_new_user(username, password):
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

    user_data = {
        "username": username,
        "password_hash": hashed_password
    }

    try:
        with open(json_file_path, 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        data = {}

    data[username] = user_data

    with open(json_file_path, 'w') as file:
        json.dump(data, file)

# Use 'pbkdf2:sha256' as the hash method
