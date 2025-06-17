from tweepy import Client, OAuth1UserHandler
import tweepy
import os

# === Twitter API Credentials ===
CONSUMER_KEY = "GwuG2MAZ65SOKjo0hoV5OWDId"
CONSUMER_SECRET = "s4kOvEpm64LOXmhKd1qQBMR4lHoqPJPf6XfLhNxQOwtAywTewc"
ACCESS_TOKEN = "1934731915082518528-WHJFZpw9KzUC1VLFJ7WSMOEqdjqDQS"
ACCESS_SECRET = "9bnLNoCcDHGdEP061SujIohbVJq1RH5GCEK73TaHWG12g"

# === Paths (unchanged) ===
OUTPUT_DIR = "pollinations_output"
TEXT_PATH = os.path.join(OUTPUT_DIR, "news.txt")
IMAGE_PATH = os.path.join(OUTPUT_DIR, "news.png")

def post_text_and_image():
    # Check content
    if not os.path.exists(TEXT_PATH):
        print("❌ news.txt not found.")
        return
    if not os.path.exists(IMAGE_PATH):
        print("❌ news.png not found.")
        return

    tweet_text = open(TEXT_PATH, "r", encoding="utf-8").read().strip()
    if not tweet_text:
        print("❌ news.txt is empty.")
        return
    if len(tweet_text) > 280:
        tweet_text = tweet_text[:277] + "..."

    # Setup OAuth1.0a for media upload
    auth = OAuth1UserHandler(
        CONSUMER_KEY, CONSUMER_SECRET,
        ACCESS_TOKEN, ACCESS_SECRET
    )
    v1_api = tweepy.API(auth)

    try:
        media = v1_api.media_upload(IMAGE_PATH)
    except Exception as e:
        print(f"❌ Media upload failed: {e}")
        return

    # Setup v2 client (User Context OAuth 1.0a)
    client = Client(
        consumer_key=CONSUMER_KEY,
        consumer_secret=CONSUMER_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_SECRET
    )

    # Post tweet with image via v2
    try:
        response = client.create_tweet(text=tweet_text, media_ids=[media.media_id_string])
        if response.data:
            print("✅ Tweet posted with image. ID:", response.data["id"])
        else:
            print("❌ Tweet posting failed:", response.errors)
    except Exception as e:
        print("❌ Tweet posting error:", e)

if __name__ == "__main__":
    post_text_and_image()