import json
import os
import glob
 
FOLLOWERS_PATTERN = 'followers_1.json'   # can also be 'followers_*.json' if you have multiple files
FOLLOWING_FILE = 'following.json'
 
 
def extract_usernames(file_pattern, data_key=None):
    """file_pattern can be a single filename or a glob pattern like 'followers_*.json'"""
    files = sorted(glob.glob(file_pattern)) if '*' in file_pattern else [file_pattern]
    files = [f for f in files if os.path.exists(f)]
 
    if not files:
        print(f"Error: No files found matching {file_pattern}")
        return set()
 
    usernames = set()
    for file_path in files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error: Could not parse {file_path} ({e})")
            continue
 
        if data_key and isinstance(data, dict) and data_key in data:
            items = data[data_key]
        elif isinstance(data, dict):
            list_values = [v for v in data.values() if isinstance(v, list)]
            if not list_values:
                print(f"Warning: No list found in {file_path}, skipping")
                continue
            items = list_values[0]
        else:
            items = data
 
        for item in items:
            if not isinstance(item, dict):
                continue
 
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
followers = extract_usernames(FOLLOWERS_PATTERN)
following = extract_usernames(FOLLOWING_FILE, data_key='relationships_following')
 
# Fans = people who follow you but you don't follow back
fans = followers - following
 
# Print summary results
print(f"\nFollowers found: {len(followers)}")
print(f"Following found: {len(following)}")
print(f"\n--- {len(fans)} Fans (Follow You, But You Don't Follow Back) ---")
for user in sorted(fans):
    print(user)
 