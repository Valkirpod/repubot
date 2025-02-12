import os
import json


# ty gpt

# Folder containing JSON files
user_data_folder = "user_data"

# Loop through all JSON files in the folder
for filename in os.listdir(user_data_folder):
    if filename.endswith(".json"):
        file_path = os.path.join(user_data_folder, filename)

        # Read JSON file
        with open(file_path, "r") as file:
            data = json.load(file)

        # Check if the file contains comments and update the "type" field
        updated = False
        for comment in data.get("comments", []):
            if comment.get("type") == "positive":
                comment["type"] = 1
                updated = True
            elif comment.get("type") == "negative":
                comment["type"] = 0
                updated = True

        # Save changes if any updates were made
        if updated:
            with open(file_path, "w") as file:
                json.dump(data, file, indent=4)

print("All JSON files have been updated.")
