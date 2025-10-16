from builder.base import XmlSaver
from builder.NS import root_ns, ns
from database.sql import donations_stmt, donations_tests_stmt
from database.utils import get_records


class Donations(XmlSaver):
    """
    Донации
    """
    def __init__(self):
        self.file_name = "donations.xml"
        self.xml_name = "Донации"
        self.app_tests = ""
        self.donations_records = None
        self.xml = None

    def load_data(self):
        records = get_records(donations_stmt)
        self.donations_records = records

    @staticmethod
    def _create_donation_attrib(record):
        donation_attrib = {
            "ResultStatus": record.ResultStatus,
            "DonationTypeId": record.DonationTypeId,
            "DepartmentId": record.DepartmentId,
            "DonorId": record.DonorId,
            "OrgId": record.OrgId,
            "CreateDate": record.CreateDate,
            "DonationDate": record.DonationDate,
            "UnId": record.UnId,
            "Barcode": record.Barcode,
            "IsDeleted": record.IsDeleted,
            "CreateUserId": record.CreateUserId
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
                CreateDate=record.CreateDate, UserId=record.UserId,
                DonationId=un_id, TestTypeId=record.TestTypeId,
                Value=record.Value
            )

    def _create_donation(self):
        for record in self.donations_records:
            self.type_test_dict = ""
            donation_attrib = self._create_donation_attrib(record)

            yield ns.Donation(
                ns.Volume(
                    record.Volume
                ),
                ns.ConsVol(
                    record.ConsVol
                ),
                ns.ConsBloodVol(
                    record.ConsBloodVol
                ),
                ns.LastModifiedDate(
                    record.LastModifiedDate
                ),
                ns.DataInputMethod(
                    record.DataInputMethod
                ),
                *self._create_results_component(record.UnId),
                ns.AppTests(
                    self.app_tests
                ) if self.app_tests else {},
                donation_attrib
            )

    def _build_xml(self):
        xml = root_ns.NodeToServerPackage(
            ns.NodeId('631000'),
            ns.RequestId('008c2fa8-63e9-469b-9d8c-7b27a4c8aaad'),
            ns.Depts(),
            ns.Sessions(),
            ns.Donations(
                *self._create_donation()
            )
        )
        return xml

    def build(self):
        self.xml = self._build_xml()
        self.save(self.file_name, self.xml)
