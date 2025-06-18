import requests
import os

# === Facebook Page Config ===
PAGE_ID = "720312981155451"
PAGE_ACCESS_TOKEN = "EAAS8uPAUoYwBOZCbCzpfu6EaerxSaA8GzZArNbOK4ycEZBu2FUJC7gVZAAfnQUHp7bXu1RjobRJXD5Fadnfm5DPG37rovoDr29TZBt3o6voatT7fgfLXK2WOZC7daYo5dNO7IDERblYsooLuIbQ2fGPEbY0wo9yeZBDUuU7AA6O6HC2rYpebhxZAMsnwHZCOqrT9iLe5LYEAm"

# === File Paths ===
BASE_DIR = "Facebook"
TEXT_PATH = os.path.join(BASE_DIR, "news.txt")
IMAGE_PATH = os.path.join(BASE_DIR, "news.png")

# === Read Text from File ===
with open(TEXT_PATH, "r", encoding="utf-8") as f:
    caption = f.read().strip()

# === Ensure image and caption are used correctly ===
url = f"https://graph.facebook.com/v19.0/{PAGE_ID}/photos"

payload = {
    "caption": caption,
    "access_token": PAGE_ACCESS_TOKEN
}

files = {
    "source": ("news.png", open(IMAGE_PATH, "rb"), "image/png")
}

response = requests.post(url, data=payload, files=files)
result = response.json()

# === Result Feedback ===
if response.status_code == 200 and "post_id" in result:
    print("[✅] Post published successfully!")
    print(f"Post ID: {result['post_id']}")
else:
    print("[❌] Post failed:")
    print(result)