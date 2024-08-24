from pathlib import Path
import json

import typer


from junitparser import JUnitXml


def requirements_status_from_test_results(
    test_requirements_filename: Path, test_results_filename: Path
):
    """
    parse test results and output status of requirements

    :param test_requirements: JSON file linking tests to requirements (one-to-many)
    :param test_results: JUnit XML file of test results
    """

    with open(test_requirements_filename) as test_requirements_file:
        test_requirements = json.load(test_requirements_file)

    requirements_status: dict[str, dict[str, dict[str, str]]] = {}
    results = JUnitXml.fromfile(test_results_filename)
    for suite in results:
        for case in suite:
            if case.classname in test_requirements:
                if case.name in test_requirements[case.classname]:
                    for requirement in test_requirements[case.classname][case.name]:
                        if requirement not in requirements_status:
                            requirements_status[requirement] = {}
                        if case.classname not in requirements_status[requirement]:
                            requirements_status[requirement][case.classname] = {}
                        requirements_status[requirement][case.classname][case.name] = (
                            "PASS"
                            if case.is_passed
                            else "SKIPPED"
                            if case.is_skipped
                            else "FAIL"
                        )

    print(json.dumps(requirements_status, indent="  "))


def print_requirements_status_from_test_results(
    test_requirements_filename: Path, test_results_filename: Path
):
    """
    parse test results and output status of requirements

    :param test_requirements: JSON file linking tests to requirements (one-to-many)
    :param test_results: JUnit XML file of test results
    """
    print(
        json.dumps(
            requirements_status_from_test_results(
                test_requirements_filename, test_results_filename
            ),
            indent="  ",
        )
    )


def main():
    typer.run(requirements_status_from_test_results)
