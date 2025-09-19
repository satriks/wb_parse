
from datetime import datetime, timezone
import requests
from DB.ORM import ORM
import logging

logger = logging.getLogger(__name__)

class WBParser():
    def __init__(self, nm_id, rate = 3 ,days = 3):
        self.nm_id = nm_id
        self.rate = rate
        self.days = days
        self.imt_id = ''
        self.db = ORM()
        self._setup_db()

        logger.info(f"Инициализирован трекер для товара {nm_id} с параметрами: rating <= {rate}, days >= {days}")


    def _setup_db(self):
        """Настройка базы данных с обработкой ошибок"""
        try:
            self.db.clear()
            self.db.create_bd()
            logger.info("База данных успешно инициализирована")
        except Exception as e:
            logger.error(f"Ошибка при инициализации БД: {str(e)}")
            raise

    def fetch_feedbacks(self) -> list:
        """Получение отзывов с WB API"""
        if not self.imt_id:
            logger.error("imt_id не определен")
            raise ValueError("imt_id не определен")

        urls = [
            f"https://feedbacks2.wb.ru/feedbacks/v2/{self.imt_id}",
            f"https://feedbacks1.wb.ru/feedbacks/v2/{self.imt_id}"
        ]

        for url in urls:
            try:
                response = requests.get(url, timeout=15)
                response.raise_for_status()
                data = response.json()

                if data.get("feedbacks"):
                    logger.info(f"Получено {len(data['feedbacks'])} отзывов с {url}")
                    return data['feedbacks']

            except requests.exceptions.RequestException as e:
                logger.warning(f"Ошибка запроса отзывов с {url}: {str(e)}")
                continue

        logger.error("Не удалось получить отзывы ни с одного сервера")
        raise ConnectionError("Не удалось получить отзывы")

    def fetch_product_details(self) -> None:
        """Получение информации о товаре для определения imt_id"""
        url = "https://u-card.wb.ru/cards/v4/detail"
        params = {
            "appType": 1,
            "curr": "rub",
            "dest": 123586123,
            "spp": 30,
            "ab_testing": "false",
            "lang": "ru",
            "nm": self.nm_id
        }

        try:
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()

            if not data.get('products'):
                raise ValueError("Товар не найден")

            self.imt_id = data['products'][0]['root']
            logger.info(f"Получен imt_id: {self.imt_id} для товара {self.nm_id}")

        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка запроса данных товара: {str(e)}")
            raise
        except (KeyError, IndexError, ValueError) as e:
            logger.error(f"Ошибка обработки данных товара: {str(e)}")
            raise


    def _is_older_than(self, date_str: str) -> bool:
        """
        Проверяет, является ли дата старше указанного количества дней относительно текущего времени.
        """
        try:

            date_obj = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)
            now = datetime.now(timezone.utc)
            delta = now - date_obj
            return delta.days >= self.days

        except ValueError as e:
            logger.error(f"Неверный формат даты {date_str}: {str(e)}")
            raise

    def filter_feedbacks(self, feedbacks: list) -> list:
        """Фильтрация отзывов по рейтингу и дате"""
        bad_feedbacks = []

        for feedback in feedbacks:
            try:
                rating = feedback.get('productValuation', 5)
                date_str = feedback.get('createdDate')

                if not date_str:
                    logger.warning(f"Отзыв {feedback.get('id')} без даты создания")
                    continue

                is_old = self._is_older_than(date_str)

                if rating <= self.rate:
                    if not is_old:
                        logger.debug(f"Отзыв {feedback['id']} слишком новый, пропускаем")
                        continue
                    bad_feedbacks.append(feedback)
                    logger.debug(f"Отзыв {feedback['id']} добавлен в плохие (оценка: {rating})")

            except Exception as e:
                logger.error(f"Ошибка обработки отзыва {feedback.get('id')}: {str(e)}")
                continue

        logger.info(f"Найдено {len(bad_feedbacks)} плохих отзывов")
        return bad_feedbacks

    def save_feedbacks(self, feedbacks: list) -> None:
        """Сохранение отзывов в БД"""
        success_count = 0

        for feedback in feedbacks:
            try:
                result = self.db.add_feedback(feedback)
                if result:
                    success_count += 1
            except Exception as e:
                logger.error(f"Ошибка сохранения отзыва {feedback.get('id')}: {str(e)}")

        logger.info(f"Успешно сохранено {success_count} из {len(feedbacks)} отзывов")

    def run(self):
        self.fetch_product_details()
        feedbacks = self.fetch_feedbacks()
        clear_feedback = self.filter_feedbacks(feedbacks)
        self.save_feedbacks(clear_feedback)














