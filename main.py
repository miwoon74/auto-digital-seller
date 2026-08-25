import os
import requests

# GitHub Secrets에서 가져오기
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
GUMROAD_TOKEN = os.getenv("GUMROAD_TOKEN")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram(message):
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": message})

def main():
    print("자동화 스크립트 실행 시작...")
    # 텔레그램 알림 테스트
    send_telegram("🤖 [Auto-Seller] 자동 등록 스크립트가 실행되었습니다!")
    print("완료!")

if __name__ == "__main__":
    main()
