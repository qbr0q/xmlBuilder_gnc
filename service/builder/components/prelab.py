from service.builder.base import XmlBase
from service.builder.base.NS import ns, xsi_type
from service.database.sql import prelab_stmt, prelab_tests_stmt
from service.database.utils import get_records


class PreLab(XmlBase):
    """
    Предлаб
    """
    def __init__(self):
        self.prelab_records = None
        super().__init__(xml_name="Предлаб")

    async def load_data(self):
        records = await get_records(prelab_stmt)
        self.prelab_records = records

    @staticmethod
    def _create_prelab_attrib(record):
        prelab_attrib = {
            "UnId": record.UnId,
            "DonorId": record.DonorId,
            "OrgId": record.OrgId,
            "UserId": record.UserId,
            "CreateDate": record.CreateDate,
            "ExamDate": record.ExamDate,
            "IsDeleted": record.IsDeleted,
            "HematologyResultType": record.HematologyResultType,
        }
        return prelab_attrib

    @staticmethod
    async def _create_results_component(un_id):
        prelab_tests = await get_records(prelab_tests_stmt % un_id)

        for record in prelab_tests:
            yield ns.Result(
                ns.IsNorm(record.IsNorm),
                ExamId=un_id, TestTypeId=record.TestTypeId,
                Value=record.Value
            )

    async def _create_hem_exams(self):
        for record in self.prelab_records:
            prelab_attrib = self._create_prelab_attrib(record)
            resulct_component = [rc async for rc in self._create_results_component(record.UnId)]

            yield ns.HemExam(
                ns.ExamEndTime(
                    record.ExamEndTime
                ),
                ns.DeferralId(
                    {xsi_type: "true"}
                ),
                *resulct_component,
                prelab_attrib
            )

    async def _build_xml(self):
        hem_exams = [h async for h in self._create_hem_exams()]

        xml = ns.HemExams(
            *hem_exams
        )
        return xml
