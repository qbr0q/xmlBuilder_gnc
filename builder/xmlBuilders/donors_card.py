from builder.base import XmlSaver
from builder.NS import root_ns, ns
from database.sql import donors_card_stmt, blood_param_stmt
from database.utils import get_records, get_record


class DonorsCard(XmlSaver):
    """
    Карта донора
    """
    def __init__(self):
        self.file_name = "donors_card.xml"
        self.xml_name = "Карта донора"
        self.person_card_records = None
        self.xml = None

    def load_data(self):
        records = get_records(donors_card_stmt)
        self.person_card_records = records

    @staticmethod
    def _create_person_card_attrib(record):
        parson_card_attrib = {
            "PhoneMob": record.PhoneMob,
            "JobInfo": record.JobInfo,
            "JobPosition": record.JobPosition,
            "OrgId": record.OrgId,
            "CreateDate": record.CreateDate,
            "CreateUserId": record.CreateUserId,
            "UnId": record.UnId,
            "MiddleName": record.MiddleName,
            "FirstName": record.FirstName,
            "LastName": record.LastName,
            "BirthDate": record.BirthDate,
            "IsDeleted": record.IsDeleted,
            "IsMessageAgree": record.IsMessageAgree
        }
        return parson_card_attrib

    def _create_person_cards(self):
        for record in self.person_card_records:
            person_card_attrib = self._create_person_card_attrib(record)
            blood_record = get_record(blood_param_stmt % record.UnId)

            yield ns.PersonCard(
                ns.RegAddress(
                    PlaneAddress=record.PlaneAddress
                ),
                ns.IdentityDoc(
                    Number=record.Number, Serie=record.Serie, DocType=record.DocType
                ),
                ns.LastModifiedDate(
                    record.LastModifiedDate
                ),
                ns.BloodGroup(
                    blood_record.BloodGroup
                ),
                ns.Rh(
                    blood_record.Rh
                ),
                ns.Kell(
                    blood_record.Kell
                ),
                ns.Phenotype(
                    blood_record.Phenotype
                ),
                ns.Gender(
                    record.Gender
                ), person_card_attrib
            )

    def _build_xml(self):
        xml = root_ns.NodeToServerPackage(
            ns.NodeId('631000'),
            ns.RequestId('008c2fa8-63e9-469b-9d8c-7b27a4c8aaad'),
            ns.PersonCards(
                *self._create_person_cards()
            )
        )
        return xml

    def build(self):
        self.xml = self._build_xml()
        self.save(self.file_name, self.xml)
