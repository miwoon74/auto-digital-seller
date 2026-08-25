import os
import requests
import datetime

# GitHub Secrets 환경 변수 불러오기
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
GUMROAD_TOKEN = os.getenv("GUMROAD_TOKEN")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram(message):
    """텔레그램 알림 전송"""
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        try:
            requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": message})
        except Exception as e:
            print(f"텔레그램 전송 실패: {e}")

def generate_digital_content():
    """Gemini API로 디지털 상품 내용 생성 (자동 Fallback 재시도 지원)"""
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    prompt = f"""
    당신은 인기 있는 디지털 정보성 전자책 작가입니다.
    오늘 날짜({today_str}) 기준 업무 및 실생활에 바로 유용한 'AI 활용 프롬프트 3선 및 활용 가이드' 전자책 콘텐츠를 작성해 주세요.

    반드시 아래 구분 기호 형식에 맞춰 출력하세요:
    [TITLE]: 상품 제목 (예: [{today_str}] 업무 생산성을 10배 올리는 AI 프롬프트 3선)
    [DESCRIPTION]: 상품 상세 내용 및 프롬프트 본문 전체
    """

    # 우선 시도할 대표 모델 후보군
    candidate_models = [
        "gemini-1.5-flash",
        "gemini-2.0-flash",
        "gemini-2.5-flash",
        "gemini-1.5-pro"
    ]

    # API에서 추가 가능한 모델 목록 가져와 최우선 순위로 배치
    try:
        list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={GEMINI_KEY}"
        res = requests.get(list_url)
        if res.status_code == 200:
            fetched = [
                m.get("name", "").replace("models/", "")
                for m in res.json().get("models", [])
                if "generateContent" in m.get("supportedGenerationMethods", [])
            ]
            for fm in reversed(fetched):
                if fm not in candidate_models:
                    candidate_models.insert(0, fm)
    except Exception as e:
        print(f"모델 목록 조회 참고: {e}")

    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    headers = {"Content-Type": "application/json"}
    last_error = ""

    # 후보 모델들을 순서대로 호출 (200 OK 응답이 나오는 첫 모델 사용)
    for model in candidate_models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_KEY}"
        print(f"Gemini 모델 시도 중: {model}")
        res = requests.post(url, json=payload, headers=headers)
        
        if res.status_code == 200:
            print(f"✅ 사용 가능한 모델 확인: {model}")
            result_text = res.json()["candidates"][0]["content"]["parts"][0]["text"]
            
            title = f"AI 프롬프트 모음집 ({today_str})"
            description = result_text

            if "[TITLE]:" in result_text and "[DESCRIPTION]:" in result_text:
                parts = result_text.split("[DESCRIPTION]:")
                title = parts[0].replace("[TITLE]:", "").strip()
                description = parts[1].strip()

            return title, description
        else:
            last_error = f"{model} ({res.status_code}): {res.text}"
            print(f"⚠️ {model} 호출 실패, 다음 모델로 전환합니다.")

    raise Exception(f"모든 Gemini 모델 호출 실패. 마지막 상세: {last_error}")

def create_gumroad_product(title, description):
    """Gumroad API를 이용한 상품 자동 등록"""
    url = "https://api.gumroad.com/v2/products"
    data = {
        "access_token": GUMROAD_TOKEN,
        "name": title,
        "price": 300,  # 판매 가격: $3.00 (센트 단위 300)
        "description": description,
    }

    res = requests.post(url, data=data)
    if res.status_code in [200, 201]:
        product_data = res.json().get("product", {})
        return product_data.get("short_url", "URL 확인 불가")
    else:
        raise Exception(f"Gumroad API 오류: {res.status_code} - {res.text}")

def main():
    print("🚀 자동 상품 생성 및 등록 시작...")
    
    try:
        # 1. Gemini로 콘텐츠 생성
        print("1. Gemini API 콘텐츠 생성 중...")
        title, description = generate_digital_content()
        print(f"생성 완료: {title}")

        # 2. Gumroad 등록
        print("2. Gumroad에 상품 등록 중...")
        product_url = create_gumroad_product(title, description)
        print(f"등록 성공: {product_url}")

        # 3. 텔레그램 알림
        msg = f"🎉 [Auto-Seller] 새 상품 등록 완료!\n\n📌 제목: {title}\n🔗 판매 링크: {product_url}"
        send_telegram(msg)
        print("3. 텔레그램 알림 전송 완료!")

    except Exception as e:
        error_msg = f"⚠️ [Auto-Seller] 오류 발생:\n{e}"
        print(error_msg)
        send_telegram(error_msg)

if __name__ == "__main__":
    main()
