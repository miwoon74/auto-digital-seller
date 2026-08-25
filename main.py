import os
import requests
import datetime
import random
import textwrap
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from PIL import Image, ImageDraw, ImageFont

GEMINI_KEY = os.getenv("GEMINI_API_KEY")
GUMROAD_TOKEN = os.getenv("GUMROAD_TOKEN")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

NOTION_MASTER_LINK = "https://www.notion.so/templates"
CANVA_MASTER_LINK = "https://www.canva.com/brand/join"

# 북미/글로벌 타깃 100% 영문 상품 카테고리
PRODUCT_CATALOG = [
    {
        "type": "Canva Social Media Kit",
        "flag": "🎨",
        "price": 700, # $7.00
        "access_link": CANVA_MASTER_LINK,
        "base_color": "#E8EAF6", # Indigo Tint
        "accent_color": "#3F51B5",
        "theme": "Aesthetic Instagram Carousel & Story Canva Templates for Business Coaches"
    },
    {
        "type": "Notion Life OS Planner",
        "flag": "🇺🇸",
        "price": 900, # $9.00
        "access_link": NOTION_MASTER_LINK,
        "base_color": "#E1F5FE", # Light Blue
        "accent_color": "#0288D1",
        "theme": "Aesthetic All-in-One Life OS & Weekly Productivity Tracker for Notion"
    },
    {
        "type": "AI Prompt Master Handbook",
        "flag": "🤖",
        "price": 600, # $6.00
        "access_link": "Included in Attached PDF Guide",
        "base_color": "#ECEFF1", # Blue Grey
        "accent_color": "#455A64",
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

def create_product_images(title, flag, base_color, accent_color):
    """Cover (1280x720) 및 Thumbnail (600x600) 이미지 자동 생성"""
    cover_name = "cover.png"
    thumb_name = "thumb.png"
    
    try:
        font_title = ImageFont.truetype("arial.ttf", 55)
        font_sub = ImageFont.truetype("arial.ttf", 28)
    except IOError:
        font_title = ImageFont.load_default(size=38)
        font_sub = ImageFont.load_default(size=20)

    # 1. Cover Image (1280x720)
    cover = Image.new('RGB', (1280, 720), color=base_color)
    draw = ImageDraw.Draw(cover)
    
    draw.rectangle([0, 0, 1280, 20], fill=accent_color)
    draw.rectangle([0, 700, 1280, 720], fill=accent_color)

    draw.text((80, 80), f"{flag} DIGITAL ASSET", fill=accent_color, font=font_sub)
    
    wrapped_title = textwrap.fill(title, width=28)
    draw.multiline_text((80, 180), wrapped_title, fill="#212121", font=font_title, spacing=18)
    
    draw.text((80, 610), "INSTANT DOWNLOAD • FULL ACCESS INCLUDED", fill="#616161", font=font_sub)
    cover.save(cover_name)

    # 2. Thumbnail Image (600x600)
    thumb = Image.new('RGB', (600, 600), color=base_color)
    draw = ImageDraw.Draw(thumb)
    
    draw.rectangle([15, 15, 585, 585], outline=accent_color, width=6)
    draw.text((40, 40), flag, fill=accent_color, font=font_title)
    
    wrapped_thumb = textwrap.fill(title, width=16)
    draw.multiline_text((40, 150), wrapped_thumb, fill="#212121", font=font_sub, spacing=10)
    
    thumb.save(thumb_name)
    return cover_name, thumb_name

def get_candidate_models():
    models = ["gemini-3.6-flash", "gemini-2.5-flash"]
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={GEMINI_KEY}"
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            fetched = [
                m.get("name", "").replace("models/", "")
                for m in res.json().get("models", [])
                if "generateContent" in m.get("supportedGenerationMethods", [])
            ]
            for m in reversed(fetched):
                if m not in models:
                    models.insert(0, m)
    except Exception as e:
        print(f"Model lookup skipped: {e}")
    return models

def generate_digital_product():
    """Gemini API를 호출하여 100% 영문 세일즈 카피 생성"""
    selected = random.choice(PRODUCT_CATALOG)

    prompt = f"""
    You are an expert digital product marketer on Gumroad targeting North American buyers.
    Write a high-converting digital product listing in 100% ENGLISH. DO NOT USE ANY KOREAN.

    Category: {selected['type']}
    Concept: {selected['theme']}

    Requirements:
    1. Title: Professional, catchy English product title without dates.
    2. Description: High-converting English sales copy. Include clear benefits, bullet points of features, who it is for, and a strong CTA.
    3. Guide: English quick-start guide text for the downloadable PDF.

    Output format MUST be strictly:
    [TITLE]: English Title
    [DESCRIPTION]: English Sales Description
    [GUIDE]: English PDF Guide Text
    """

    candidate_models = get_candidate_models()
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    headers = {"Content-Type": "application/json"}

    for model in candidate_models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_KEY}"
        res = requests.post(url, json=payload, headers=headers)
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

    raise Exception("Gemini API generation failed.")

def create_gumroad_product_with_assets(title, description, price, pdf_path, cover_path, thumb_path):
    """Gumroad API를 통해 상품, PDF 파일, Cover, Thumbnail 한 번에 전송"""
    url = "https://api.gumroad.com/v2/products"
    
    data = {
        "access_token": GUMROAD_TOKEN,
        "name": title,
        "price": price,
        "description": f"{description}\n\n----------\n📄 ACCESS LINK INCLUDED: Download the attached PDF guide to duplicate your digital assets instantly.",
        "published": "true" # 🔥 공개 상태로 직행
    }

    with open(pdf_path, "rb") as pdf_f, open(cover_path, "rb") as cover_f, open(thumb_path, "rb") as thumb_f:
        files = {
            "file": (pdf_path, pdf_f, "application/pdf"),
            "cover": (cover_path, cover_f, "image/png"),
            "thumbnail": (thumb_path, thumb_f, "image/png")
        }
        res = requests.post(url, data=data, files=files)

    if res.status_code in [200, 201]:
        p_data = res.json().get("product", {})
        return p_data.get("url") or p_data.get("short_url") or "https://gumroad.com/products"
    else:
        raise Exception(f"Gumroad API Error ({res.status_code}): {res.text}")

def main():
    print("🚀 Auto-Seller Starting (Full English Copy + Image Upload)...")
    temp_files = []
    try:
        # 1. 100% 영문 콘텐츠 생성
        config, title, desc, guide = generate_digital_product()
        print(f"Generated ({config['type']}): {title}")

        # 2. PDF 가이드 생성
        pdf_file = "Digital_Asset_Guide.pdf"
        create_pdf_guide(pdf_file, title, config, guide)
        temp_files.append(pdf_file)

        # 3. 커버 & 썸네일 이미지 파일 생성
        cover_file, thumb_file = create_product_images(title, config['flag'], config['base_color'], config['accent_color'])
        temp_files.extend([cover_file, thumb_file])

        # 4. Gumroad 자동 업로드 및 등록
        product_url = create_gumroad_product_with_assets(title, desc, config['price'], pdf_file, cover_file, thumb_file)
        print(f"Live on Gumroad: {product_url}")

        # 5. 텔레그램 알림 전송
        price_usd = f"${config['price'] / 100:.2f} USD"
        msg = f"{config['flag']} [Auto-Seller US] NEW PRODUCT PUBLISHED!\n\n📌 Title: {title}\n📦 Category: {config['type']}\n💰 Price: {price_usd}\n🔗 Link: {product_url}"
        send_telegram(msg)

    except Exception as e:
        error_msg = f"⚠️ [Auto-Seller Error]: {e}"
        print(error_msg)
        send_telegram(error_msg)

    finally:
        for f in temp_files:
            if os.path.exists(f):
                os.remove(f)

if __name__ == "__main__":
    main()
