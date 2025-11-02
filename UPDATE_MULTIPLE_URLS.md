# 🔗 Добавление множественных URL для мониторинга

## ✅ Что изменено

Бот теперь проверяет **8 сайтов** одновременно:

1. https://polonicum.uw.edu.pl/pl/egzaminy-certyfikatowe/
2. https://san.edu.pl/egzaminy-certyfikatowe-z-jezyka-polskiego
3. https://sjo.sggw.edu.pl/egzaminy-certyfikatowe/
4. https://www.sgh.waw.pl/egzamin-panstwowy-z-jezyka-polskiego
5. https://irk.uksw.edu.pl/pl/offer/EGZ/
6. https://www.wum.edu.pl/dla-kandydatow/egzaminy-certyfikatowe
7. https://chowaniak-school.pl/page/egzamin-certyfikatowy
8. https://certyfikatpolski.pl/rejestracja-na-egzamin/

## 📝 Обновление секрета в GitHub

### Шаг 1: Обновите секрет CHECK_URLS

1. Перейдите в ваш репозиторий: `https://github.com/RomanDevelop/exbot`
2. Откройте `Settings` → `Secrets and variables` → `Actions`
3. Найдите секрет **`CHECK_URL`** (старый) - можете его удалить
4. Добавьте новый секрет **`CHECK_URLS`**:
   - Нажмите `New repository secret`
   - **Name:** `CHECK_URLS`
   - **Secret:** (вставьте все URL через запятую)
     ```
     https://polonicum.uw.edu.pl/pl/egzaminy-certyfikatowe/,https://san.edu.pl/egzaminy-certyfikatowe-z-jezyka-polskiego,https://sjo.sggw.edu.pl/egzaminy-certyfikatowe/,https://www.sgh.waw.pl/egzamin-panstwowy-z-jezyka-polskiego,https://irk.uksw.edu.pl/pl/offer/EGZ/,https://www.wum.edu.pl/dla-kandydatow/egzaminy-certyfikatowe,https://chowaniak-school.pl/page/egzamin-certyfikatowy,https://certyfikatpolski.pl/rejestracja-na-egzamin/
     ```
   - Нажмите `Add secret`

### Шаг 2: Проверьте работу

1. Перейдите в `Actions`
2. Запустите workflow вручную (`Run workflow`)
3. Проверьте логи - должны увидеть проверку всех 8 сайтов

## 📊 Формат хранения статусов

Теперь `exam_status.json` хранит статусы для каждого URL отдельно:

```json
{
  "urls": {
    "https://chowaniak-school.pl/page/egzamin-certyfikatowy": "closed",
    "https://polonicum.uw.edu.pl/pl/egzaminy-certyfikatowe/": "open",
    ...
  }
}
```

## 🔔 Уведомления

Теперь вы будете получать отдельное уведомление для **каждого сайта**, когда его статус изменится.

Формат сообщения:
```
📢 PolExamBot: Изменение статуса!

🌐 Сайт: chowaniak-school.pl
📊 Новый статус: OPEN
🔗 https://chowaniak-school.pl/page/egzamin-certyfikatowy
```

## ⚙️ Локальная настройка

Для локального запуска обновите `.env` файл:

```env
TELEGRAM_TOKEN=ваш_токен
TELEGRAM_CHAT_ID=ваш_chat_id
CHECK_URLS=https://polonicum.uw.edu.pl/pl/egzaminy-certyfikatowe/,https://san.edu.pl/egzaminy-certyfikatowe-z-jezyka-polskiego,...
```

Или используйте перенос строки:
```env
CHECK_URLS=https://polonicum.uw.edu.pl/pl/egzaminy-certyfikatowe/
https://san.edu.pl/egzaminy-certyfikatowe-z-jezyka-polskiego
https://sjo.sggw.edu.pl/egzaminy-certyfikatowe/
...
```

---

**Готово!** Теперь бот будет мониторить все 8 сайтов одновременно. 🎉

