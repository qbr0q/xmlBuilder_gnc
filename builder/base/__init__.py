from lxml import etree
from database.utils import get_records


class XmlSaver:
    """
    Класс для сохранения файлов xml
    """
    @staticmethod
    def save(xml_name, xml):
        with open(xml_name, 'wb') as f:
            f.write(etree.tostring(xml, pretty_print=True,
                                   encoding='utf-8', xml_declaration=True))
