"""Prepare Allure metadata files for Jenkins reports."""
import argparse
import json
import os
from datetime import datetime
from pathlib import Path
import xml.etree.ElementTree as ET


def load_summary(report_path: Path) -> dict:
    if not report_path.exists():
        return {"total": 0, "passed": 0, "failed": 0, "skipped": 0, "duration": 0.0}
    with report_path.open(encoding="utf-8") as f:
        data = json.load(f)
    summary = data.get("summary", {})
    return {
        "total": int(summary.get("total", 0) or 0),
        "passed": int(summary.get("passed", 0) or 0),
        "failed": int(summary.get("failed", 0) or 0),
        "skipped": int(summary.get("skipped", 0) or 0),
        "duration": float(data.get("duration", 0.0) or 0.0),
    }


def load_coverage_percent(coverage_path: Path):
    if not coverage_path.exists():
        return None
    root = ET.parse(coverage_path).getroot()
    line_rate = float(root.attrib.get("line-rate", 0.0) or 0.0)
    return round(line_rate * 100, 2)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--allure-results", required=True)
    parser.add_argument("--reports", required=True)
    parser.add_argument("--jenkins-url", default="")
    parser.add_argument("--job-name", default="")
    parser.add_argument("--build-number", default="")
    parser.add_argument("--build-url", default="")
    args = parser.parse_args()

    allure_dir = Path(args.allure_results)
    reports_dir = Path(args.reports)
    allure_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    unit = load_summary(reports_dir / "unit_report.json")
    api = load_summary(reports_dir / "api_report.json")
    web = load_summary(reports_dir / "web_report.json")
    ui = load_summary(reports_dir / "ui_report.json")
    total = unit["total"] + api["total"] + web["total"] + ui["total"]
    passed = unit["passed"] + api["passed"] + web["passed"] + ui["passed"]
    failed = unit["failed"] + api["failed"] + web["failed"] + ui["failed"]
    skipped = unit["skipped"] + api["skipped"] + web["skipped"] + ui["skipped"]
    pass_rate = round((passed / total) * 100, 2) if total else 0.0
    coverage = load_coverage_percent(reports_dir / "coverage.xml")

    env_lines = {
        "PROJECT": "Mock CPE DevOps",
        "PIPELINE_MODE": os.environ.get("PIPELINE_MODE", "quick-local"),
        "BASE_URL": os.environ.get("BASE_URL", "N/A"),
        "SELENIUM_REMOTE_URL": os.environ.get("SELENIUM_REMOTE_URL", "not-used"),
        "BROWSER": os.environ.get("BROWSER", "not-used"),
        "HEADLESS": os.environ.get("HEADLESS", "not-used"),
        "UNIT_TESTS": str(unit["total"]),
        "API_TESTS": str(api["total"]),
        "WEB_UI_ROUTE_TESTS": str(web["total"]),
        "SELENIUM_UI_TESTS": str(ui["total"]),
        "TOTAL_TESTS": str(total),
        "PASSED": str(passed),
        "FAILED": str(failed),
        "SKIPPED": str(skipped),
        "PASS_RATE": f"{pass_rate}%",
        "COVERAGE": f"{coverage}%" if coverage is not None else "N/A",
    }
    with (allure_dir / "environment.properties").open("w", encoding="utf-8") as f:
        for key, value in env_lines.items():
            f.write(f"{key}={value}\n")

    try:
        build_order = int(args.build_number or 0)
    except ValueError:
        build_order = 0

    executor = {
        "name": "Jenkins",
        "type": "jenkins",
        "url": args.jenkins_url,
        "buildOrder": build_order,
        "buildName": f"#{args.build_number}",
        "buildUrl": args.build_url,
        "reportName": f"Mock CPE DevOps #{args.build_number}",
    }
    with (allure_dir / "executor.json").open("w", encoding="utf-8") as f:
        json.dump(executor, f, ensure_ascii=False, indent=2)

    categories = [
        {
            "name": "UI assertion failures",
            "matchedStatuses": ["failed"],
            "messageRegex": ".*AssertionError.*",
        },
        {
            "name": "Selenium/browser errors",
            "matchedStatuses": ["broken", "failed"],
            "traceRegex": ".*(selenium|TimeoutException|WebDriver).*",
        },
        {
            "name": "Backend/API failures",
            "matchedStatuses": ["failed"],
            "messageRegex": ".*(status_code|api|response).*",
        },
    ]
    with (allure_dir / "categories.json").open("w", encoding="utf-8") as f:
        json.dump(categories, f, ensure_ascii=False, indent=2)

    metrics = {
        "unit": unit,
        "api": api,
        "web": web,
        "ui": ui,
        "total": total,
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
        "pass_rate": pass_rate,
        "coverage": coverage,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
    }
    with (reports_dir / "test_metrics.json").open("w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)

    print(f"Allure metadata prepared in {allure_dir}")
    print(json.dumps(metrics, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
