from types import SimpleNamespace as sn

from service.builder.base import (XmlSaver, XmlBuilder,
                                  XmlValidate, XmlLogger)
from service.builder.components import components


class XmlManager:
    def __init__(self):
        self.builder = XmlBuilder()
        self.validator = XmlValidate()
        self.logger = XmlLogger()
        self.saver = XmlSaver()

    def execute(self):
        build_response = self.builder.build(
            components_list=components
        )
        xml_content = build_response.content

        validate_response = self.validator.validate(
            xml_content
        )

        log_data = sn(
            request_id=build_response.request_id,
            validation_status=validate_response.is_valid,
            message=build_response.log_messages + validate_response.log_messages
        )

        self.logger.log_info(log_data)

        self.saver.save(xml_content)
