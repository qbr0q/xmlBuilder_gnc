from service.builder.base import XmlBase
from service.builder.base.NS import ns
from service.database.sql import (donors_card_stmt, address_stmt,
                                  blood_param_stmt)
from service.database.utils import get_records, get_record


class DonorsCard(XmlBase):
    """
    Карта донора
    """
    def __init__(self):
        self.person_card_records = None
        self.address_records = None
        super().__init__(xml_name="Карта донора")

    def load_data(self):
        records = get_records(donors_card_stmt)
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
            "PhoneMob": record.PhoneMob,
            "JobInfo": record.JobInfo,
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
            address_record = get_record(address_stmt % record.UnId)
            blood_record = get_record(blood_param_stmt % record.UnId)

            yield ns.PersonCard(
                ns.Gender(
                    record.Gender
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
                ns.BloodGroup(
                    blood_record.BloodGroup
                ),
                ns.Rh(
                    blood_record.Rh
                ),
                ns.Kell(
                    blood_record.Kell
                ) if blood_record.Kell else {},
                ns.Phenotype(
                    blood_record.Phenotype
                ),
                ns.LastModifiedDate(
                    record.LastModifiedDate
                ),
                ns.LastModifiedUserId(
                    record.CreateUserId
                ),
                ns.IdentityDoc(
                    ns.IssueDate(record.IssueDate),
                    Number=record.Number, Serie=record.Serie,
                    DocType=record.DocType, IssuedBy=record.IssuedBy,
                ),
                person_card_attrib
            )

    def _build_xml(self):
        xml = ns.PersonCards(
            *self._create_person_cards()
        )
        return xml
