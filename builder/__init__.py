from builder.xmlBuilders import xml_builders


class XmlBuilder:
    @staticmethod
    def build():
        for XmlBuilder in xml_builders:
            xml_builder = XmlBuilder()
            # xml_builder.load_data()
            xml_builder.build()
