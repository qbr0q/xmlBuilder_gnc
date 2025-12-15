import sys
import sqlalchemy
import logging

from settings import (DB_USER, DB_PASSWORD, DB_HOST,
                      DB_PORT, DB_DATABASE)


logger = logging.getLogger(__name__)


DATABASE_URL = "postgresql://{user}:{password}@{host}:{port}/{database}".format(
    user=DB_USER, password=DB_PASSWORD, host=DB_HOST,
    port=DB_PORT, database=DB_DATABASE
)

engine = sqlalchemy.create_engine(
    DATABASE_URL,
    connect_args={"connect_timeout": 5}
)


def init_db():
    try:
        engine.connect()
    except sqlalchemy.exc.OperationalError as e:
        logger.error('Ошибка подлкючения к бд: не удалось соединиться')
        sys.exit(1)
    except Exception as e:
        logger.error(f'Неизвестная ошибка: {e}')
        sys.exit(1)
