from service.builder.base import XmlBase
from service.builder.base.NS import ns
from service.builder.base.utils import fetch_batch_data
from service.database.sql import donations_stmt, donations_tests_stmt
from service.database.utils import get_records


class Donations(XmlBase):
    """
    Донации
    """
    def __init__(self):
        self.app_tests = ""
        self.donations_records = None
        self.donation_tests = {}
        super().__init__(xml_name="Донации")

    async def load_data(self):
        records = await get_records(donations_stmt)
        self.donations_records = records

        self.donation_tests = await fetch_batch_data(records, donations_tests_stmt, 'DonationId', get_records)

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

    async def _create_results_component(self, un_id):
        donation_tests = self.donation_tests.get(un_id)
        self._get_test_type_info(donation_tests)

        for record in donation_tests:
            yield ns.Result(
                DonationId=un_id, UserId=record.UserId,
                CreateDate=record.CreateDate, TestTypeId=record.TestTypeId,
                Value=record.Value
            )

    async def _create_donation(self):
        for record in self.donations_records:
            donation_attrib = self._create_donation_attrib(record)
            results_component = [r async for r in self._create_results_component(record.DonationId)]

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
                *results_component,
                donation_attrib
            )

    async def _build_xml(self):
        donations_list = [d async for d in self._create_donation()]

        xml = ns.Donations(
            *donations_list
        )
        return xml
