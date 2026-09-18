import json
import os

FOLLOWERS_FILE = 'followers_1.json'
FOLLOWING_FILE = 'following.json'

def extract_usernames(file_path, data_key=None):
    if not os.path.exists(file_path):
        print(f"Error: Could not find {file_path}")
        return set()

    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if data_key and isinstance(data, dict) and data_key in data:
        items = data[data_key]
    elif isinstance(data, dict):
        items = list(data.values())[0]
    else:
        items = data

    usernames = set()
    for item in items:
        username = None

        # Try string_list_data entries first (some exports have 'value' here)
        for entry in item.get('string_list_data', []):
            if entry.get('value'):
                username = entry['value']
                break
            elif entry.get('href'):
                # Fallback: pull the username out of the profile URL
                username = entry['href'].rstrip('/').split('/')[-1]
                break

        # Fallback: some exports put the username in the item's 'title'
        if not username and item.get('title'):
            username = item['title']

        if username:
            usernames.add(username)

    return usernames

# Extract lists
followers = extract_usernames(FOLLOWERS_FILE)
following = extract_usernames(FOLLOWING_FILE, data_key='relationships_following')

print(f"Followers found: {len(followers)}")
print(f"Following found: {len(following)}")

# Compute difference
not_following_back = following - followers

# Print summary results
print(f"\n--- {len(not_following_back)} Accounts Not Following You Back ---")
for user in sorted(not_following_back):
    print(user)