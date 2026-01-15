from sqlalchemy import text
import datetime

from service.database.connection import engine


class FormattedRecord:
    _default_value = {
        bool: 'false',
        int: '0',
        datetime.datetime: '1900-01-01T00:00:00',
        datetime.date: '1900-01-01T00:00:00',
        str: '-'
    }

    def __init__(self, record, field_descriptions):
        self.record = record
        self.field_descriptions = self._get_dict_description(
            field_descriptions
        )

    def __getattr__(self, item):
        record_value = getattr(self.record, item, None)
        item_type = self.field_descriptions.get(item)
        if record_value is not None:
            return self._get_formatted_value(record_value, item_type)
        return self._default_value.get(item_type, 'null')

    @staticmethod
    def _get_formatted_value(record_value, item_type):
        if item_type == bool:
            return str(record_value).lower()
        elif item_type in (datetime.datetime, datetime.date):
            return record_value.strftime('%Y-%m-%dT%H:%M:%S')
        elif item_type == float:
            return str(int(record_value))
        return str(record_value)

    @staticmethod
    def _get_dict_description(field_descriptions):
        return {i[0]: PG_TYPES_MAP.get(i[1]) for i in field_descriptions}


async def get_records(stmt):
    async with engine.connect() as conn:
        result_data = await conn.execute(text(stmt))
        field_descriptions = result_data.cursor.description
        result_raw = result_data.fetchall()
        result = [FormattedRecord(res, field_descriptions) for res in result_raw]
    return result


async def get_record(stmt):
    async with engine.connect() as conn:
        result_data = await conn.execute(text(stmt))
        field_descriptions = result_data.cursor.description
        result_raw = result_data.fetchone()
        result = FormattedRecord(result_raw, field_descriptions)
    return result


# OID полей в постгресе -> тип данных в питоне
PG_TYPES_MAP = {
    # Числа (Integers / Floats)
    16: bool,  # bool
    20: int,  # int8 (bigint)
    21: int,  # int2 (smallint)
    23: int,  # int4 (integer)
    700: float,  # float4 (real)
    701: float,  # float8 (double precision)

    # Строки
    18: str,  # char
    25: str,  # text
    1042: str,  # bpchar (char fixed length)
    1043: str,  # varchar

    # Даты и время
    1082: datetime.date,  # date
    1114: datetime.datetime,  # timestamp (without timezone)
    1184: datetime.datetime,  # timestamptz (with timezone)
    1083: datetime.time,  # time
    1266: datetime.time,  # timetz
}
