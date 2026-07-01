import os

token = os.getenv("DISCORD_TOKEN")

print("TOKEN EXISTS:", token is not None)
print("TOKEN START:", token[:5] if token else "NONE")
