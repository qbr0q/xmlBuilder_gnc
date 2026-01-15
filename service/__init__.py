from service.database import init_db
from service.builder import XmlManager


def run_service():
    init_db()

    xml_manager = XmlManager()
    xml_manager.execute()
