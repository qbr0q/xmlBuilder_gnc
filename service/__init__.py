from service.logging_config import setup_log
from service.database import init_db
from service.builder import XmlBuilder


def run_service():
    setup_log()
    init_db()

    xml_builder = XmlBuilder()
    xml_builder.build()
