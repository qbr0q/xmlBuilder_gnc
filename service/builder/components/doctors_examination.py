from service.builder.base import XmlBase
from service.builder.base.NS import ns, xsi_type
from service.database.sql import docs_stmt, docs_tests_stmt
from service.database.utils import get_records


class DocsExam(XmlBase):
    """
    Врачебный осмотр
    """
    def __init__(self):
        self.visits_records = None
        super().__init__(xml_name="Врачебный осмотр")

    async def load_data(self):
        records = await get_records(docs_stmt)
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
    async def _create_results_component(un_id):
        docs_tests = await get_records(docs_tests_stmt % un_id)

        for record in docs_tests:
            yield ns.Result(
                ns.IsNorm(record.IsNorm) if record.IsNorm != '-' else {},
                ExamId=un_id, TestTypeId=record.TestTypeId,
                Value=record.Value
            )

    async def _create_med_exams(self):
        for record in self.visits_records:
            med_exam_attrib = self._create_med_exam_attrib(record)
            results_component = [rc async for rc in self._create_results_component(record.UnId)]

            yield ns.MedExam(
                ns.DeferralId(
                    {xsi_type: "true"}
                ),
                *results_component,
                med_exam_attrib
            )

    async def _build_xml(self):
        med_exams = [me async for me in self._create_med_exams()]

        xml = ns.MedExams(
            *med_exams
        )
        return xml
