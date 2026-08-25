import os
import sys
import requests
import random

GEMINI_KEY = os.getenv("GEMINI_API_KEY")
GUMROAD_TOKEN = os.getenv("GUMROAD_TOKEN")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

NOTION_MASTER_LINK = "https://www.notion.so/templates"
CANVA_MASTER_LINK = "https://www.canva.com/brand/join"

PRODUCT_CATALOG = [
    {
        "type": "Canva Social Media Kit",
        "flag": "🎨",
        "price": 700, # $7.00
        "access_link": CANVA_MASTER_LINK,
        "theme": "Aesthetic Instagram Carousel & Story Canva Templates for Business Coaches"
    },
    {
        "type": "Notion Life OS Planner",
        "flag": "🇺🇸",
        "price": 900, # $9.00
        "access_link": NOTION_MASTER_LINK,
        "theme": "Aesthetic All-in-One Life OS & Weekly Productivity Tracker for Notion"
    },
    {
        "type": "AI Prompt Master Handbook",
        "flag": "🤖",
        "price": 600, # $6.00
        "access_link": NOTION_MASTER_LINK,
        "theme": "ChatGPT & Midjourney Business Prompt Handbook for Solopreneurs"
    }
]

def send_telegram(message):
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        try:
            requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": message}, timeout=10)
        except Exception as e:
            print(f"Telegram alert warning: {e}")

def generate_english_product():
    selected = random.choice(PRODUCT_CATALOG)
    prompt = f"""
    You are a professional digital product copywriter for Gumroad targeting US/Global buyers.
    Write a high-converting digital product listing in 100% ENGLISH ONLY. No Korean allowed.

    Category: {selected['type']}
    Concept: {selected['theme']}

    Requirements:
    1. Title: Catchy, professional English product title without dates.
    2. Description: High-converting English sales copy with features, target audience, and call-to-action.

    Strict Output Format:
    [TITLE]: English Title
    [DESCRIPTION]: English Description
    """

    candidate_models = ["gemini-2.5-flash", "gemini-1.5-flash", "gemini-2.0-flash"]
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    headers = {"Content-Type": "application/json"}

    if GEMINI_KEY:
        for model in candidate_models:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_KEY}"
            try:
                res = requests.post(url, json=payload, headers=headers, timeout=12)
                if res.status_code == 200:
                    text = res.json()["candidates"][0]["content"]["parts"][0]["text"]
                    if "[TITLE]:" in text and "[DESCRIPTION]:" in text:
                        parts = text.split("[DESCRIPTION]:")
                        title = parts[0].replace("[TITLE]:", "").strip()
                        desc = parts[1].strip()
                        return selected, title, desc
            except Exception as e:
                print(f"Model {model} failed: {e}")

    # Fallback default copy
    fallback_title = f"{selected['theme']}"
    fallback_desc = f"""Transform your workflow with this premium {selected['type']}.

✨ KEY BENEFITS:
- Instantly customizable digital assets
- Designed specifically for modern creators and entrepreneurs
- Saves you 10+ hours of setup and design time

👉 Get instant access today and level up your business!"""

    return selected, fallback_title, fallback_desc

def create_gumroad_product(title, description, price, access_link):
    if not GUMROAD_TOKEN:
        raise Exception("GUMROAD_TOKEN environment variable is missing!")

    url = "https://api.gumroad.com/v2/products"
    
    full_description = f"{description}\n\n----------\n🔗 INSTANT ACCESS LINK:\n{access_link}"

    data = {
        "access_token": str(GUMROAD_TOKEN),
        "name": str(title),
        "price": str(price),
        "description": str(full_description),
        "published": "true"
    }

    # Pure form-encoded request without files payload
    res = requests.post(url, data=data, timeout=30)
    res_json = res.json()

    if res.status_code in [200, 201] and res_json.get("success"):
        p_data = res_json.get("product", {})
        product_url = p_data.get("short_url") or p_data.get("url")
        if product_url:
            return product_url

    raise Exception(f"Gumroad API Error ({res.status_code}): {res.text}")

def main():
    print("🚀 Auto-Seller Starting...")
    try:
        config, title, desc = generate_english_product()
        print(f"Generated: {title}")

        product_url = create_gumroad_product(title, desc, config['price'], config['access_link'])
        print(f"✅ Live on Gumroad: {product_url}")

        price_usd = f"${config['price'] / 100:.2f} USD"
        msg = f"{config['flag']} [Auto-Seller US] NEW PRODUCT PUBLISHED!\n\n📌 Title: {title}\n📦 Category: {config['type']}\n💰 Price: {price_usd}\n🔗 Link: {product_url}"
        send_telegram(msg)

    except Exception as e:
        error_msg = f"⚠️ [Auto-Seller Error]: {e}"
        print(error_msg)
        send_telegram(error_msg)
        sys.exit(1)

if __name__ == "__main__":
    main()
