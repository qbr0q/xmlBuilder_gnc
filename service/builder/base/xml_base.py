import os
import uuid
import asyncio
from abc import ABC, abstractmethod
from lxml import etree
from datetime import datetime
from types import SimpleNamespace as sn

from service.builder.base.NS import root_ns, ns
from service.database.connection import SessionLocal
from service.database.models import XmlExportLog
from settings import validation_path, DEVELOP_MODE, org_id


class XmlBase(ABC):
    """
    Абстрактный базовый класс для генерации XML
    """
    def __init__(self, xml_name: str):
        self.xml_name = xml_name

    async def load_data(self):
        pass

    @abstractmethod
    def _build_xml(self):
        pass

    async def build(self):
        try:
            await self.load_data()
            xml = await self._build_xml()
            return sn(
                status='ok',
                content=xml
            )

        except Exception as e:
            return sn(
                status='error',
                content=f'Ошибка формирования или сохранения с документом "{self.xml_name}": {e}'
            )


class XmlSaver:
    """
    Класс для сохранения файлов XML
    """
    base_dir_name = 'output'
    temp_dir_name = ''

    def save(self, xml):
        file_name = self.get_file_name()
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

    @staticmethod
    def get_file_name():
        now = datetime.now()
        timestamp = now.strftime("%Y%m%d%H%M%S")
        return f"{timestamp}.xml"


class XmlBuilder:
    """
    Класс для формирования документа xml
    """
    def __init__(self):
        self.log_messages = []
        self.request_id = self._get_request_id()

    async def build(self, components_list):
        tasks = []

        xml = root_ns.NodeToServerPackage(
            ns.NodeId(org_id),
            ns.RequestId(self.request_id)
        )
        for component in components_list:
            cmp_cls = component()
            tasks.append(cmp_cls.build())

        responses = await asyncio.gather(*tasks, return_exceptions=True)
        for response in responses:
            if isinstance(response, Exception):
                self.log_messages.append(f"Критическая ошибка: {str(response)}")
                continue

            if response.status == 'ok':
                xml_content = response.content
                if xml_content is not None and len(xml_content):
                    xml.append(xml_content)
            elif response.status == 'error':
                self.log_messages.append(response.content)

        return sn(
            content=xml,
            log_messages=self.log_messages,
            request_id=self.request_id
        )

    @staticmethod
    def _get_request_id():
        guid = uuid.uuid4()
        guid_str = str(guid)
        return guid_str


class XmlValidate:
    """
    Класс для валидации документа xml
    """
    def __init__(self):
        self.log_messages = []

    def validate(self, xml):
        if xml is None or not len(xml) or len(xml) == 2:
            return sn(
                log_messages=['Не сформировался ни один компонент'],
                is_valid=False
            )

        with open(validation_path, 'rb') as f:
            schema_root = etree.XML(f.read())
            schema = etree.XMLSchema(schema_root)

        is_valid = schema.validate(xml)
        if not is_valid:
            for error in schema.error_log:
                self.log_messages.append(
                    f'{error.path} - {error.message}'
                )
        self.log_messages.append(
            f'Validation: {is_valid}'
        )

        return sn(
            log_messages=self.log_messages,
            is_valid=is_valid
        )


class XmlLogger:
    """
    Класс для логирования информации
    """
    def __init__(self):
        pass

    @staticmethod
    def log_info(data_log):
        if DEVELOP_MODE:
            print('\n'.join(data_log.message))
        else:
            record = XmlExportLog(
                request_id=data_log.request_id,
                validation_status=data_log.validation_status,
                message='\n'.join(data_log.message)
            )
            with SessionLocal() as session:
                session.add(record)
                session.commit()
