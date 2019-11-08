import sys
import os
import urllib.request
import json
import xml.etree.ElementTree as ET
from datetime import datetime

# read environment variables
env_commit_sha = os.environ['CI_COMMIT_SHA']
env_project_id = os.environ['CI_PROJECT_ID']

# read pipeline status
project_url = "https://gitlab.com/api/v4/projects/" + env_project_id
project_pipelines_url = project_url + "/pipelines"

# Load data about last builds (pipelines) using GitLab API
try:
    pipeline_data = urllib.request.urlopen(project_pipelines_url).read()
    project_pipelines = json.loads(pipeline_data)
    for pipeline in project_pipelines:
        if pipeline["ref"] == "master":
            latest_pipeline_id = str(pipeline["id"])
            latest_build_date = pipeline["updated_at"]
            latest_build_timestamp = datetime.timestamp(datetime.strptime(latest_build_date, '%Y-%m-%dT%H:%M:%S.%fZ'))
            latest_build_status = pipeline["status"]
            break
    for pipeline in project_pipelines:
        if pipeline["ref"] == "master" and pipeline["status"] == "success":
            green_pipeline_id = str(pipeline["id"])
            green_build_date = pipeline["updated_at"]
            green_build_timestamp = datetime.timestamp(datetime.strptime(green_build_date, '%Y-%m-%dT%H:%M:%S.%fZ'))
            break
except Exception as e:
    print("ERROR failed parsing pipeline data:", e)

# parse coverage report
try:
    cov_tree = ET.parse('build/reports/code-coverage.xml')
except FileNotFoundError:
    print("ERROR: code-coverage.xml file not found")
    sys.exit(1)

cov_root = cov_tree.getroot()
cov_rate = cov_root.get("line-rate")

# parse unit tests
try:
    tests_tree = ET.parse('build/reports/unit-tests.xml')
except FileNotFoundError:
    print("ERROR: unit-tests.xml file not found")
    sys.exit(1)

tests_root = tests_tree.getroot()
tests_testsuite = tests_root.find("testsuite")
tests_errors = tests_testsuite.get("errors")
tests_failures = tests_testsuite.get("failures")
tests_total = tests_testsuite.get("tests")

# parse linting report
try:
    lint_tree = ET.parse('build/reports/linting.xml')
except FileNotFoundError:
    print("ERROR: linting.xml file not found")
    sys.exit(1)

lint_root = lint_tree.getroot()
lint_testsuite = lint_root.find("testsuite")
lint_errors = lint_testsuite.get("errors")
lint_failures = lint_testsuite.get("failures")
lint_total = lint_testsuite.get("tests")

# create data object with all the collected info
ci_metrics_data = {
    "commit-sha": env_commit_sha,
    "build-status": {
        "last": {
            "status": latest_build_status,
            "timestamp": latest_build_timestamp
        },
        "green": {
            "timestamp": green_build_timestamp
        }
    },
    "coverage": {
        "percentage": 100*float(cov_rate)
        },
    "tests": {
        "errors": int(tests_errors),
        "failures": int(tests_failures),
        "total": int(tests_total)
    },
    "lint": {
        "errors": int(lint_errors),
        "failures": int(lint_failures),
        "total": int(lint_total)
    }
}

with open("build/reports/ci-metrics.json", "w") as write_file:
    json.dump(ci_metrics_data, write_file)