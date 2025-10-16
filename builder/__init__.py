from builder.xmlBuilders.donors_card import DonorsCard
from builder.xmlBuilders.donors_card_fias import DonorsCardFias
from builder.xmlBuilders.doctors_examination import DocsExam
from builder.xmlBuilders.prelab import PreLab
from builder.xmlBuilders.donations import Donations
from builder.xmlBuilders.exemption import Exemption


class XmlBuilder:
    @staticmethod
    def build():
        xml_classes = (DonorsCard, DonorsCardFias, DocsExam, PreLab, Donations, Exemption)
        for XmlClass in xml_classes:
            xml_class = XmlClass()
            xml_class.load_data()
            xml_class.build()
