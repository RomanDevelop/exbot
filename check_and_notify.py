# check_and_notify.py
import os
import json
import requests
from bs4 import BeautifulSoup

CHECK_URL = os.getenv("CHECK_URL")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
STATUS_FILE = "exam_status.json"

def get_status():
    """Проверяет текущий статус на сайте."""
    try:
        r = requests.get(CHECK_URL, timeout=15)
        r.raise_for_status()
        txt = r.text
        if "Zapisy otwarte" in txt or "Rejestracja otwarta" in txt:
            return "open"
        if "Brak miejsc" in txt or "Zamknięta" in txt or "Zapisy zamknięte" in txt:
            return "closed"
        return "unknown"
    except Exception as e:
        print("Fetch error:", e)
        return "error"

def load_prev():
    """Загружает предыдущий статус из файла."""
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, "r", encoding="utf-8") as f:
            return json.load(f).get("status", "unknown")
    return "unknown"

def save(status):
    """Сохраняет статус в файл."""
    with open(STATUS_FILE, "w", encoding="utf-8") as f:
        json.dump({"status": status}, f)

def notify(status):
    """Отправляет уведомление в Telegram."""
    msg = f"📢 PolExamBot: Изменение статуса!\n\nНовый статус: {status.upper()}\n{CHECK_URL}"
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": msg}
    try:
        resp = requests.post(url, data=data, timeout=10)
        print("Telegram response:", resp.status_code, resp.text)
    except Exception as e:
        print("Telegram error:", e)

def main():
    """Основная функция."""
    cur = get_status()
    prev = load_prev()
    print("prev:", prev, "cur:", cur)
    
    if cur != prev and cur != "error":
        save(cur)
        notify(cur)
        return True
    
    print("No change.")
    return False

if __name__ == "__main__":
    main()

