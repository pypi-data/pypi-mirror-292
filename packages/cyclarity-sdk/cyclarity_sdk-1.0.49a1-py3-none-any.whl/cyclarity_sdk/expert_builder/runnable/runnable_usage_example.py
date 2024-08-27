''' Usage example '''

from typing import Optional
from cyclarity_sdk.expert_builder import Runnable, BaseResultsModel


class CanTestResult(BaseResultsModel):
    res_str: str


class canRunnableInstance(Runnable, results_type=CanTestResult):
    desc: str
    cli_args: str
    _num: Optional[int] = 1  # not appear in the model_json_schema

    def setup(self):
        self.logger.info("setup")

    def run(self) -> CanTestResult:

        self.platform_api.send_test_report_description("This is dummy description for test")
        return CanTestResult(res_str="success!")

    def teardown(self, exception_type, exception_value, traceback):
        self.logger.info("teardown")


with canRunnableInstance(desc="test", cli_args="-as -fsd -dsd") as runnable_instance:  # noqa
    result: CanTestResult = runnable_instance()

# generates params schema from the runnable class attributes
print("\nParams schema - private members not included")
print(canRunnableInstance.model_json_schema())


# generate result schema
print("\nResult json schema:")
print(canRunnableInstance.generate_results_schema())


# generates result config (actual json instance of the result attributes)
print("\nResult config: ")
print(result.model_dump_json())
