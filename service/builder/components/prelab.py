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

    def load_data(self):
        records = get_records(prelab_stmt)
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
    def _create_results_component(un_id):
        prelab_tests = get_records(prelab_tests_stmt % un_id)

        for record in prelab_tests:
            yield ns.Result(
                ns.IsNorm(record.IsNorm),
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
        xml = ns.HemExams(
            *self._create_hem_exams()
        )
        return xml
