from pathlib import Path
import re
import json

import typer
from typing_extensions import Annotated


def extract_requirements_from_tests(
    directory: Annotated[Path, typer.Argument(help="test directory")],
):
    """
    extract requirements (decorated as `@metrics_logger("DMS408")`) from tests in the given directory
    """

    test_requirements: dict[str, dict[str, list[str]]] = {}
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

    print(json.dumps(test_requirements, indent="  "))


def main():
    typer.run(extract_requirements_from_tests)
