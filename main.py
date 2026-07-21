import requests
import os

USER_ID = 514413

# -----------------------------
# Discord Bot 1
# -----------------------------
discord_url_1 = "https://discord.com/api/v9/applications/1521891841820069979/users/455056705244364801/identities/0/profile"

headers_1 = {
    "Content-Type": "application/json",
    "Authorization": f"Bot {os.getenv('DISCORD_TOKEN')}",
    "User-Agent": "DiscordBot (https://github.com/discord/discord-api-docs, 1.0.0)"
}

# -----------------------------
# Discord Bot 2
# -----------------------------
discord_url_2 = "https://discord.com/api/v9/applications/1524055331209084948/users/455056705244364801/identities/0/profile"

headers_2 = {
    "Content-Type": "application/json",
    "Authorization": f"Bot {os.getenv('DISCORD_TOKEN2')}",
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
        createdAt

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
    json={
        "query": query,
        "variables": {"userId": USER_ID}
    }
)

data = res.json()
activities = data["data"]["Page"]["activities"]


# -----------------------------
# 2. Activities erstellen
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
    from datetime import datetime

activity_time = datetime.fromtimestamp(
    a["createdAt"]
).strftime("%d.%m.%Y %H:%M")

    
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

if pretty_status == "Completed":
    desc = "Completed"

elif media_type == "ANIME":
    if progress:
        desc = f"{pretty_status} episode {progress}"
    else:
        desc = pretty_status

else:
    if progress:
        desc = f"{pretty_status} chapter {progress}"
    else:
        desc = pretty_status

    list_activities.append({
        "title": title,
        "desc": desc,
        "cover": cover
        "time": activity_time
    })

    if len(list_activities) == 5:
        break


while len(list_activities) < 5:
    list_activities.append({
        "title": "",
        "desc": "",
        "cover": "https://via.placeholder.com/150"
        "time": ""
    })


# -----------------------------
# 3. AniList Stats
# -----------------------------
stats_query = """
query ($userId: Int) {
  User(id: $userId) {
    statistics {
      anime {
        count
        minutesWatched
        episodesWatched
        meanScore
      }
      manga {
        count
        chaptersRead
        volumesRead
        meanScore
      }
    }
  }
}
"""

stats_res = requests.post(
    "https://graphql.anilist.co",
    json={
        "query": stats_query,
        "variables": {"userId": USER_ID}
    }
)

stats = stats_res.json()["data"]["User"]["statistics"]

anime_stats = stats["anime"]
manga_stats = stats["manga"]

total_anime = anime_stats["count"]
total_manga = manga_stats["count"]
episodes_watched = anime_stats["episodesWatched"]
days_watched = round(anime_stats["minutesWatched"] / 1440, 1)
mean_score = anime_stats["meanScore"]

manga_mean_score = manga_stats["meanScore"]
chapters_read = manga_stats["chaptersRead"]
volumes_read = manga_stats["volumesRead"]


# -----------------------------
# 4. Payload Bot 1
# -----------------------------
payload_1 = {
    "data": {
        "dynamic": [

            {"type": 3, "name": "Activity Pic 1", "value": {"url": list_activities[0]["cover"]}},
            {"type": 1, "name": "Activity 1", "value": list_activities[0]["title"]},
            {"type": 1, "name": "Activity Description 1", "value": list_activities[0]["desc"]},
            {"type": 1, "name": "Activity Time 1", "value": list_activities[0]["time"]},

            {"type": 3, "name": "Activity Pic 2", "value": {"url": list_activities[1]["cover"]}},
            {"type": 1, "name": "Activity 2", "value": list_activities[1]["title"]},
            {"type": 1, "name": "Activity Description 2", "value": list_activities[1]["desc"]},

            {"type": 3, "name": "Activity Pic 3", "value": {"url": list_activities[2]["cover"]}},
            {"type": 1, "name": "Activity 3", "value": list_activities[2]["title"]},
            {"type": 1, "name": "Activity Description 3", "value": list_activities[2]["desc"]},

            {"type": 3, "name": "Activity Pic 4", "value": {"url": list_activities[3]["cover"]}},
            {"type": 1, "name": "Activity 4", "value": list_activities[3]["title"]},
            {"type": 1, "name": "Activity Description 4", "value": list_activities[3]["desc"]},

            {"type": 3, "name": "Activity Pic 5", "value": {"url": list_activities[4]["cover"]}},
            {"type": 1, "name": "Activity 5", "value": list_activities[4]["title"]},
            {"type": 1, "name": "Activity Description 5", "value": list_activities[4]["desc"]},

            {"type": 1, "name": "Days Watched", "value": str(days_watched)},
            {"type": 1, "name": "Total Manga", "value": str(total_manga)},
            {"type": 1, "name": "Total Anime", "value": str(total_anime)}
        ]
    }
}


# -----------------------------
# 5. Payload Bot 2
# -----------------------------
payload_2 = {
    "data": {
        "dynamic": [
            {
                "type": 1,
                "name": "Total Anime",
                "value": str(total_anime)
            },
            {
                "type": 1,
                "name": "Total Manga",
                "value": str(total_manga)
            },
            {
                "type": 1,
                "name": "Episodes Watched",
                "value": str(episodes_watched)
            },
            {
                "type": 1,
                "name": "Days Watched",
                "value": str(days_watched)
            },
            {
                "type": 1,
                "name": "Mean Score Anime",
                "value": str(mean_score)
            },
            {
                "type": 1,
                "name": "Chapters Read",
                "value": str(chapters_read)
            },
            {
                "type": 1,
                "name": "Volumes Read",
                "value": str(volumes_read)
            },
            {
                "type": 1,
                "name": "Mean Score Manga",
                "value": str(manga_mean_score)
            }
        ]
    }
}


# -----------------------------
# 6. PATCH senden
# -----------------------------
response_1 = requests.patch(
    discord_url_1,
    headers=headers_1,
    json=payload_1
)

response_2 = requests.patch(
    discord_url_2,
    headers=headers_2,
    json=payload_2
)


print("Bot 1:", response_1.status_code)
print(response_1.text)

print("Bot 2:", response_2.status_code)
print(response_2.text)
