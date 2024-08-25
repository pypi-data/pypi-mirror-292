"""Assets module."""
from datetime import datetime, timedelta
from typing import Optional

from coverage import Coverage

from t_qa.config import Inputs
from t_qa.goole_api.google_drive_service import GoogleDriveService
from t_qa.models import TestCase
from t_qa.workitems import RUN_NUMBER


class RunAssets:
    """Assets class."""

    def __init__(self, google_drive_service: GoogleDriveService):
        """Initialize the Assets object."""
        self._google_drive_service = google_drive_service
        self._file = {}
        self._assets = {}
        self._run_data = {}

    def get_assets(self):
        """Get the assets from the Google Drive."""
        self._file = self._google_drive_service.create_file_if_not_exists(
            folder=self._google_drive_service.get_root_folder("T-QA Assets"),
            file_name=Inputs.ADMIN_CODE,
            mime_type="application/json",
        )
        self._assets = self._google_drive_service.get_file_content(file=self._file)
        self._delete_old_run_data()
        self._run_data = self._assets.get(RUN_NUMBER, {})
        return self._assets

    def upload_assets(self) -> None:
        """Upload the assets to the Google Drive."""
        self._google_drive_service.unlock_file(self._file)
        self._assets[RUN_NUMBER] = self._run_data
        self._google_drive_service.update_json_file(file=self._file, data=self._assets)

    def update_test_cases(self, test_cases: list[TestCase]) -> list[TestCase]:
        """Update the test cases."""
        if self._run_data.get("test_cases", False):
            for index, test_case in enumerate(test_cases):
                if test_case.status != "":
                    self._run_data["test_cases"][index]["status"] = test_case.status
        else:
            self._run_data["test_cases"] = [test_case.__dict__ for test_case in test_cases]

        return [TestCase(**test_case) for test_case in self._run_data["test_cases"]]

    def update_bug_counter(self, bug_counter: int) -> int:
        """Update the bug counter."""
        if self._run_data.get("bug_counter", False):
            self._run_data["bug_counter"] += bug_counter
        else:
            self._run_data["bug_counter"] = bug_counter
        return self._run_data["bug_counter"]

    def _delete_old_run_data(self) -> None:
        """Delete old assets."""
        for key, value in self._assets.items():
            if value.get("run_date", None):
                run_date = datetime.strptime(value["run_date"], "%Y-%m-%d %H:%M:%S")
                if run_date < datetime.now() - timedelta(days=3):
                    del self._assets[key]

    def update_record_status_counters(self, record_status_counters: dict[str, int]) -> dict[str, int]:
        """Update the record status counters."""
        if self._run_data.get("record_status_counters", False):
            for key, value in record_status_counters.items():
                if key in self._run_data["record_status_counters"]:
                    self._run_data["record_status_counters"][key] += value
                else:
                    self._run_data["record_status_counters"][key] = value
        else:
            self._run_data["record_status_counters"] = record_status_counters
        return self._run_data["record_status_counters"]

    def update_start_datetime(self, start_datetime: datetime) -> datetime:
        """Update the start datetime."""
        if self._run_data.get("start_datetime", False):
            asset_datetime = datetime.strptime(self._run_data["start_datetime"], "%Y-%m-%d %H:%M:%S")
            if start_datetime < asset_datetime:
                self._run_data["start_datetime"] = start_datetime.strftime("%Y-%m-%d %H:%M:%S")
        else:
            self._run_data["start_datetime"] = start_datetime.strftime("%Y-%m-%d %H:%M:%S")
        return datetime.strptime(self._run_data["start_datetime"], "%Y-%m-%d %H:%M:%S")

    def update_code_coverage_percentage(self, coverage: Coverage) -> str:
        """Update the code coverage."""
        if self._run_data.get("code_coverage", None):
            total_lines = self._run_data["code_coverage"].get("total_lines", 0)
            covered_lines = self._run_data["code_coverage"].get("covered_lines", 0)
        else:
            self._run_data["code_coverage"] = {}
            total_lines = 0
            covered_lines = 0

        for file in coverage.get_data().measured_files():
            analysis = coverage._analyze(file)
            total_lines += len(analysis.statements)
            covered_lines += len(analysis.executed)

        self._run_data["code_coverage"]["total_lines"] = total_lines
        self._run_data["code_coverage"]["covered_lines"] = covered_lines
        percentage = (covered_lines / total_lines) * 100 if total_lines > 0 else 0
        return f"{percentage :.0f}%"

    def get_row_number(self) -> Optional[int]:
        """Get the row number."""
        if self._run_data.get("row_number", False):
            return self._run_data["row_number"]
        else:
            return None

    def set_row_number(self, row_number) -> None:
        """Set the row number."""
        self._run_data["row_number"] = row_number
