import json
import os

# Update these paths if your files are named differently (e.g., if you have followers_2.json)
FOLLOWERS_FILE = 'followers_1.json'
FOLLOWING_FILE = 'following.json'

def extract_usernames(file_path, data_key=None):
    if not os.path.exists(file_path):
        print(f"Error: Could not find {file_path}")
        return set()
        
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # If Instagram nested the list inside a main key (like relationships_following)
    if data_key and isinstance(data, dict) and data_key in data:
        items = data[data_key]
    elif isinstance(data, dict):
        # Fallback if it's a dict but a different key name
        items = list(data.values())[0]
    else:
        # It's already a top-level list (common in modern followers_1.json)
        items = data

    usernames = set()
    for item in items:
        # Instagram packages user details inside a 'string_list_data' list
        for entry in item.get('string_list_data', []):
            username = entry.get('value')
            if username:
                usernames.add(username)
    return usernames

# Extract lists
followers = extract_usernames(FOLLOWERS_FILE)
following = extract_usernames(FOLLOWING_FILE, data_key='relationships_following')

# Compute difference
not_following_back = following - followers

# Print summary results
print(f"\n--- {len(not_following_back)} Accounts Not Following You Back ---")
for user in sorted(not_following_back):
    print(user)