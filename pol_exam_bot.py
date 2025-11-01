import os
import time
import json
import asyncio
import requests
import schedule
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from telegram import Bot

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
URL = os.getenv("CHECK_URL")

DATA_FILE = "exam_status.json"

bot = Bot(token=TOKEN)

def get_exam_status():
    """Проверяет статус регистрации на экзамен на сайте."""
    try:
        response = requests.get(URL, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Ищем ключевые фразы на странице
        if "Zapisy otwarte" in soup.text or "Rejestracja otwarta" in soup.text:
            return "open"
        elif "Brak miejsc" in soup.text or "Zamknięta" in soup.text:
            return "closed"
        else:
            return "unknown"
    except Exception as e:
        print(f"[ERROR] {e}")
        return "error"

def load_status():
    """Загружает последний сохраненный статус из файла."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"status": "unknown"}

def save_status(status):
    """Сохраняет текущий статус в файл."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump({"status": status}, f)

async def check_updates():
    """Проверяет изменения статуса и отправляет уведомление при необходимости."""
    current = get_exam_status()
    previous = load_status().get("status")
    
    if current != previous and current != "error":
        save_status(current)
        msg = f"📢 Изменение статуса экзамена!\n\nНовый статус: **{current.upper()}**\nСсылка: {URL}"
        try:
            await bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode="Markdown")
            print(f"[INFO] Notification sent: {current}")
        except Exception as e:
            print(f"[ERROR] Failed to send message: {e}")
    else:
        print(f"[INFO] No change ({current})")

def run_check():
    """Обертка для запуска асинхронной функции в синхронном контексте."""
    asyncio.run(check_updates())

def main():
    """Основная функция для запуска бота."""
    print("[START] PolExamBot запущен...")
    
    # Первая проверка при запуске
    run_check()
    
    # Настройка расписания проверок каждые 2 часа
    schedule.every(2).hours.do(run_check)
    
    print("[INFO] Бот будет проверять сайт каждые 2 часа...")
    
    # Основной цикл
    while True:
        schedule.run_pending()
        time.sleep(30)

if __name__ == "__main__":
    main()

