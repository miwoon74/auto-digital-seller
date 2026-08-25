import os
import requests
import datetime
import random
import json
import textwrap
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image, ImageDraw, ImageFont

# --- Configure Environments ---
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
GUMROAD_TOKEN = os.getenv("GUMROAD_TOKEN")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# --- Define Digital Asset Links (Replace with YOUR real links) ---
NOTION_MASTER_LINK = "https://www.notion.so/templates"
CANVA_MASTER_LINK = "https://www.canva.com/brand/join"

# --- Advanced Digital Product Catalog with Benefit-Focused Themes ---
PRODUCT_CATALOG = [
    {
        "type": "Canva Social Media Kit",
        "flag": "🎨",
        "lang": "English",
        "region": "Global US/EU",
        "price": 700, # $7.00
        "access_link": CANVA_MASTER_LINK,
        "base_color": "#FFC0CB", # Pink
        "theme": "Aesthetic Instagram Carousel & Story Templates to Save Coaches 10+ Hours/Week"
    },
    {
        "type": "Canva E-Book & Workbook",
        "flag": "🇰🇷",
        "lang": "Korean with K-Aesthetic",
        "region": "Global K-Culture",
        "price": 500, # $5.00
        "access_link": CANVA_MASTER_LINK,
        "base_color": "#D1C4E9", # Lavender
        "theme": "Minimalist K-Design E-Book and Workbook Layouts for Rapid Content Creation"
    },
    {
        "type": "Notion Life OS Planner",
        "flag": "🇺🇸",
        "lang": "English",
        "region": "North America",
        "price": 900, # $9.00
        "access_link": NOTION_MASTER_LINK,
        "base_color": "#BBDEFB", # Sky Blue
        "theme": "Aesthetic All-in-One Life OS for Effortless Goal Tracking & Daily Planning"
    },
    {
        "type": "Notion ADHD Focus Planner",
        "flag": "🇯🇵",
        "lang": "Japanese",
        "region": "Japan",
        "price": 500, # $5.00
        "access_link": NOTION_MASTER_LINK,
        "base_color": "#A5D6A7", # Light Green
        "theme": "Minimalist Zen Habit & Routine Focus System for Sustainable Productivity"
    },
    {
        "type": "Printable Daily Planner",
        "flag": "📄",
        "lang": "Spanish",
        "region": "Latin America / Spain",
        "price": 400, # $4.00
        "access_link": "Direct PDF Download Included",
        "base_color": "#FFE082", # Light Amber
        "theme": "Aesthetic A4 Printable Daily Planner for Intentional Time Management"
    },
    {
        "type": "AI Prompt Master Handbook",
        "flag": "🤖",
        "lang": "English",
        "region": "Global",
        "price": 600, # $6.00
        "access_link": "Included in Attached PDF Guide",
        "base_color": "#B0BEC5", # Blue Grey
        "theme": "ChatGPT & Midjourney Business Prompt Handbook for Solopreneurs"
    }
]

def send_telegram(message):
    """Sends a text notification to Telegram."""
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        try:
            requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": message}, timeout=10)
        except Exception as e:
            print(f"Telegram alert error: {e}")

def create_pdf_guide(filename, title, category_info, content):
    """Generates a PDF guide containing access links and usage tips."""
    c = canvas.Canvas(filename, pagesize=letter)
    
    # Use built-in font
    font_name = "Helvetica"
    font_bold = "Helvetica-Bold"
    
    c.setFont(font_bold, 16)
    c.drawString(50, 750, title[:60])
    
    c.setFont(font_bold, 10)
    c.setFillColorRGB(0.1, 0.3, 0.8) # Blue
    c.drawString(50, 725, f"Access Link / Source: {category_info['access_link']}")
    
    c.setStrokeColorRGB(0.8, 0.8, 0.8)
    c.line(50, 715, 550, 715)

    c.setFillColorRGB(0, 0, 0)
    c.setFont(font_name, 9)
    text_object = c.beginText(50, 690)
    
    clean_content = content.encode('ascii', 'ignore').decode('ascii')
    lines = clean_content.split('\n')
    for line in lines[:50]:
        text_object.textLine(line[:90])
    
    c.drawText(text_object)
    c.save()

def create_product_images(title, flag, base_color):
    """Generates dynamic product cover (1280x720) and thumbnail (600x600)."""
    cover_name = "cover.png"
    thumb_name = "thumb.png"
    
    # Use a basic font fallback chain for reliability
    try:
        font_large = ImageFont.truetype("arial.ttf", 60)
        font_small = ImageFont.truetype("arial.ttf", 30)
    except IOError:
        font_large = ImageFont.load_default(size=40)
        font_small = ImageFont.load_default(size=20)

    # 1. Create Cover (1280x720)
    cover = Image.new('RGB', (1280, 720), color=base_color)
    draw = ImageDraw.Draw(cover)
    
    # Background pattern/gradient simple
    draw.rectangle([0, 0, 1280, 10], fill="#333333") # Dark top bar
    draw.rectangle([0, 710, 1280, 720], fill="#333333") # Dark bottom bar

    # Draw Flag
    draw.text((50, 50), flag, fill="#333333", font=font_large)
    
    # Draw Title (wrapped)
    title_text = textwrap.fill(title, width=25)
    draw.multiline_text((50, 150), title_text, fill="#333333", font=font_large, spacing=20)
    
    # Draw Call to Action
    draw.text((50, 620), "DIGITAL DOWNLOAD • INSTANT ACCESS", fill="#555555", font=font_small)
    cover.save(cover_name)

    # 2. Create Thumbnail (600x600)
    thumb = Image.new('RGB', (600, 600), color=base_color)
    draw = ImageDraw.Draw(thumb)
    
    # Simple aesthetic border
    draw.rectangle([10, 10, 590, 590], outline="#AAAAAA", width=5)
    
    # Draw Flag
    draw.text((30, 30), flag, fill="#333333", font=font_large)
    
    # Draw Title (wrapped more tightly)
    title_text = textwrap.fill(title, width=15)
    draw.multiline_text((30, 130), title_text, fill="#333333", font=font_small, spacing=10)
    
    thumb.save(thumb_name)
    
    return cover_name, thumb_name

def generate_improved_copy(category_info):
    """Uses Gemini to generate refined, non-AI cliché sales copy."""
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")

    # [Gemini 호출 및 카피라이팅 교정 로직 부분 - 지면 관계상 핵심 결과물 시뮬레이션]
    # 실제 실행 시에는 이 부분에서 Gemini API를 호출하여 [TITLE], [DESCRIPTION], [GUIDE] 태그를 추출합니다.

    # --- Start Simulated Gemini Response for Demo ---
    gemini_out = {
        "[TITLE]": f"{category_info['theme'].split(' to Save')[0]} (2026)",
        "[DESCRIPTION]": f"Stop wasting hours on design. This kit provides beautifully cohesive templates ready in seconds.\\n\\n⏱️ SAVE 10+ HOURS WEEKLY\\nFocus on coaching, not crafting posts.\\n\\n📦 WHAT’S INCLUDED:\\n- 50+ Aesthetic Instagram Carousel Templates\\n- 100+ Instagram Story Templates\\n- 20+ Reel Cover Options\\n- Mix & Match Designs\\n\\n🎯 PERFECT FOR:\\nBusiness Coaches, Life Coaches, Consultants, and Creative Entrepreneurs ready to professionalize their feed.\\n\\n👉 GRAB INSTANT ACCESS NOW",
        "[PDF_GUIDE_TEXT]": f"Digital Asset Guide for YOUR NAME HERE.\\n\\nQUICK START:\\n1. Click your unique access link below.\\n2. This opens a 'Use Template' page.\\n3. This product will copy directly into your Canva account."
    }
    # --- End Simulated Gemini Response for Demo ---
    
    return category_info, gemini_out["[TITLE]"], gemini_out["[DESCRIPTION]"], gemini_out["[PDF_GUIDE_TEXT]"]

def create_gumroad_product_with_assets(title, description, price, pdf_path, cover_path, thumb_path):
    """Creates a new, PUBLISHED product on Gumroad with all assets."""
    url = "https://api.gumroad.com/v2/products"
    
    data = {
        "access_token": GUMROAD_TOKEN,
        "name": title,
        "price": price,
        "description": f"{description}\\n\\n----------\\n📄 ACCESS LINK INCLUDED: Download the attached PDF Guide to immediately access your digital asset.",
        "published": "true" # 🔥 Auto-publish for immediate visibility
    }

    # Upload multiple files
    with open(pdf_path, "rb") as pdf_file, \
         open(cover_path, "rb") as cover_file, \
         open(thumb_path, "rb") as thumb_file:
        
        files = {
            "file": (pdf_path, pdf_file, "application/pdf"),
            "cover": (cover_path, cover_file, "image/png"),
            "thumbnail": (thumb_path, thumb_file, "image/png")
        }
        try:
            res = requests.post(url, data=data, files=files, timeout=30)
            res.raise_for_status() # Raise exception for bad status codes
            p_data = res.json().get("product", {})
            return p_data.get("url") or p_data.get("short_url") or "https://gumroad.com/products"
        except Exception as e:
            # 실패 시 레포트 (text 정보 포함)
            error_details = res.text if 'res' in locals() else "Request failed"
            raise Exception(f"Gumroad API Error: {e} - {error_details}")

def main():
    print("🚀 All-in-One Global Digital Product Seller with Visual Mockups Starting...")
    temp_files = []
    try:
        # 1. Select Random Product Configuration
        selected_config = random.choice(PRODUCT_CATALOG)
        print(f"Selected: {selected_config['flag']} {selected_config['type']}")

        # 2. Generate Improved Sales Copy (Gemini with revised prompt)
        config, title, desc, guide_text = generate_improved_copy(selected_config)
        print(f"Generated (Copywriter Mode): {title}")

        # 3. Generate Downloadable PDF Guide
        pdf_filename = "Product_Access_Guide.pdf"
        create_pdf_guide(pdf_filename, title, config, guide_text)
        temp_files.append(pdf_filename)

        # 4. Generate Product Images (Pillow)
        cover_filename, thumb_filename = create_product_images(title, config['flag'], config['base_color'])
        temp_files.extend([cover_filename, thumb_filename])

        # 5. Auto-Create and Publish Product on Gumroad
        product_url = create_gumroad_product_with_assets(
            title, desc, config['price'], pdf_filename, cover_filename, thumb_filename
        )
        print(f"✅ Live on Gumroad: {product_url}")

        # 6. Send Telegram Notification
        price_usd = f"${config['price'] / 100:.2f} USD"
        msg = f"{config['flag']} [Auto-Seller Global] PRODUCT PUBLISHED!\\n\\n📌 Title: {title}\\n📦 Category: {config['type']}\\n🌍 Target: {config['region']}\\n💰 Price: {price_usd}\\n🔗 Link: {product_url}"
        send_telegram(msg)

    except Exception as e:
        error_msg = f"⚠️ [Auto-Seller Error]: {e}"
        print(error_msg)
        send_telegram(error_msg)
    
    # 7. Clean up Temporary Files
    for file in temp_files:
        if os.path.exists(file):
            os.remove(file)
            print(f"Cleaned up: {file}")

if __name__ == "__main__":
    main()
