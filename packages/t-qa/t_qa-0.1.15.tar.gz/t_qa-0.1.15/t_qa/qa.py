"""QA.py module contains the QA class for the Digital Worker's process."""
import atexit
import os
import re
import traceback
from datetime import datetime
from typing import Optional

import pytz
import t_bug_catcher
import yaml
from coverage import Coverage
from ta_bitwarden_cli.exceptions import NotLoggedInError
from ta_bitwarden_cli.handler import get_attachment
from thoughtful.supervisor import report_builder

from .config import DEFAULT_QA_RESULT_FILE_PATH, DEFAULT_TEST_CASES_FILE_PATH, LOCAL_RUN, SCOPES
from .excel_processing.google_sheet import GoogleSheet
from .excel_processing.report import _Report
from .exception import (
    NotLoggedInToGoogleException,
    ServiceAccountKeyPathException,
    SkipIfItLocalRunException,
    SkipIfItWorkItemsNotSetException,
    TestCaseFileDoesNotExistException,
    TestCaseReadException,
    TQaBaseException,
    TQaBaseSilentException,
)
from .goole_api.account import Account
from .goole_api.google_drive_service import GoogleDriveService
from .logger import logger
from .models import RunData, TestCase
from .run_assets import RunAssets
from .status import Status
from .utils import SingletonMeta, install_sys_hook
from .workitems import METADATA, RUN_NUMBER, VARIABLES


class QA(metaclass=SingletonMeta):
    """QA class for the Digital Worker's process."""

    def __init__(self) -> None:
        """Initialize the QA process."""
        if not LOCAL_RUN:
            if Coverage.current():
                self.coverage = Coverage.current()
            elif Coverage().config.config_file:
                self.coverage = Coverage()
            else:
                self.coverage = Coverage(branch=True)
                self.coverage.exclude(r"    def __repr__")
                self.coverage.exclude(r"raise AssertionError")
                self.coverage.exclude(r"raise NotImplementedError")
                self.coverage.exclude(r"if 0:")
                self.coverage.exclude(r"if __name__ == .__main__.:")
                self.coverage.exclude(r"if TYPE_CHECKING:")
                self.coverage.exclude(r"class .*\bProtocol\):")
                self.coverage.exclude(r"@(abc\.)?abstractmethod")
            self.coverage.start()
        self.run_status: str = Status.SUCCESS.value
        self.service_account_key_path: Optional[str] = None
        self.test_cases: list[TestCase] = []
        self.record_status_counters = {}

    def configurate(
        self,
        test_cases_file_path: str = DEFAULT_TEST_CASES_FILE_PATH,
        service_account_key_path: str = None,
    ) -> None:
        """Configurate the QA process."""
        try:
            self._set_test_cases(test_cases_file_path)
            self._set_service_account_key_path(service_account_key_path)
            self._skip_if_it_local_run()
        except TQaBaseSilentException:
            return
        except TQaBaseException as e:
            logger.warning(e)
            return
        self._set_start_datetime()
        atexit.register(self.dump)

    def test_case_pass(self, id: str) -> None:
        """Check the test case passed."""
        self._set_test_case_status(id=id, status=Status.PASS.value)

    def test_case_fail(self, id: str) -> None:
        """Check the test case failed."""
        self._set_test_case_status(id=id, status=Status.FAIL.value)

    def dump(self):
        """Dump the test cases."""
        try:
            self._get_code_coverage()
            account = Account(
                service_account_key_path=self.service_account_key_path,
                scopes=SCOPES,
            )
            google_drive_service = GoogleDriveService(account)
            run_assets = RunAssets(google_drive_service)
            run_assets.get_assets()

            self.test_cases = run_assets.update_test_cases(self.test_cases)
            self.start_datetime = run_assets.update_start_datetime(self.start_datetime)
            self.record_status_counters = run_assets.update_record_status_counters(self.record_status_counters)

            bugs = run_assets.update_bug_counter(t_bug_catcher.get_errors_count())
            code_coverage = run_assets.update_code_coverage_percentage(self.coverage)

            run_data = RunData(
                run_date=self.start_datetime,
                duration=self.__get_duration(),
                empower_env="Prod" if VARIABLES.get("environment", "") == "production" else "Dev",
                run_link=f'=HYPERLINK("{METADATA.get("processRunUrl", "")}", "{RUN_NUMBER}")',
                status=self._get_run_result(),
                test_cases=self.test_cases,
                bugs=str(bugs),
                code_coverage=code_coverage,
                record_status_counters=self.record_status_counters,
            )
            report = _Report(
                local_excel_file_path=DEFAULT_QA_RESULT_FILE_PATH,
                google_sheet=GoogleSheet(account),
                google_drive=google_drive_service,
            )
            row_number = report.dump(
                run_data=run_data,
                row_number=run_assets.get_row_number(),
            )
            run_assets.set_row_number(row_number)
            run_assets.upload_assets()
        except TQaBaseException as e:
            logger.warning(e)
        except Exception as e:
            logger.error(f"Error during dumping: {e}")
            traceback.print_exc()

    def set_test_records_status_count(self, record_status_counters: dict[str, int]):
        """Set the test records status count."""
        if len(record_status_counters.keys()) >= 15:
            logger.error("The record status count is too large. It should be less than 15 statuses.")
            record_status_counters = {}
        self.record_status_counters = record_status_counters

    def _get_run_result(self):
        if self.run_status == Status.SUCCESS.value:
            try:
                self.run_status = report_builder.status.value
            except AttributeError:
                logger.warning("Could not get the run result from supervisor.")
        return self.run_status

    def __get_duration(self):
        duration = datetime.now(pytz.UTC) - self.start_datetime.astimezone(pytz.UTC)
        seconds = duration.seconds
        minutes = seconds // 60
        hours = minutes // 60
        duration_str = f"{hours}h {minutes % 60}m {seconds % 60}s"
        return duration_str

    def _set_test_cases(self, test_cases_file_path: str) -> None:
        if not os.path.exists(test_cases_file_path):
            raise TestCaseFileDoesNotExistException(f"Test cases file not found: {test_cases_file_path}")
        try:
            with open(test_cases_file_path) as test_cases_file:
                test_cases = yaml.safe_load(test_cases_file)["test_cases"]
                self.test_cases = [TestCase(**test_case) for test_case in test_cases]
        except (TypeError, KeyError, ValueError) as e:
            raise TestCaseReadException(f"Error during reading test cases: {e}")

    def _set_service_account_key_path(self, service_account_key_path: Optional[str]) -> None:
        if service_account_key_path:
            self.service_account_key_path = service_account_key_path
        else:
            try:
                self.service_account_key_path = get_attachment(
                    "T-QA Google",
                    "service_account_key.json",
                )
            except NotLoggedInError:
                raise NotLoggedInToGoogleException()
            except ValueError:
                raise ServiceAccountKeyPathException("There are no access to 'T-QA Google' collection")

    def _skip_if_it_local_run(self):
        if LOCAL_RUN:
            raise SkipIfItLocalRunException()
        if not METADATA:
            raise SkipIfItWorkItemsNotSetException("'Metadata' is not set")
        if not VARIABLES:
            raise SkipIfItWorkItemsNotSetException("'Variables' is not set")

    def _set_start_datetime(self) -> None:
        """Get the start datetime."""
        try:
            root_path = os.environ.get("ROBOT_ROOT", "")
            console_log_folder_path = os.path.abspath(os.path.join(root_path, os.pardir))
            console_log_file_path = os.path.join(console_log_folder_path, "console.txt")
            with open(console_log_file_path, "r") as file:
                data = file.read()
            date_str = re.findall(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", data)[0]
            date_str += "UTC"
            self.start_datetime = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S%Z")
        except (TypeError, FileNotFoundError, IndexError) as e:
            logger.warning("Could not get the start datetime from the empower.")
            self.start_datetime = datetime.now()
            t_bug_catcher.report_error(exception=e)

    def _set_test_case_status(self, id: str, status: str):
        """Check the test case."""
        for test_case in self.test_cases:
            if test_case.id == id:
                test_case.status = status

    def _get_code_coverage(self):
        self.coverage.stop()
        self.coverage.save()
        self.coverage.report(
            ignore_errors=True,
            omit=["*/t_qa/*"],
        )


t_qa = QA()
install_sys_hook(t_qa)

configure_qa = t_qa.configurate
test_case_failed = t_qa.test_case_fail
test_case_passed = t_qa.test_case_pass
set_test_records_status_count = t_qa.set_test_records_status_count
