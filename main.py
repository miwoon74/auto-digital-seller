import os
import requests
import datetime
import random
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

GEMINI_KEY = os.getenv("GEMINI_API_KEY")
GUMROAD_TOKEN = os.getenv("GUMROAD_TOKEN")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# 기본 템플릿 링크 설정 (본인의 노션/캔바 공유 링크로 자유롭게 교체)
NOTION_MASTER_LINK = "https://www.notion.so/templates"
CANVA_MASTER_LINK = "https://www.canva.com/brand/join"

# 다국어 및 전체 디지털 상품 카테고리 구성
PRODUCT_CATALOG = [
    {
        "type": "Canva Social Media Kit",
        "flag": "🎨",
        "lang": "English",
        "region": "Global US/EU",
        "price": 700,  # $7.00
        "access_link": CANVA_MASTER_LINK,
        "theme": "Aesthetic Instagram Carousel & Story Canva Templates for Business Owners"
    },
    {
        "type": "Canva E-Book & Workbook",
        "flag": "🇰🇷",
        "lang": "Korean with K-Aesthetic",
        "region": "Global K-Culture",
        "price": 500,  # $5.00
        "access_link": CANVA_MASTER_LINK,
        "theme": "K-Aesthetic Minimalist E-Book & Workbook Canva Template"
    },
    {
        "type": "Notion Life OS Planner",
        "flag": "🇺🇸",
        "lang": "English",
        "region": "North America",
        "price": 900,  # $9.00
        "access_link": NOTION_MASTER_LINK,
        "theme": "Aesthetic All-in-One Life OS & Weekly Productivity Tracker"
    },
    {
        "type": "Notion ADHD Focus Planner",
        "flag": "🇯🇵",
        "lang": "Japanese",
        "region": "Japan",
        "price": 500,  # $5.00
        "access_link": NOTION_MASTER_LINK,
        "theme": "Minimalist Zen Habit & Routine Focus Tracker"
    },
    {
        "type": "Printable Daily Planner",
        "flag": "📄",
        "lang": "Spanish",
        "region": "Latin America / Spain",
        "price": 400,  # $4.00
        "access_link": "Direct PDF Download Included",
        "theme": "Planificador Diario A4 Minimalista e Imprimible"
    },
    {
        "type": "AI Prompt Master Handbook",
        "flag": "🤖",
        "lang": "English",
        "region": "Global",
        "price": 600,  # $6.00
        "access_link": "Included in Attached PDF Guide",
        "theme": "ChatGPT & Midjourney Business Prompt Handbook for Solopreneurs"
    }
]

def send_telegram(message):
    """텔레그램 알림 전송"""
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        try:
            requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": message})
        except Exception as e:
            print(f"Telegram alert error: {e}")

def create_pdf_guide(filename, title, category_info, content):
    """PDF 가이드북 자동 생성 (링크 및 사용법 포함)"""
    c = canvas.Canvas(filename, pagesize=letter)
    
    # 헤더
    c.setFont("Helvetica-Bold", 15)
    c.drawString(50, 750, title[:55])
    
    c.setFont("Helvetica-Bold", 10)
    c.setFillColorRGB(0.1, 0.3, 0.8)
    c.drawString(50, 725, f"Access Link / Source: {category_info['access_link']}")
    
    c.setStrokeColorRGB(0.8, 0.8, 0.8)
    c.line(50, 715, 550, 715)

    # 본문 (인코딩 깨짐 방지 안전 처리)
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica", 9)
    text_object = c.beginText(50, 690)
    
    clean_content = content.encode('ascii', 'ignore').decode('ascii')
    lines = clean_content.split('\n')
    for line in lines[:45]:
        text_object.textLine(line[:85])
    
    c.drawText(text_object)
    c.save()

def generate_digital_product():
    """모든 상품 카테고리 중 무작위 선택하여 Gemini 콘텐츠 생성"""
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    selected = random.choice(PRODUCT_CATALOG)

    prompt = f"""
    You are a professional global digital product creator on Gumroad.
    Create a high-converting digital product listing for:
    - Category: {selected['type']}
    - Target Language: {selected['lang']}
    - Target Region: {selected['region']}
    - Concept: {selected['theme']}

    Requirements:
    1. Product Title & Description MUST be in the target language ({selected['lang']}).
    2. Make the description engaging with features, target audience, and call-to-action.
    3. Provide a clear English PDF Quick-Start Guide text for the downloadable file.

    Strict Output Format:
    [TITLE]: Product Title
    [DESCRIPTION]: High-Converting Product Description
    [GUIDE]: PDF Quick Start Guide Text (in English)
    """

    candidate_models = ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-1.5-pro"]
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    headers = {"Content-Type": "application/json"}

    for model in candidate_models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_KEY}"
        res = requests.post(url, json=payload, headers=headers)
        if res.status_code == 200:
            text = res.json()["candidates"][0]["content"]["parts"][0]["text"]
            
            title = f"{selected['theme']} ({today_str})"
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

def create_gumroad_product_with_file(title, description, price, pdf_path):
    """Gumroad에 상품 정보 및 PDF 파일 첨부 등록"""
    url = "https://api.gumroad.com/v2/products"
    
    data = {
        "access_token": GUMROAD_TOKEN,
        "name": title,
        "price": price,
        "description": f"{description}\n\n----------\n📄 Access Link Included: Download the attached PDF guide to access your digital assets immediately.",
    }

    with open(pdf_path, "rb") as f:
        files = {"file": (pdf_path, f, "application/pdf")}
        res = requests.post(url, data=data, files=files)

    if res.status_code in [200, 201]:
        return res.json().get("product", {}).get("short_url", "URL unavailable")
    else:
        raise Exception(f"Gumroad API Error: {res.status_code} - {res.text}")

def main():
    print("🚀 All-in-One Global Digital Product Generator Starting...")
    try:
        # 1. 다각화된 상품 무작위 생성
        cat, title, desc, guide = generate_digital_product()
        print(f"Generated ({cat['flag']} {cat['type']}): {title}")

        # 2. 다운로드용 PDF 가이드북 생성
        pdf_filename = "Digital_Product_Guide.pdf"
        create_pdf_guide(pdf_filename, title, cat, guide)

        # 3. Gumroad 자동 업로드 및 등록
        product_url = create_gumroad_product_with_file(title, desc, cat['price'], pdf_filename)
        print(f"Live on Gumroad: {product_url}")

        # 4. 텔레그램 알림 수신
        price_usd = f"${cat['price'] / 100:.2f} USD"
        msg = f"{cat['flag']} [Auto-Seller Global] New Product Listed!\n\n📌 Title: {title}\n📦 Category: {cat['type']}\n🌍 Target: {cat['region']}\n💰 Price: {price_usd}\n🔗 Link: {product_url}"
        send_telegram(msg)

        if os.path.exists(pdf_filename):
            os.remove(pdf_filename)

    except Exception as e:
        error_msg = f"⚠️ [Auto-Seller Error]: {e}"
        print(error_msg)
        send_telegram(error_msg)

if __name__ == "__main__":
    main()
