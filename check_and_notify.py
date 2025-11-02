# check_and_notify.py
import os
import json
import requests
from bs4 import BeautifulSoup

# Загружаем переменные из .env файла (если файл существует и dotenv установлен)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # В GitHub Actions dotenv не нужен, переменные передаются через env:
    pass

# Получаем список URL для проверки (разделенные запятой или переносом строки)
CHECK_URLS_STR = os.getenv("CHECK_URLS", "").strip()
if CHECK_URLS_STR:
    # Если указаны через запятую или перенос строки
    CHECK_URLS = [url.strip() for url in CHECK_URLS_STR.replace('\n', ',').split(',') if url.strip()]
else:
    # Fallback на старый CHECK_URL для обратной совместимости
    old_url = os.getenv("CHECK_URL", "")
    CHECK_URLS = [old_url] if old_url else []

# Если ничего не указано, используем список по умолчанию
if not CHECK_URLS:
    CHECK_URLS = [
        "https://polonicum.uw.edu.pl/pl/egzaminy-certyfikatowe/",
        "https://san.edu.pl/egzaminy-certyfikatowe-z-jezyka-polskiego",
        "https://sjo.sggw.edu.pl/egzaminy-certyfikatowe/",
        "https://www.sgh.waw.pl/egzamin-panstwowy-z-jezyka-polskiego",
        "https://irk.uksw.edu.pl/pl/offer/EGZ/",
        "https://www.wum.edu.pl/dla-kandydatow/egzaminy-certyfikatowe",
        "https://chowaniak-school.pl/page/egzamin-certyfikatowy",
        "https://certyfikatpolski.pl/rejestracja-na-egzamin/"
    ]

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
STATUS_FILE = "exam_status.json"

def get_status(url):
    """Проверяет текущий статус на конкретном сайте."""
    try:
        # Используем более реалистичные заголовки для обхода защиты
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        r = requests.get(url, timeout=15, headers=headers, allow_redirects=True, verify=True)
        
        # Проверяем статус код - не все 4xx являются критичными
        if r.status_code >= 500:
            print(f"Server error {r.status_code} for {url}")
            return "error"
        
        # Даже если 404, попробуем проверить содержимое (может быть редирект или кастомная страница)
        if r.status_code == 404:
            # Проверяем, может быть это кастомная 404 страница с информацией
            txt = r.text
            if len(txt) > 100:  # Если страница не пустая, возможно там есть информация
                pass  # Продолжаем проверку
            else:
                print(f"Page not found (404) for {url}")
                return "error"
        
        # Для всех остальных статусов продолжаем
        txt = r.text
        
        # Ищем ключевые фразы (расширенный поиск)
        txt_lower = txt.lower()
        
        # Фразы для "открыто"
        open_phrases = [
            "zapisy otwarte", "rejestracja otwarta", "zapisy są otwarte",
            "zapisy trwają", "możliwość rejestracji", "rekrutacja otwarta",
            "zapisz się", "dostępne miejsca", "wolne miejsca"
        ]
        
        # Фразы для "закрыто"
        closed_phrases = [
            "brak miejsc", "zamknięta", "zapisy zamknięte", "brak wolnych miejsc",
            "zapisy zakończone", "rekrutacja zamknięta", "nie ma miejsc",
            "brak miejsca", "zapisy zostały zamknięte"
        ]
        
        for phrase in open_phrases:
            if phrase in txt_lower:
                return "open"
        
        for phrase in closed_phrases:
            if phrase in txt_lower:
                return "closed"
        
        return "unknown"
        
    except requests.exceptions.Timeout:
        print(f"Timeout error for {url}")
        return "error"
    except requests.exceptions.ConnectionError:
        print(f"Connection error for {url}")
        return "error"
    except requests.exceptions.TooManyRedirects:
        print(f"Too many redirects for {url}")
        return "error"
    except Exception as e:
        print(f"Fetch error for {url}: {type(e).__name__}: {e}")
        return "error"

def load_prev():
    """Загружает предыдущие статусы из файла."""
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Поддержка старого формата {"status": "..."} для обратной совместимости
            if "status" in data and "urls" not in data:
                # Конвертируем старый формат в новый
                return {CHECK_URLS[0] if CHECK_URLS else "": data.get("status", "unknown")}
            return data.get("urls", {})
    return {}

def save(statuses):
    """Сохраняет статусы всех URL в файл."""
    with open(STATUS_FILE, "w", encoding="utf-8") as f:
        json.dump({"urls": statuses}, f, indent=2)

def notify(url, status):
    """Отправляет уведомление в Telegram о изменении статуса конкретного URL."""
    # Короткое имя сайта из URL
    site_name = url.split("//")[1].split("/")[0] if "//" in url else url
    
    msg = f"📢 PolExamBot: Изменение статуса!\n\n🌐 Сайт: {site_name}\n📊 Новый статус: {status.upper()}\n🔗 {url}"
    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": msg}
    try:
        resp = requests.post(telegram_url, data=data, timeout=10)
        print(f"Telegram response for {url}: {resp.status_code}")
        if resp.status_code != 200:
            print(f"Telegram error: {resp.text}")
    except Exception as e:
        print(f"Telegram error for {url}: {e}")

def main():
    """Основная функция - проверяет все URL."""
    prev_statuses = load_prev()
    current_statuses = {}
    changes_found = False
    
    print(f"Проверяю {len(CHECK_URLS)} сайтов...")
    
    for url in CHECK_URLS:
        if not url:
            continue
            
        print(f"\nПроверяю: {url}")
        cur_status = get_status(url)
        prev_status = prev_statuses.get(url, "unknown")
        
        current_statuses[url] = cur_status
        
        print(f"  Предыдущий статус: {prev_status}")
        print(f"  Текущий статус: {cur_status}")
        
        if cur_status != prev_status and cur_status != "error":
            print(f"  ✅ ИЗМЕНЕНИЕ ОБНАРУЖЕНО!")
            notify(url, cur_status)
            changes_found = True
        else:
            if cur_status == "error":
                print(f"  ⚠️ Ошибка при проверке, пропускаю уведомление")
            else:
                print(f"  ℹ️ Изменений нет")
    
    # Сохраняем все статусы
    if changes_found:
        save(current_statuses)
        print("\n✅ Изменения сохранены!")
    else:
        print("\nℹ️ Изменений не обнаружено на всех сайтах.")
    
    return changes_found

if __name__ == "__main__":
    main()
