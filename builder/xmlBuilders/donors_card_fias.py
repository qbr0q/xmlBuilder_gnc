from builder.base import XmlSaver
from builder.NS import root_ns, ns
from database.sql import (donors_card_fias_stmt, address_stmt,
                          blood_param_stmt, notes_stmt)
from database.utils import get_records, get_record


class DonorsCardFias(XmlSaver):
    """
    Карта донора ФИАС
    """
    def __init__(self):
        self.file_name = "donors_card_fias.xml"
        self.xml_name = "Карта донора ФИАС"
        self.person_card_records = None
        self.address_records = None
        self.xml = None

    def load_data(self):
        records = get_records(donors_card_fias_stmt)
        self.person_card_records = records

    @staticmethod
    def _create_person_card_attrib(record):
        parson_card_attrib = {
            "UnId": record.UnId,
            "OrgId": record.OrgId,
            "LastName": record.LastName,
            "FirstName": record.FirstName,
            "MiddleName": record.MiddleName,
            "BirthDate": record.BirthDate,
            "BirthDateIsUndef": record.BirthDateIsUndef,
            "PhoneMob": record.PhoneMob,
            "JobInfo": record.JobInfo,
            "Snils": record.Snils,
            "CreateDate": record.CreateDate,
            "CreateUserId": record.CreateUserId,
            "IsMessageAgree": record.IsMessageAgree,
            "IsDeleted": record.IsDeleted
        }
        return parson_card_attrib

    @staticmethod
    def _create_notes_component(record):
        notes_records = get_records(notes_stmt % record.UnId)
        for note_record in notes_records:
            yield ns.Notes(
                ns.Text(note_record.Text),
                DonorId=note_record.DonorId, NoteType=note_record.NoteType,
                CreateDate=note_record.CreateDate, UserId=note_record.UserId,
                IsFixed=note_record.IsFixed, AssignedTo=note_record.AssignedTo,
                IsDeleted=note_record.IsDeleted
            )

    def _create_person_cards(self):
        for record in self.person_card_records:
            person_card_attrib = self._create_person_card_attrib(record)
            # находим адрес и параметры крови для конрктеного пациента
            address_record = get_record(address_stmt % record.UnId)
            blood_record = get_record(blood_param_stmt % record.UnId)

            yield ns.PersonCard(
                ns.Gender(
                    record.Gender
                ),
                ns.RegAddressIsInactive(
                    address_record.RegAddressIsInactive
                ),
                ns.FactAddressIsInactive(
                    address_record.FactAddressIsInactive
                ),
                ns.TempAddressIsInactive(
                    address_record.TempAddressIsInactive
                ),
                ns.RegAddress(
                    ns.FiasRegionId(address_record.RegFiasRegionId),
                    ns.FiasRegion(address_record.RegRegion),
                    ns.FiasStreetId(address_record.RegFiasStreetId),
                    ns.FiasStreet(address_record.RegStreet),
                    Id=address_record.RegId, House=address_record.RegHouse,
                    Flat=address_record.RegFlat, PlaneAddress=address_record.RegPlaneAddress
                ),
                ns.FactAddress(
                    ns.FiasRegionId(address_record.FactFiasRegionId),
                    ns.FiasRegion(address_record.FactRegion),
                    ns.FiasStreetId(address_record.FactFiasStreetId),
                    ns.FiasStreet(address_record.FactStreet),
                    Id=address_record.FactId, House=address_record.FactHouse,
                    Flat=address_record.FactFlat, PlaneAddress=address_record.FactPlaneAddress
                ),
                ns.MedicalCertsInfo('хз'),
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
                ns.RbcAntibody(
                    blood_record.RbcAntibody
                ),
                ns.LastModifiedDate(
                    record.LastModifiedDate
                ),
                ns.LastModifiedUserId(
                    record.CreateUserId
                ),
                ns.IsActive(
                    record.IsActive
                ),
                ns.IsAgree(
                    record.IsAgree
                ),
                ns.IdentityDoc(
                    ns.IssueDate(record.IssueDate),
                    DocType=record.DocType, Serie=record.Serie,
                    Number=record.Number
                ),
                *self._create_notes_component(record)
                if record.note_id != '-' else {},
                person_card_attrib
            )

    def _build_xml(self):
        xml = root_ns.NodeToServerPackage(
            ns.NodeId('631000'),
            ns.RequestId('008c2fa8-63e9-469b-9d8c-7b27a4c8aaad'),
            ns.Users(),
            ns.Employees(),
            ns.Depts(),
            ns.Teams(),
            ns.Sessions(),
            ns.Positions(),
            ns.PersonCards(
                *self._create_person_cards()
            )
        )
        return xml

    def build(self):
        self.xml = self._build_xml()
        self.save(self.file_name, self.xml)
