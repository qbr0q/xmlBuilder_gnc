import asyncio

from service.database import init_db
from service.builder import XmlManager


def run_service():
    init_db()

    xml_manager = XmlManager()
    asyncio.run(xml_manager.execute())
