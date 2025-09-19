import json
import logging
from datetime import datetime
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database
from DB.models import Base, WBFeedback

logger = logging.getLogger(__name__)
class ORM(object):
    def __init__(self):
        self.DATABASE_URL = "sqlite:///wb_feedbacks.db"
        self.engine = None
        self.Session = None
        self.connect() # Проверяем существование таблиц при инициализации

    def connect(self):
        """Установка соединения с базой данных"""
        try:
            self.engine = create_engine(self.DATABASE_URL)
            self.Session = sessionmaker(bind=self.engine)
            self._ensure_tables_exist()
            logger.info("Успешное подключение к базе данных")
        except Exception as e:
            logger.error(f"Ошибка подключения к БД: {str(e)}")
            raise

    def _ensure_tables_exist(self):
        """Проверка и создание таблиц при необходимости"""
        inspector = inspect(self.engine)

        try:
            if not inspector.has_table("wb_feedbacks"):
                logger.warning("Таблица wb_feedbacks не найдена, создаем...")
                self.create_db()
        except Exception as e:
            logger.error(f"Ошибка проверки таблиц: {str(e)}")
            raise
    def create_db(self):
        """Создание структуры базы данных"""
        try:
            Base.metadata.create_all(self.engine)
            logger.info("База данных успешно создана")
        except Exception as e:
            logger.error(f"Ошибка создания БД: {str(e)}")
            raise
    def check_bd(self):
        """Проверяет существование базы данных"""
        engine = create_engine(self.DATABASE_URL)
        if not database_exists(engine.url):
            create_database(engine.url)
        # print(f'База данных {self.DATABASE_URL.split("/")[-1]} создана: {database_exists(engine.url)}')
        engine.dispose()

    def clear(self):
        """Очищает все таблицы"""
        Base.metadata.drop_all(self.engine)
        logger.info(f"База данных очищена")
        # print("Все таблицы удалены")
        self.engine.dispose()

    def create_bd(self):
        """Создает все таблицы"""
        self.check_bd()
        Base.metadata.create_all(self.engine)

        # print('Таблицы созданы, база готова к работе\n')
        self.engine.dispose()

    def add_feedback(self, feed_data):
        """Добавляет отзыв в базу данных"""
        with self.Session() as session:
            # Проверяем, есть ли ответ от продавца
            answer = feed_data.get('answer')
            existing = session.query(WBFeedback).get(feed_data['id'])
            if existing:
                logger.warning(f"Отзыв {feed_data['id']} уже существует, пропускаем")
                return False
            try:

                video_data = feed_data.get('video')
                video = json.dumps(video_data) if video_data and isinstance(video_data, dict) else None

                feedback = WBFeedback(

                    id=feed_data.get('id', ''),
                    pros=feed_data.get('pros', ''),
                    cons=feed_data.get('cons', ''),
                    matching_size=feed_data.get('matchingSize', ''),
                    matching_photo=feed_data.get('matchingPhoto', ''),
                    matching_description=feed_data.get('matchingDescription', ''),
                    status_id=feed_data.get('statusId', 0),  # Числовое поле - 0 по умолчанию
                    excluded_from_rating=feed_data.get('excludedFromRating', {"isExcluded": False, "reasons": []}),
                    supplier_id=feed_data.get('wbUserId', None),  # Для ID None - стандартное значение

                    # Аналогично для остальных полей:
                    global_user_id=feed_data.get('globalUserId', ''),
                    nm_id=feed_data.get('nmId', 0),
                    product_valuation=feed_data.get('productValuation', 0),
                    text=feed_data.get('text', ''),
                    created_date=self._parse_datetime(feed_data.get('createdDate')),
                    updated_date=self._parse_datetime(feed_data.get('updatedDate')),
                    color=feed_data.get('color', ''),
                    size=feed_data.get('size', ''),
                    rank=feed_data.get('rank', 0.0),
                    bables=feed_data.get('bables', ''),

                    good_reasons=feed_data.get('reasons', {}).get('good', ''),
                    bad_reasons=feed_data.get('reasons', {}).get('bad', ''),
                    votes=feed_data.get('votes', {"pluses": 0, "minuses": 0}),
                    wb_user_details=feed_data.get('wbUserDetails', {}),
                    video=video,
                    feedback_helpfulness=feed_data.get('feedbackHelpfulness', ''),

                    # Поля ответа
                    answer_text=answer.get('text', '') if answer else '',
                    answer_create_date=self._parse_datetime(answer.get('createDate')) if answer else None,
                    answer_last_update=self._parse_datetime(answer.get('lastUpdate')) if answer else None,
                    answer_state=answer.get('state', '') if answer else '',
                    answer_editable=answer.get('editable', False) if answer else False,
                    answer_metadata=answer.get('metadata', None) if answer else None
                )

                session.add(feedback)
                session.commit()
                logger.info(f"Отзыв {feed_data['id']} успешно сохранен")
                return True

            except Exception as e:
                session.rollback()
                logger.error(f"Ошибка сохранения отзыва {feed_data.get('id')}: {str(e)}")
                return False

    def _parse_datetime(self, date_str):
        if not date_str or date_str == '0001-01-01T00:00:00Z':
            return None
        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))


