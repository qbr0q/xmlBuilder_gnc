import os
from abc import ABC, abstractmethod
from lxml import etree
from datetime import datetime
import logging


logger = logging.getLogger(__name__)


class XmlSaver:
    """
    Класс для сохранения файлов XML
    """
    base_dir_name = 'output'
    temp_dir_name = ''

    def save(self, file_name, xml):
        xml_path = self.get_path(file_name)
        with open(xml_path, 'wb') as f:
            f.write(etree.tostring(xml, pretty_print=True,
                                   encoding='utf-8', xml_declaration=True))

    def get_path(self, file_name):
        """
        Создаёт директорию для файла
        """
        XmlSaver.ensure_dir(self.base_dir_name)

        if not XmlSaver.temp_dir_name:
            current_date = datetime.now()
            dir_count = len(os.listdir(self.base_dir_name)) + 1

            temp_dir_name = f"{self.base_dir_name}/{current_date.strftime('%Y-%m-%d')}_{dir_count}"
            XmlSaver.ensure_dir(temp_dir_name)
            XmlSaver.temp_dir_name = temp_dir_name

        xml_path = f'{XmlSaver.temp_dir_name}/{file_name}'
        return xml_path

    @staticmethod
    def ensure_dir(dir_name):
        if dir_name and not os.path.exists(dir_name):
            os.makedirs(dir_name)


class XmlBase(ABC, XmlSaver):
    """
    Абстрактный базовый класс для генерации XML
    """
    def __init__(self, file_name: str, xml_name: str):
        self.file_name = file_name
        self.xml_name = xml_name

    @abstractmethod
    def load_data(self):
        pass

    @abstractmethod
    def _build_xml(self):
        pass

    def build(self):
        try:
            self.load_data()
            xml = self._build_xml()
            self.save(self.file_name, xml)
        except Exception as e:
            logger.error(f'Ошибка формирования или сохранения с документом "{self.xml_name}": {e}')
