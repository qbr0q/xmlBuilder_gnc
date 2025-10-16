from builder.base import XmlSaver
from builder.NS import root_ns, ns, xsi_type
from database.sql import prelab_stmt, prelab_tests_stmt
from database.utils import get_records


class PreLab(XmlSaver):
    """
    Предлаб
    """
    def __init__(self):
        self.file_name = "prelab.xml"
        self.xml_name = "Предлаб"
        self.prelab_records = None
        self.xml = None

    def load_data(self):
        records = get_records(prelab_stmt)
        self.prelab_records = records

    @staticmethod
    def _create_prelab_attrib(record):
        prelab_attrib = {
            "HematologyResultType": record.HematologyResultType,
            "OrgId": record.OrgId,
            "DonorId": record.DonorId,
            "IsDeleted": record.IsDeleted,
            "CreateDate": record.CreateDate,
            "ExamDate": record.ExamDate,
            "UnId": record.UnId,
            "UserId": record.UserId
        }
        return prelab_attrib

    @staticmethod
    def _create_results_component(un_id):
        prelab_tests = get_records(prelab_tests_stmt % un_id)

        for record in prelab_tests:
            yield ns.Result(
                ExamId=un_id, TestTypeId=record.TestTypeId,
                Value=record.Value
            )

    def _create_hem_exams(self):
        for record in self.prelab_records:
            prelab_attrib = self._create_prelab_attrib(record)

            yield ns.HemExam(
                ns.ExamEndTime(
                    record.ExamEndTime
                ),
                ns.DeferralId(
                    {xsi_type: "true"}
                ),
                *self._create_results_component(record.UnId),
                prelab_attrib
            )

    def _build_xml(self):
        xml = root_ns.NodeToServerPackage(
            ns.NodeId('631000'),
            ns.RequestId('008c2fa8-63e9-469b-9d8c-7b27a4c8aaad'),
            ns.Users(),
            ns.HemExams(
                *self._create_hem_exams()
            )
        )
        return xml

    def build(self):
        self.xml = self._build_xml()
        self.save(self.file_name, self.xml)
