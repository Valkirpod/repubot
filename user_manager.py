import json
import os
import datetime

USER_DATA_FOLDER = "user_data"

if not os.path.exists(USER_DATA_FOLDER):
    os.makedirs(USER_DATA_FOLDER)

def get_user_path(user_id):
    return f"{USER_DATA_FOLDER}/{user_id}.json"

def load_user(user_id):
    path = get_user_path(user_id)
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {
        "comments": [],
        "reputation": 0,
        "streak": {
            "current_streak": 0,
            "max_streak": 0,
            "last_claimed": datetime.datetime.min.replace(tzinfo=datetime.UTC).isoformat()
        }
    }

def save_user(user_id, data):
    path = get_user_path(user_id)
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

def user_exists(user_id):
    return os.path.exists(get_user_path(user_id))

def all_user_files():
    """Returns list of (user_id, data) tuples for all users."""
    results = []
    for filename in os.listdir(USER_DATA_FOLDER):
        if filename.endswith(".json"):
            user_id = int(filename.split(".json")[0])
            path = os.path.join(USER_DATA_FOLDER, filename)
            with open(path, "r") as f:
                data = json.load(f)
            results.append((user_id, data))
    return results