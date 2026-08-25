import os
import sys
import requests
import datetime
import random
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

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
        "access_link": "Included in Attached PDF Guide",
        "theme": "ChatGPT & Midjourney Business Prompt Handbook for Solopreneurs"
    }
]

def send_telegram(message):
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        try:
            requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": message}, timeout=10)
        except Exception as e:
            print(f"Telegram alert error: {e}")

def create_pdf_guide(filename, title, category_info, content):
    c = canvas.Canvas(filename, pagesize=letter)
    c.setFont("Helvetica-Bold", 15)
    c.drawString(50, 750, title[:55])
    
    c.setFont("Helvetica-Bold", 10)
    c.setFillColorRGB(0.1, 0.3, 0.8)
    c.drawString(50, 725, f"Access Link / Source: {category_info['access_link']}")
    
    c.setStrokeColorRGB(0.8, 0.8, 0.8)
    c.line(50, 715, 550, 715)

    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica", 9)
    text_object = c.beginText(50, 690)
    
    clean_content = content.encode('ascii', 'ignore').decode('ascii')
    lines = clean_content.split('\n')
    for line in lines[:45]:
        text_object.textLine(line[:85])
    
    c.drawText(text_object)
    c.save()

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
    3. Guide: English quick-start guide text for the downloadable PDF.

    Strict Output Format:
    [TITLE]: English Title
    [DESCRIPTION]: English Description
    [GUIDE]: English PDF Guide Text
    """

    candidate_models = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash"]
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    headers = {"Content-Type": "application/json"}

    for model in candidate_models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_KEY}"
        res = requests.post(url, json=payload, headers=headers, timeout=15)
        if res.status_code == 200:
            text = res.json()["candidates"][0]["content"]["parts"][0]["text"]
            title = selected['theme']
            desc = text
            guide = text

            if "[TITLE]:" in text and "[DESCRIPTION]:" in text and "[GUIDE]:" in text:
                parts = text.split("[DESCRIPTION]:")
                title = parts[0].replace("[TITLE]:", "").strip()
                sub_parts = parts[1].split("[GUIDE]:")
                desc = sub_parts[0].strip()
                guide = sub_parts[1].strip()

            return selected, title, desc, guide

    raise Exception("Gemini API content generation failed.")

def create_gumroad_product(title, description, price, pdf_path):
    url = "https://api.gumroad.com/v2/products"
    data = {
        "access_token": GUMROAD_TOKEN,
        "name": title,
        "price": price,
        "description": f"{description}\n\n----------\n📄 ACCESS LINK INCLUDED: Download the attached PDF guide to duplicate your digital assets instantly.",
        "published": "true"
    }

    with open(pdf_path, "rb") as pdf_f:
        files = {"file": (pdf_path, pdf_f, "application/pdf")}
        res = requests.post(url, data=data, files=files, timeout=30)

    if res.status_code in [200, 201]:
        p_data = res.json().get("product", {})
        return p_data.get("url") or p_data.get("short_url") or "https://gumroad.com/products"
    else:
        raise Exception(f"Gumroad API Error ({res.status_code}): {res.text}")

def main():
    print("🚀 Auto-Seller Starting...")
    pdf_file = "Digital_Asset_Guide.pdf"
    try:
        config, title, desc, guide = generate_english_product()
        print(f"Generated: {title}")

        create_pdf_guide(pdf_file, title, config, guide)
        product_url = create_gumroad_product(title, desc, config['price'], pdf_file)
        print(f"Live on Gumroad: {product_url}")

        price_usd = f"${config['price'] / 100:.2f} USD"
        msg = f"{config['flag']} [Auto-Seller US] NEW PRODUCT PUBLISHED!\n\n📌 Title: {title}\n📦 Category: {config['type']}\n💰 Price: {price_usd}\n🔗 Link: {product_url}"
        send_telegram(msg)

    except Exception as e:
        error_msg = f"⚠️ [Auto-Seller Error]: {e}"
        print(error_msg)
        send_telegram(error_msg)
        sys.exit(1) # GitHub Actions에서 실제 실패를 명확히 판정하도록 처리
    finally:
        if os.path.exists(pdf_file):
            os.remove(pdf_file)

if __name__ == "__main__":
    main()
