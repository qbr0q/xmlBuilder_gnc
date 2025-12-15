from service.builder.xmlBuilders import xml_builders


class XmlBuilder:
    @staticmethod
    def build():
        for XmlBuilder in xml_builders:
            xml_builder = XmlBuilder()
            xml_builder.build()
