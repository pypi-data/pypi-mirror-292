from pathlib import Path

import json
import pytest

from testreqstatus.parse import requirements_status_from_test_results

DATA_DIRECTORY = Path(__file__).parent / "data"


@pytest.mark.parametrize(
    "test_requirements_filename,test_results_filename,requirements_status_filename",
    [
        (
            DATA_DIRECTORY / "input" / "romancal_test_requirements.json",
            DATA_DIRECTORY / "input" / "results-Linux-x64-py3.11.xml",
            DATA_DIRECTORY
            / "output"
            / "romancal_requirements_status-Linux-x64-py3.11.json",
        ),
        (
            DATA_DIRECTORY / "input" / "romancal_test_requirements.json",
            DATA_DIRECTORY / "input" / "results-macOS-x86-py3.11.xml",
            DATA_DIRECTORY
            / "output"
            / "romancal_requirements_status-macOS-x86-py3.11.json",
        ),
        (
            DATA_DIRECTORY / "input" / "romancal_test_requirements.json",
            DATA_DIRECTORY / "input" / "results-macOS-ARM64-py3.11.xml",
            DATA_DIRECTORY
            / "output"
            / "romancal_requirements_status-macOS-ARM64-py3.11.json",
        ),
    ],
)
def test_parse(
    test_requirements_filename,
    test_results_filename,
    requirements_status_filename,
    capfd,
):
    requirements_status_from_test_results(
        test_requirements_filename, test_results_filename
    )
    test_status, _ = capfd.readouterr()

    with open(requirements_status_filename) as reference_file:
        reference_status = json.load(reference_file)

    assert json.loads(test_status) == reference_status
