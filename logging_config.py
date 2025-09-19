import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logging():
    os.makedirs('logs', exist_ok=True)
    # Настройки логирования
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            RotatingFileHandler(
                'logs/wb_feedback_tracker.log',
                maxBytes=5 * 1024 * 1024,  # 5 MB
                backupCount=3
            ),
            logging.StreamHandler()
        ]
    )
    logging.getLogger('sqlalchemy').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
