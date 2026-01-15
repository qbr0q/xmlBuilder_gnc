from sqlalchemy import (Column, Integer, String,
                        DateTime, Text, Boolean)
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class XmlExportLog(Base):
    __tablename__ = 'xml_export_logs'

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.now)
    request_id = Column(String(50))
    validation_status = Column(Boolean)
    message = Column(Text)
