import json

# Load followers
with open('followers_1.json', 'r', encoding='utf-8') as f:
    followers_data = json.load(f)

# Load following
with open('following.json', 'r', encoding='utf-8') as f:
    following_data = json.load(f)

# Extract usernames
# Note: Instagram's JSON structure usually nests the username inside a string_list_data array
followers = set()
for item in followers_data:
    for string_data in item.get('string_list_data', []):
        followers.add(string_data.get('value'))

following = set()
# The following file usually nests items inside a 'relationships_following' key
following_list = following_data.get('relationships_following', following_data)
for item in following_list:
    for string_data in item.get('string_list_data', []):
        following.add(string_data.get('value'))

# Find people who don't follow you back
not_following_back = following - followers

# Print the results
print(f"--- {len(not_following_back)} People Not Following You Back ---")
for username in sorted(not_following_back):
    print(username)
