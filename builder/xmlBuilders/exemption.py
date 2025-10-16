from builder.base import XmlSaver
from builder.NS import root_ns, ns
from database.sql import exemption_stmt
from database.utils import get_records


class Exemption(XmlSaver):
    """
    Отводы
    """
    def __init__(self):
        self.file_name = "exemption.xml"
        self.xml_name = "Отводы"
        self.exemption_records = None
        self.xml = None

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

    def build(self):
        self.xml = self._build_xml()
        self.save(self.file_name, self.xml)
