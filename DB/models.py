from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, JSON, Index
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class WBFeedback(Base):
    __tablename__ = 'wb_feedbacks'

    # Единственное обязательное поле
    id = Column(String, primary_key=True, unique=True, nullable=False, comment="Уникальный ID отзыва")

    # Все остальные поля сделаны nullable=True с разумными default значениями
    global_user_id = Column(String, nullable=True, default=None, comment="Глобальный ID пользователя")
    nm_id = Column(Integer, nullable=True, default=None, comment="Артикул товара (nmId)")
    product_valuation = Column(Integer, nullable=True, default=None, comment="Оценка товара (1-5)")
    text = Column(String, nullable=True, default='', comment="Текст отзыва")
    created_date = Column(DateTime, nullable=True, default=None, comment="Дата создания отзыва")
    updated_date = Column(DateTime, nullable=True, default=None, comment="Дата последнего обновления")
    color = Column(String, nullable=True, default='', comment="Цвет товара")
    size = Column(String, nullable=True, default='', comment="Размер товара")
    rank = Column(Float, nullable=True, default=0.0, comment="Рейтинг отзыва")

    # JSON поля с пустыми значениями по умолчанию
    bables = Column(JSON, nullable=True, default={}, comment="Ключевые слова в отзыве")
    good_reasons = Column(JSON, nullable=True, default=[],
                         comment="Положительные причины оценки (список ID причин)")
    bad_reasons = Column(JSON, nullable=True, default=[],
                        comment="Отрицательные причины оценки (список ID причин)")
    votes = Column(JSON, nullable=True, default={"pluses": 0, "minuses": 0},
                   comment="Голоса ({'pluses': X, 'minuses': Y})")
    wb_user_details = Column(JSON, nullable=True, default={},
                             comment="Данные пользователя ({'name': '...', 'country': 'ru'})")

    # Дополнительные поля
    status_id = Column(Integer, nullable=True, default=0, comment="ID статуса отзыва")
    matching_description = Column(String, nullable=True, default='', comment="Соответствие описанию")
    matching_size = Column(String, nullable=True, default='', comment="Соответствие размеру")
    matching_photo = Column(String, nullable=True, default='', comment="Соответствие фото")
    video = Column(String, nullable=True, default=None, comment="Ссылка на видео (если есть)")
    feedback_helpfulness = Column(JSON, nullable=True, default=None, comment="Полезность отзыва")

    # Поля с мнениями
    pros = Column(String, nullable=True, default='', comment="Плюсы")
    cons = Column(String, nullable=True, default='', comment="Минусы")
    excluded_from_rating = Column(JSON, nullable=True,
                                  default={"isExcluded": False, "reasons": []},
                                  comment="Исключен из рейтинга?")
    supplier_id = Column(Integer, nullable=True, default=None, comment="ID поставщика")

    # Поля ответа компании
    answer_text = Column(String, nullable=True, default=None, comment="Текст ответа от магазина")
    answer_create_date = Column(DateTime, nullable=True, default=None, comment="Дата ответа")
    answer_last_update = Column(DateTime, nullable=True, default=None, comment="Дата обновления ответа")
    answer_state = Column(String, nullable=True, default=None, comment="Статус ответа (пример: 'wbRu')")
    answer_editable = Column(Boolean, nullable=True, default=False, comment="Можно ли редактировать ответ?")
    answer_metadata = Column(JSON, nullable=True, default=None, comment="Метаданные ответа")

    # Индексы для ускорения запросов
    __table_args__ = (
        Index('idx_nm_id', 'nm_id'),
        Index('idx_product_valuation', 'product_valuation'),
        Index('idx_created_date', 'created_date'),
    )
