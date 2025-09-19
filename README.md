# WB Feedback Tracker

Сервис для мониторинга негативных отзывов на Wildberries с сохранением в БД.

##  📌 Основные функции

✔️ Парсинг отзывов по артикулу товара  
✔️ Фильтрация по рейтингу (1-3 звезды)  
✔️ Фильтрация по периоду (последние N дней)  
✔️ Сохранение в SQLite с дедупликацией  
✔️ Логирование всех операций  

##  🛠 Установка

```bash
# 1. Клонировать репозиторий
git clone https://github.com/yourrepo/wb-feedback-tracker.git
cd wb-feedback-tracker

# 2. Установить зависимости
pip install -r requirements.txt
```

## Использование
Основное использование через main.py:
````python

from WB.WBParser import WBFeedbackTracker

# Артикул товара, максимальный рейтинг, количество дней
tracker = WBFeedbackTracker(nm_id=402649345, rate=3, days=3)
tracker.run()


````
## Параметры:

 - nm_id - артикул товара на WB (обязательный)
 - rate - максимальный рейтинг для негативных отзывов (по умолчанию 3)
 - days - количество дней для анализа (по умолчанию 3)
 - 
## Настройка
База данных:

 * По умолчанию используется SQLite (файл wb_feedbacks.db)
 * Для смены БД измените DATABASE_URL в DB/ORM.py

Логирование:

* Конфигурация в logging_config.py
* Логи сохраняются в logs/wb_feedback_tracker.log

Форматы данных:
* Схема БД описана в DB/models.py

