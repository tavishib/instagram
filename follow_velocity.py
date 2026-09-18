import json
import os
import glob
from datetime import datetime
from collections import Counter

import matplotlib.pyplot as plt

FOLLOWING_FILE = 'following.json'
FOLLOWERS_PATTERN = 'followers_1.json'  # set to 'followers_*.json' if you have multiple files


def extract_entries(file_pattern, data_key=None):
    """Returns list of (username, timestamp) tuples."""
    files = sorted(glob.glob(file_pattern)) if '*' in file_pattern else [file_pattern]
    files = [f for f in files if os.path.exists(f)]

    if not files:
        print(f"Error: No files found matching {file_pattern}")
        return []

    entries = []
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
                continue
            items = list_values[0]
        else:
            items = data

        for item in items:
            if not isinstance(item, dict):
                continue

            username = None
            timestamp = None

            for entry in item.get('string_list_data', []):
                timestamp = entry.get('timestamp', timestamp)
                if entry.get('value'):
                    username = entry['value']
                elif entry.get('href') and not username:
                    username = entry['href'].rstrip('/').split('/')[-1]

            if not username and item.get('title'):
                username = item['title']

            if username and timestamp:
                entries.append((username, timestamp))

    return entries


def monthly_counts(entries):
    """Bucket (username, timestamp) entries into YYYY-MM counts."""
    counts = Counter()
    for _, ts in entries:
        try:
            dt = datetime.fromtimestamp(ts)
        except (ValueError, OSError, OverflowError):
            continue
        key = f"{dt.year:04d}-{dt.month:02d}"
        counts[key] += 1
    return counts


def plot_velocity(following_counts, followers_counts=None):
    all_months = sorted(set(following_counts) | set(followers_counts or {}))
    if not all_months:
        print("No valid timestamped entries found to plot.")
        return

    following_vals = [following_counts.get(m, 0) for m in all_months]

    fig, ax = plt.subplots(figsize=(14, 6))
    ax.plot(all_months, following_vals, marker='o', linewidth=1.5, label='Accounts followed', color='#3897f0')

    if followers_counts:
        followers_vals = [followers_counts.get(m, 0) for m in all_months]
        ax.plot(all_months, followers_vals, marker='o', linewidth=1.5, label='New followers', color='#e1306c')

    ax.set_title('Follow Velocity Over Time (per month)', fontsize=14, fontweight='bold')
    ax.set_xlabel('Month')
    ax.set_ylabel('Number of accounts')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Thin out x-axis labels so they stay readable
    step = max(1, len(all_months) // 24)
    ax.set_xticks(range(0, len(all_months), step))
    ax.set_xticklabels([all_months[i] for i in range(0, len(all_months), step)], rotation=45, ha='right')

    plt.tight_layout()
    output_path = 'follow_velocity.png'
    plt.savefig(output_path, dpi=150)
    print(f"\nChart saved to {output_path}")


if __name__ == '__main__':
    following_entries = extract_entries(FOLLOWING_FILE, data_key='relationships_following')
    followers_entries = extract_entries(FOLLOWERS_PATTERN)

    following_by_month = monthly_counts(following_entries)
    followers_by_month = monthly_counts(followers_entries)

    print(f"Following entries with valid timestamps: {len(following_entries)}")
    print(f"Followers entries with valid timestamps: {len(followers_entries)}")

    # Busiest months
    if following_by_month:
        busiest = max(following_by_month.items(), key=lambda x: x[1])
        print(f"\nBusiest 'following' month: {busiest[0]} ({busiest[1]} accounts followed)")

    plot_velocity(following_by_month, followers_by_month if followers_entries else None)