import os
import random
import requests
import json

# === CONFIG ===
output_dir = "pollinations_output"
os.makedirs(output_dir, exist_ok=True)

news_text_path = os.path.join(output_dir, "news.txt")
news_image_path = os.path.join(output_dir, "news.png")
themes_file = "themes.txt"

REAL_NEWS_CHANCE = 0.3  # 30% chance to pull from real news
REAL_NEWS_API_KEY = "pub_86937d2624d24772986de8efd9c1bc7f"
REAL_NEWS_ENDPOINT = f"https://newsdata.io/api/1/news?apikey={REAL_NEWS_API_KEY}&language=en&country=us"

GEMINI_API_KEY = "AIzaSyCyvjN_7_kDRU8p0J3ANhbTpQwjcHrJ1gc"
GEMINI_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

HEADERS_GEMINI = {
    "Content-Type": "application/json"
}

# === Load Random Fictional Prompt ===
def load_fictional_theme():
    with open(themes_file, "r", encoding="utf-8") as f:
        themes = [line.strip() for line in f if line.strip()]
    return random.choice(themes)

# === Get Real News Title ===
def fetch_real_news_headline():
    try:
        res = requests.get(REAL_NEWS_ENDPOINT)
        data = res.json()
        if "results" in data:
            headlines = [item["title"] for item in data["results"] if item.get("title")]
            return random.choice(headlines) if headlines else None
    except Exception as e:
        print(f"Error fetching real news: {e}")
    return None

# === Generate Story (Pollinations with fallback to Gemini) ===
def generate_content(prompt_topic, is_real=False):
    if is_real:
        prompt = (
            f"""Write a breaking news article based on this real headline: '{prompt_topic}'. 
            Make it intense, tabloid-style, emotionally charged, and exactly 250 characters long. 
            Must include suspense, drama, or fear avoid poetry or metaphor."""
        )
    else:
        prompt = (
            f"""Write a fictional BREAKING NEWS story for this headline: '{prompt_topic}'. 
            Style must resemble professional tabloid journalism. Be shocking, brief, and dramatic. 
            Exactly 250 characters. No poetic or literary tone. Emphasize fear, danger, or strange developments."""
        )

    # Try Pollinations first
    try:
        encoded_prompt = requests.utils.quote(prompt)
        url = f"https://text.pollinations.ai/{encoded_prompt}"
        response = requests.get(url)
        if response.status_code == 200:
            story = response.text.strip()
            # Adjust to exactly 250 characters
            if len(story) > 250:
                story = story[:250]
            elif len(story) < 250:
                story = story + " " * (250 - len(story))
            return story
        elif response.status_code == 429:
            raise Exception("429 Too Many Requests")
    except Exception as e:
        print(f"Pollinations failed, switching to Gemini: {e}")
        # Fallback to Gemini
        try:
            payload = {
                "contents": [{"parts": [{"text": prompt}]}]
            }
            gemini_url = f"{GEMINI_ENDPOINT}?key={GEMINI_API_KEY}"
            r = requests.post(gemini_url, headers=HEADERS_GEMINI, json=payload)
            if r.status_code == 200:
                data = r.json()
                story = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                # Adjust to exactly 250 characters
                if len(story) > 250:
                    story = story[:250]
                elif len(story) < 250:
                    story = story + " " * (250 - len(story))
                return story
            else:
                raise Exception(f"Gemini text failed: {r.text}")
        except Exception as e2:
            raise Exception(f"Text generation failed: {e2}")

# === Generate Image (Pollinations with fallback to Gemini) ===
def generate_image(prompt):
    try:
        encoded = requests.utils.quote(prompt)
        image_url = f"https://image.pollinations.ai/prompt/{encoded}"
        resp = requests.get(image_url, stream=True)
        if resp.status_code == 200:
            with open(news_image_path, "wb") as f:
                for chunk in resp.iter_content(1024):
                    f.write(chunk)
            return news_image_path
        elif resp.status_code == 429:
            raise Exception("429 Pollinations limit")
        else:
            raise Exception(f"Pollinations image failed: {resp.text}")
    except Exception as e:
        print(f"Pollinations image failed, switching to Gemini: {e}")
        try:
            prompt_gemini = f"Create a detailed news illustration for: {prompt}"
            payload = {
                "contents": [{"parts": [{"text": prompt_gemini}]}]
            }
            gemini_url = f"{GEMINI_ENDPOINT}?key={GEMINI_API_KEY}&model=gemini-1.5-flash"
            r = requests.post(gemini_url, headers=HEADERS_GEMINI, json=payload)
            data = r.json()
            if "candidates" in data and "inlineData" in data["candidates"][0]["content"]["parts"][0]:
                image_data = data["candidates"][0]["content"]["parts"][0]["inlineData"]["data"]
                import base64
                with open(news_image_path, "wb") as img_file:
                    img_file.write(base64.b64decode(image_data))
                return news_image_path
            else:
                raise Exception("Gemini image response malformed")
        except Exception as e2:
            raise Exception(f"Image generation failed: {e2}")

# === Save Story as plain text ===
def save_content(story_text, headline):
    formatted = f"BREAKING NEWS:\n\n\n{story_text}"
    with open(news_text_path, "w", encoding="utf-8") as f:
        f.write(formatted)
    return news_text_path

# === Main Logic ===
def generate_news():
    use_real = random.random() < REAL_NEWS_CHANCE
    if use_real:
        headline = fetch_real_news_headline()
        if not headline:
            headline = load_fictional_theme()
            use_real = False
    else:
        headline = load_fictional_theme()

    print(f"Selected {'REAL' if use_real else 'FICTIONAL'} headline: {headline}")

    story = generate_content(headline, is_real=use_real)
    save_content(story, headline)
    generate_image(story)

    print("News story and image generated.")

# === Execute ===
if __name__ == "__main__":
    generate_news()
