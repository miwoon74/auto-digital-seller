import os
import sys
import time
import requests
import random
from PIL import Image, ImageDraw

GEMINI_KEY = os.getenv("GEMINI_API_KEY")
GUMROAD_TOKEN = os.getenv("GUMROAD_TOKEN")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

NOTION_MASTER_LINK = "https://www.notion.so/templates"
CANVA_MASTER_LINK = "https://www.canva.com/brand/join"

PRODUCT_CATALOG = [
    {
        "type": "Canva Social Media Kit",
        "flag": "🇺🇸",
        "lang": "English",
        "price": 700,
        "access_link": CANVA_MASTER_LINK,
        "theme": "Aesthetic Instagram Carousel & Story Templates for Business Coaches"
    },
    {
        "type": "Notion Life OS Planner",
        "flag": "🇯🇵",
        "lang": "Japanese",
        "price": 900,
        "access_link": NOTION_MASTER_LINK,
        "theme": "Aesthetic All-in-One Life OS & Weekly Productivity Tracker"
    },
    {
        "type": "AI Prompt Master Handbook",
        "flag": "🇪🇸",
        "lang": "Spanish",
        "price": 600,
        "access_link": NOTION_MASTER_LINK,
        "theme": "ChatGPT & Midjourney Business Prompt Handbook for Solopreneurs"
    },
    {
        "type": "Digital Finance Tracker",
        "flag": "🇩🇪",
        "lang": "German",
        "price": 800,
        "access_link": NOTION_MASTER_LINK,
        "theme": "Minimalist Monthly Budget & Investment Portfolio Tracker for Notion"
    },
    {
        "type": "Brand Identity Starter Kit",
        "flag": "🇫🇷",
        "lang": "French",
        "price": 1200,
        "access_link": CANVA_MASTER_LINK,
        "theme": "Modern Brand Guidelines & Logo Style Guide Canva Kit"
    },
    {
        "type": "Freelancer Client Portal",
        "flag": "🇮🇹",
        "lang": "Italian",
        "price": 1500,
        "access_link": NOTION_MASTER_LINK,
        "theme": "Notion Client Onboarding & Project Management Dashboard"
    },
    {
        "type": "Content Planner 365",
        "flag": "🇧🇷",
        "lang": "Portuguese",
        "price": 950,
        "access_link": NOTION_MASTER_LINK,
        "theme": "365-Day Social Media Content Calendar & Idea Bank"
    },
    {
        "type": "Ebook Lead Magnet Template",
        "flag": "🇳🇱",
        "lang": "Dutch",
        "price": 850,
        "access_link": CANVA_MASTER_LINK,
        "theme": "High-Converting Ebook & Workbook Canva Layout Kit"
    },
    {
        "type": "Ultimate Career Resume",
        "flag": "🇸🇪",
        "lang": "Swedish",
        "price": 500,
        "access_link": CANVA_MASTER_LINK,
        "theme": "Professional Resume & Portfolio Template for Tech Professionals"
    },
    {
        "type": "Solopreneur SaaS Dashboard",
        "flag": "🌐",
        "lang": "English",
        "price": 1100,
        "access_link": NOTION_MASTER_LINK,
        "theme": "SaaS Subscription & Monthly Recurring Revenue Tracker"
    }
]

COLOR_PALETTES = [
    {"bg": (20, 24, 33), "accent": (255, 107, 129), "box": (32, 38, 52)},
    {"bg": (28, 20, 33), "accent": (107, 185, 255), "box": (42, 30, 50)},
    {"bg": (18, 30, 28), "accent": (129, 255, 107), "box": (28, 48, 44)},
    {"bg": (33, 24, 20), "accent": (255, 210, 107), "box": (50, 38, 30)},
    {"bg": (24, 24, 28), "accent": (210, 107, 255), "box": (38, 38, 45)}
]

def send_telegram(message):
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        try:
            requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": message}, timeout=10)
        except Exception as e:
            print(f"Telegram alert warning: {e}")

def create_images(title, category, lang_name, index):
    palette = COLOR_PALETTES[index % len(COLOR_PALETTES)]
    
    # 1. Cover Image (1280x720)
    c_width, c_height = 1280, 720
    cover_img = Image.new("RGB", (c_width, c_height), color=palette["bg"])
    draw_c = ImageDraw.Draw(cover_img)
    draw_c.rectangle([40, 40, c_width - 40, c_height - 40], outline=palette["accent"], width=5)
    draw_c.rectangle([80, 80, c_width - 80, 160], fill=palette["box"])
    draw_c.text((110, 105), f"VOL.{index + 1} [{lang_name.upper()}] | {category.upper()}", fill=palette["accent"])

    words = title.split()
    lines, current_line = [], []
    for word in words:
        current_line.append(word)
        if len(" ".join(current_line)) > 30:
            lines.append(" ".join(current_line[:-1]))
            current_line = [word]
    if current_line:
        lines.append(" ".join(current_line))

    y_offset = 240
    for line in lines[:4]:
        draw_c.text((100, y_offset), line, fill=(255, 255, 255))
        y_offset += 60

    draw_c.rectangle([100, 560, 420, 620], fill=palette["accent"])
    draw_c.text((130, 580), "INSTANT TEMPLATE ACCESS", fill=(255, 255, 255))
    cover_file = f"cover_{index + 1}.png"
    cover_img.save(cover_file)

    # 2. Thumbnail Image (600x600)
    t_size = 600
    thumb_img = Image.new("RGB", (t_size, t_size), color=palette["bg"])
    draw_t = ImageDraw.Draw(thumb_img)
    draw_t.rectangle([20, 20, t_size - 20, t_size - 20], outline=palette["accent"], width=4)
    draw_t.rectangle([40, 50, t_size - 40, 110], fill=palette["box"])
    draw_t.text((60, 70), f"VOL.{index + 1} [{lang_name.upper()}] {category.upper()}", fill=palette["accent"])

    t_y = 160
    for line in lines[:3]:
        draw_t.text((50, t_y), line, fill=(255, 255, 255))
        t_y += 50

    draw_t.rectangle([50, 480, 350, 530], fill=palette["accent"])
    draw_t.text((70, 495), "DIGITAL DOWNLOAD", fill=(255, 255, 255))
    thumb_file = f"thumbnail_{index + 1}.png"
    thumb_img.save(thumb_file)

    return cover_file, thumb_file

def upload_image_and_get_url(image_path):
    try:
        with open(image_path, "rb") as f:
            res = requests.post("https://tmpfiles.org/api/v1/upload", files={"file": f}, timeout=15)
            if res.status_code == 200:
                data = res.json()
                raw_url = data.get("data", {}).get("url", "")
                if raw_url:
                    return raw_url.replace("tmpfiles.org/", "tmpfiles.org/dl/")
    except Exception as e:
        print(f"Image upload warning for {image_path}: {e}")
    return None

def generate_multilingual_product(item):
    prompt = f"""
    You are a professional digital product copywriter for Gumroad targeting global buyers.
    Write a high-converting digital product listing in 100% {item['lang'].upper()} ONLY. No Korean.

    Category: {item['type']}
    Concept: {item['theme']}

    Requirements:
    1. Title: Catchy, professional product title in {item['lang']}.
    2. Description: High-converting sales copy with features, benefits, and call-to-action in {item['lang']}.

    Strict Output Format:
    [TITLE]: Title in {item['lang']}
    [DESCRIPTION]: Description in {item['lang']}
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
                        return item, title, desc
            except Exception as e:
                print(f"Model {model} failed: {e}")

    fallback_title = f"{item['theme']}"
    fallback_desc = f"Premium {item['type']} template designed for modern creators."
    return item, fallback_title, fallback_desc

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

    res = requests.post(url, data=data, timeout=30)
    res_json = res.json()

    if res.status_code in [200, 201] and res_json.get("success"):
        p_data = res_json.get("product", {})
        return p_data.get("short_url") or p_data.get("url")

    raise Exception(f"Gumroad API Error ({res.status_code}): {res.text}")

def main():
    print("🚀 Auto-Seller Starting Batch Upload...")
    success_count = 0

    for idx, item in enumerate(PRODUCT_CATALOG):
        cover_file, thumb_file = f"cover_{idx + 1}.png", f"thumbnail_{idx + 1}.png"
        try:
            print(f"\n[Product {idx + 1}/10] Language: {item['lang']} - {item['type']}")
            config, title, desc = generate_multilingual_product(item)

            # 이미지 생성 및 온라인 다운로드 링크 생성
            cover_file, thumb_file = create_images(title, config['type'], config['lang'], idx)
            cover_url = upload_image_and_get_url(cover_file)
            thumb_url = upload_image_and_get_url(thumb_file)

            # Gumroad 텍스트 기반 상품 생성
            product_url = create_gumroad_product(title, desc, config['price'], config['access_link'])
            print(f"✅ Live on Gumroad [{config['lang']}] #{idx + 1}: {product_url}")
            success_count += 1

            price_usd = f"${config['price'] / 100:.2f} USD"
            
            # 텔레그램으로 이미지 다운로드 링크 및 상품 관리 링크 원스톱 발송
            msg = (
                f"{config['flag']} [Auto-Seller {config['lang'].upper()} #{idx + 1}] NEW PRODUCT!\n\n"
                f"📌 Title: {title}\n"
                f"💰 Price: {price_usd}\n"
                f"🔗 Product: {product_url}\n\n"
                f"🖼️ Cover Download:\n{cover_url or 'Failed'}\n\n"
                f"🖼️ Thumbnail Download:\n{thumb_url or 'Failed'}"
            )
            send_telegram(msg)

            time.sleep(2)

        except Exception as e:
            print(f"⚠️ Error processing product #{idx + 1}: {e}")
        finally:
            for f in [cover_file, thumb_file]:
                if os.path.exists(f):
                    os.remove(f)

    print(f"\n🎉 Completed! {success_count}/10 Multilingual Products successfully published.")

if __name__ == "__main__":
    main()
