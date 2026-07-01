import requests
import os

USER_ID = 514413

discord_url = "https://discord.com/api/v9/applications/1521891841820069979/users/455056705244364801/identities/0/profile"

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bot {os.getenv('DISCORD_TOKEN')}",
    "User-Agent": "DiscordBot (https://github.com/discord/discord-api-docs, 1.0.0)"
}

# -----------------------------
# 1. AniList Activities
# -----------------------------
query = """
query ($userId: Int) {
  Page(page: 1, perPage: 20) {
    activities(userId: $userId, sort: ID_DESC) {
      __typename

      ... on ListActivity {
        status
        progress
        media {
          type
          title {
            english
            romaji
          }
          coverImage {
            large
          }
        }
      }
    }
  }
}
"""

res = requests.post(
    "https://graphql.anilist.co",
    json={"query": query, "variables": {"userId": USER_ID}}
)

data = res.json()
activities = data["data"]["Page"]["activities"]

# -----------------------------
# 2. 4 Activities bauen
# -----------------------------
list_activities = []

for a in activities:
    if a["__typename"] != "ListActivity":
        continue

    media = a["media"]
    title = media["title"]["english"] or media["title"]["romaji"]
    media_type = media["type"]
    progress = a["progress"]
    cover = media["coverImage"]["large"]

    status_map = {
        "watched episode": "Watched",
        "rewatched episode": "Rewatched",
        "read chapter": "Read",
        "reread chapter": "Reread",
        "watched": "Watched",
        "rewatched": "Rewatched",
        "read": "Read",
        "reread": "Reread"
    }

    pretty_status = status_map.get(
        a["status"],
        a["status"].capitalize() if a["status"] else "Updated"
    )

    if media_type == "ANIME":
        desc = f"{pretty_status} episode {progress}"
    else:
        desc = f"{pretty_status} chapter {progress}"

    list_activities.append({
        "title": title,
        "desc": desc,
        "cover": cover
    })

    if len(list_activities) == 4:
        break

while len(list_activities) < 4:
    list_activities.append({
        "title": "",
        "desc": "",
        "cover": "https://via.placeholder.com/150"
    })

# -----------------------------
# 3. REAL AniList STATS (NEU)
# -----------------------------
stats_query = """
query ($userId: Int) {
  User(id: $userId) {
    statistics {
      anime {
        count
        minutesWatched
      }
      manga {
        count
      }
    }
  }
}
"""

stats_res = requests.post(
    "https://graphql.anilist.co",
    json={"query": stats_query, "variables": {"userId": USER_ID}}
)

stats_data = stats_res.json()["data"]["User"]["statistics"]

total_anime = stats_data["anime"]["count"]
total_manga = stats_data["manga"]["count"]

# minutes → days
days_watched = round(stats_data["anime"]["minutesWatched"] / 1440, 1)

# -----------------------------
# 4. Discord Payload
# -----------------------------
payload = {
    "data": {
        "dynamic": [

            {"type": 3, "name": "Activity Pic 2", "value": {"url": list_activities[0]["cover"]}},
            {"type": 1, "name": "Activity 2", "value": list_activities[0]["title"]},
            {"type": 1, "name": "Activity Description 2", "value": list_activities[0]["desc"]},

            {"type": 3, "name": "Activity Pic 3", "value": {"url": list_activities[1]["cover"]}},
            {"type": 1, "name": "Activity 3", "value": list_activities[1]["title"]},
            {"type": 1, "name": "Activity Description 3", "value": list_activities[1]["desc"]},

            {"type": 3, "name": "Activity Pic 4", "value": {"url": list_activities[2]["cover"]}},
            {"type": 1, "name": "Activity 4", "value": list_activities[2]["title"]},
            {"type": 1, "name": "Activity Description 4", "value": list_activities[2]["desc"]},

            {"type": 3, "name": "Activity Pic 5", "value": {"url": list_activities[3]["cover"]}},
            {"type": 1, "name": "Activity 5", "value": list_activities[3]["title"]},
            {"type": 1, "name": "Activity Description 5", "value": list_activities[3]["desc"]},

            {"type": 1, "name": "Days Watched", "value": str(days_watched)},
            {"type": 1, "name": "Total Manga", "value": str(total_manga)},
            {"type": 1, "name": "Total Anime", "value": str(total_anime)},
        ]
    }
}

# -----------------------------
# 5. PATCH senden
# -----------------------------
response = requests.patch(discord_url, headers=headers, json=payload)

print(response.status_code)
print(response.text)
