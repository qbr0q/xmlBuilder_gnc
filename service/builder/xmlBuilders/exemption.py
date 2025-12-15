from service.builder.base import XmlBase
from service.builder.NS import root_ns, ns
from service.database.sql import exemption_stmt
from service.database.utils import get_records


class Exemption(XmlBase):
    """
    Отводы
    """
    def __init__(self):
        self.exemption_records = None
        super().__init__(file_name="exemption.xml", xml_name="Отводы")

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
                ns.RevokeReason(),
                ns.RevokedUserId(
                    record.RevokedUserId
                ),
                ns.RevokedOrgId(
                    record.RevokedOrgId
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
        xml = root_ns.NodeToServerPackage(
            ns.NodeId('631000'),
            ns.RequestId('008c2fa8-63e9-469b-9d8c-7b27a4c8aaad'),
            ns.Deferrals(
                *self._create_deferral()
            )
        )
        return xml
