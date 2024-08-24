from pathlib import Path
import re
import json

import typer


def extract_requirements_from_tests(directory: Path, output_filename: Path):
    """
    extract requirements (decorated as `@metrics_logger("DMS408")`) from tests in the given directory

    :param directory: test directory
    :param output_filename: filename to write test requirements to
    """

    test_requirements = {}
    for test_filename in directory.glob("**/test_*.py"):
        with open(test_filename) as test_file:
            test_file_contents = test_file.read()

        for match in re.finditer(
            '@metrics_logger\(("DMS.+")\)[\S\s]*?def ([^\(]+)\(.*\):',
            test_file_contents,
        ):
            test_module = f"{str(test_filename.parent.relative_to(directory)).replace('/', '.')}.{test_filename.stem}"
            if test_module not in test_requirements:
                test_requirements[test_module] = {}
            test_requirements[test_module][f"{match.group(2)}"] = [
                requirement.strip('" ') for requirement in match.group(1).split(",")
            ]

    with open(output_filename, "w") as output_file:
        json.dump(test_requirements, output_file, indent="  ")


def main():
    typer.run(extract_requirements_from_tests)
