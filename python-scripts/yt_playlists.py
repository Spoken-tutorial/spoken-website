# YouTube Data API Key Setup Instructions


# To run this script, you must generate a YouTube Data API key.
#
# Steps to obtain the key:
#
# 1. Go to Google Cloud Console:
#    https://console.cloud.google.com/
#
# 2. Create a new project (or select an existing one).
#
# 3. Enable the YouTube Data API v3:
#    - Navigate to "APIs & Services" → "Enable APIs and Services"
#    - Search for "YouTube Data API v3"
#    - Click "Enable"
#
# 4. Create an API key:
#    - Go to "APIs & Services" → "Credentials"
#    - Click "Create Credentials" → "API key"
#
# 5. Put the key in a .env file in the same directory as this script:
#    YOUTUBE_API_KEY = "YOUR_API_KEY_HERE"
#
# ============================================================



import os
import csv

import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("YOUTUBE_API_KEY")
if not API_KEY:
    raise RuntimeError("YOUTUBE_API_KEY is not set in the environment or .env file")
CHANNEL_ID = "UCcLQJOfR-MCcI5RtIHFl6Ww"  
BASE_URL = "https://www.googleapis.com/youtube/v3"

def get_playlists():
    url = f"{BASE_URL}/playlists"
    params = {
        "part": "snippet",
        "channelId": CHANNEL_ID,
        "maxResults": 50,
        "key": API_KEY
    }
    playlists = []

    while True:
        data = requests.get(url, params=params).json()
        for item in data.get("items", []):
            playlists.append({
                "id": item["id"],
                "title": item["snippet"]["title"]
            })

        if "nextPageToken" not in data:
            break
        params["pageToken"] = data["nextPageToken"]

    return playlists


def get_videos(playlist_id):
    url = f"{BASE_URL}/playlistItems"
    params = {
        "part": "snippet",
        "playlistId": playlist_id,
        "maxResults": 50,
        "key": API_KEY
    }
    videos = []

    while True:
        data = requests.get(url, params=params).json()
        for item in data.get("items", []):
            videos.append(item["snippet"]["title"])

        if "nextPageToken" not in data:
            break
        params["pageToken"] = data["nextPageToken"]

    return videos


def main():
    playlists = get_playlists()
    rows = []

    for p in playlists:
        print(f"Fetching playlist: {p['title']}")
        videos = get_videos(p["id"])

        for v in videos:
            rows.append({
                "playlist_name": p["title"],
                "video_name": v
            })

    with open("spoken_tutorial.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["playlist_name", "video_name"])
        writer.writeheader()
        writer.writerows(rows)

    print("CSV created: spoken_tutorial.csv")


if __name__ == "__main__":
    main()
