from sqlalchemy import text

from database import engine


class NotEmptyRecord:
    """
    Класс, возвращающий дефолтное значение
    для пустых данных, иначе - строку
    """
    def __init__(self, record):
        self.record = record
        self.default_item = "-"

    def __getattr__(self, item):
        if self.record._mapping.get(item) is not None:
            return str(
                getattr(self.record, item)
            )
        return self.default_item


def get_records(stmt):
    with engine.connect() as conn:
        result_data = conn.execute(text(stmt))
        result_raw = result_data.fetchall()
        result = [NotEmptyRecord(res) for res in result_raw]
    return result


def get_record(stmt):
    with engine.connect() as conn:
        result_data = conn.execute(text(stmt))
        result_raw = result_data.fetchone()
        result = NotEmptyRecord(result_raw)
    return result
