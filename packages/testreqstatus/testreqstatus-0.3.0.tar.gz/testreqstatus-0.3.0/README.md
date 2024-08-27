# testreqstatus

[![PyPI - Version](https://img.shields.io/pypi/v/testreqstatus.svg)](https://pypi.org/project/testreqstatus)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/testreqstatus.svg)](https://pypi.org/project/testreqstatus)

-----

```console
pip install testreqstatus
```

## Usage

1. Establish a set of requirements:

    ```json
    {
      "romancal.regtest.test_mos_pipeline": {
        "test_level3_mos_pipeline": [
          "DMS356",
          "DMS374",
          "DMS400"
        ],
        "test_hlp_mosaic_pipeline": [
          "DMS373"
        ]
      }
    }
    ```

> [!TIP]
> To extract test requirements from existing tests 
> decorated with `@metrics_logger`, use `extract_requirements_from_tests` 

2. Run tests and generate a `results.xml` file:

    ```xml
    <?xml version="1.0" encoding="utf-8"?>
    <testsuites>
      <testsuite name="pytest" errors="0" failures="0" skipped="0" tests="2" time="2021.550" timestamp="2024-08-23T00:23:01.454354" hostname="spacetelescope-runner-2ls89-rrbf2">
        <testcase classname="romancal.regtest.test_mos_pipeline" name="test_level3_mos_pipeline" time="677.728">
        </testcase>
        <testcase classname="romancal.regtest.test_mos_pipeline" name="test_hlp_mosaic_pipeline" time="486.642">
        </testcase>
      </testsuite>
    </testsuites>
    ```

3. Run `requirements_status_from_test_results` to retrieve requirements status from test results:

    ```shell
    requirements_status_from_test_results examples/test_requirements.json examples/results.xml
    ```

    ```json
    {
      "DMS356": {
        "romancal.regtest.test_mos_pipeline": {
          "test_level3_mos_pipeline": "PASS"
        }
      },
      "DMS374": {
        "romancal.regtest.test_mos_pipeline": {
          "test_level3_mos_pipeline": "PASS"
        }
      },
      "DMS400": {
        "romancal.regtest.test_mos_pipeline": {
          "test_level3_mos_pipeline": "PASS"
        }
      },
      "DMS373": {
        "romancal.regtest.test_mos_pipeline": {
          "test_hlp_mosaic_pipeline": "PASS"
        }
      }
    }
    ```

> [!TIP]
> Use `--help` to print usage information for any command.

