from service.builder.base import XmlBase
from service.builder.base.NS import ns
from service.database.sql import exemption_stmt
from service.database.utils import get_records


class Exemption(XmlBase):
    """
    Отводы
    """
    def __init__(self):
        self.exemption_records = None
        super().__init__(xml_name="Отводы")

    def load_data(self):
        records = get_records(exemption_stmt)
        self.exemption_records = records

    @staticmethod
    def _create_deferral_attrib(record):
        deferral_attrib = {
            "UnId": record.UnId,
            "DonorId": record.DonorId,
            "OrgId": record.OrgId,
            "DefType": record.DefType,
            "CreateDate": record.CreateDate,
            "CreateUserId": record.CreateUserId
        }
        return deferral_attrib

    def _create_deferral(self):
        for record in self.exemption_records:
            deferral_attrib = self._create_deferral_attrib(record)

            yield ns.Deferral(
                ns.StartDate(
                    record.StartDate
                ),
                ns.StopDate(
                    record.StopDate
                ),
                ns.RevokeDate(
                    record.RevokeDate
                ),
                ns.LastModifiedDate(
                    record.LastModifiedDate
                ),
                ns.LastModifiedUserId(
                    record.LastModifiedUserId
                ),
                ns.Comments(
                    record.Comments
                ),
                deferral_attrib
            )

    def _build_xml(self):
        xml = ns.Deferrals(
            *self._create_deferral()
        )
        return xml
