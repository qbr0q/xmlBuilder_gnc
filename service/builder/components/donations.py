from service.builder.base import XmlBase
from service.builder.base.NS import ns
from service.database.sql import donations_stmt, donations_tests_stmt
from service.database.utils import get_records


class Donations(XmlBase):
    """
    Донации
    """
    def __init__(self):
        self.app_tests = ""
        self.donations_records = None
        super().__init__(xml_name="Донации")

    def load_data(self):
        records = get_records(donations_stmt)
        self.donations_records = records

    @staticmethod
    def _create_donation_attrib(record):
        donation_attrib = {
            "UnId": record.UnId,
            "DonorId": record.UnId,
            "OrgId": record.OrgId,
            "CreateUserId": record.CreateUserId,
            "CreateDate": record.CreateDate,
            "DonationDate": record.DonationDate,
            "IsDeleted": record.IsDeleted,
            "Barcode": record.Barcode,
            "DepartmentId": record.DepartmentId,
            "DonationTypeId": record.DonationTypeId,
            "ResultStatus": record.ResultStatus
        }
        return donation_attrib

    def _get_test_type_info(self, records):
        type_info = (f'{record.TestTypeId}:{(record.Value != "-") + 1}' for record in records)
        self.app_tests = "|".join(type_info)

    def _create_results_component(self, un_id):
        prelab_tests = get_records(donations_tests_stmt % un_id)
        self._get_test_type_info(prelab_tests)

        for record in prelab_tests:
            yield ns.Result(
                DonationId=un_id, UserId=record.UserId,
                CreateDate=record.CreateDate, TestTypeId=record.TestTypeId,
                Value=record.Value
            )

    def _create_donation(self):
        for record in self.donations_records:
            donation_attrib = self._create_donation_attrib(record)

            yield ns.Donation(
                ns.Volume(
                    record.Volume
                ),
                ns.DataInputMethod(
                    record.DataInputMethod
                ),
                ns.LastModifiedDate(
                    record.LastModifiedDate
                ),
                ns.ConsVol(
                    record.ConsVol
                ),
                ns.ConsBloodVol(
                    record.ConsBloodVol
                ),
                ns.AppTests(
                    self.app_tests
                ) if self.app_tests else {},
                *self._create_results_component(record.DonationId),
                donation_attrib
            )

    def _build_xml(self):
        xml = ns.Donations(
            *self._create_donation()
        )
        return xml
