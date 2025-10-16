from builder.base import XmlSaver
from builder.NS import root_ns, ns, xsi_type
from database.sql import docs_stmt, docs_tests_stmt
from database.utils import get_records


class DocsExam(XmlSaver):
    """
    Врачебный осмотр
    """
    def __init__(self):
        self.file_name = "doctors_examination.xml"
        self.xml_name = "Врачебный осмотр"
        self.visits_records = None
        self.xml = None

    def load_data(self):
        records = get_records(docs_stmt)
        self.visits_records = records

    @staticmethod
    def _create_med_exam_attrib(record):
        med_exam_attrib = {
            "UserId": record.UserId,
            "CreateDate": record.CreateDate,
            "OrgId": record.OrgId,
            "DonorId": record.DonorId,
            "UnId": record.UnId,
            "ExamDate": record.ExamDate,
            "IsDeleted": record.IsDeleted
        }
        return med_exam_attrib

    @staticmethod
    def _create_results_component(un_id):
        docs_tests = get_records(docs_tests_stmt % un_id)
        for record in docs_tests:
            yield ns.Result(
                ns.IsNorm(record.IsNorm) if record.IsNorm != '-' else {},
                ExamId=un_id, TestTypeId=record.TestTypeId,
                Value=record.Value
            )

    def _create_med_exams(self):
        for record in self.visits_records:
            med_exam_attrib = self._create_med_exam_attrib(record)

            yield ns.MedExam(
                ns.DeferralId(
                    {xsi_type: "true"}
                ),
                *self._create_results_component(record.UnId),
                med_exam_attrib
            )

    def _build_xml(self):
        xml = root_ns.NodeToServerPackage(
            ns.NodeId('631000'),
            ns.RequestId('008c2fa8-63e9-469b-9d8c-7b27a4c8aaad'),
            ns.MedExams(
                *self._create_med_exams()
            )
        )
        return xml

    def build(self):
        self.xml = self._build_xml()
        self.save(self.file_name, self.xml)
