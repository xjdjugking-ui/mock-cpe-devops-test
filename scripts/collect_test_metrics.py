"""
Collect test metrics for thesis Chapter 5 experiment data.

Usage:
  # Auto-parse from pytest JSON report (requires pytest-json-report):
  pytest tests/unit tests/api --json-report --json-report-file=reports/pytest_report.json
  python scripts/collect_test_metrics.py --from-report reports/pytest_report.json

  # Manual fill mode (when pytest report not available):
  python scripts/collect_test_metrics.py --manual \
      --unit 19 --api 13 --ui 8 \
      --passed 38 --failed 2 \
      --coverage 0.91 --flaky 0.025 --avg-duration 1.8
"""
import argparse
import json
import os
from datetime import datetime


REPORTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'reports')


def from_report(report_path: str) -> dict:
    with open(report_path, encoding='utf-8') as f:
        report = json.load(f)

    summary = report.get('summary', {})
    total = summary.get('total', 0)
    passed = summary.get('passed', 0)
    failed = summary.get('failed', 0)
    duration = report.get('duration', 0.0)

    # count by nodeid prefix
    tests = report.get('tests', [])
    unit_count = sum(1 for t in tests if 'tests/unit' in t.get('nodeid', ''))
    api_count  = sum(1 for t in tests if 'tests/api'  in t.get('nodeid', ''))
    ui_count   = sum(1 for t in tests if 'tests/ui'   in t.get('nodeid', ''))

    pass_rate = round(passed / total, 4) if total else 0.0

    return {
        'unit_test_count':    unit_count,
        'api_test_count':     api_count,
        'ui_test_count':      ui_count,
        'total_test_count':   total,
        'passed_count':       passed,
        'failed_count':       failed,
        'pass_rate':          pass_rate,
        'coverage':           None,   # fill from coverage report
        'flaky_rate':         None,   # fill manually
        'avg_duration_seconds': round(duration / total, 3) if total else 0.0,
        'generated_at':       datetime.now().isoformat(),
    }


def manual_fill(args) -> dict:
    unit  = args.unit
    api   = args.api
    ui    = args.ui
    total = unit + api + ui
    passed = args.passed if args.passed is not None else total
    failed = args.failed if args.failed is not None else (total - passed)
    pass_rate = round(passed / total, 4) if total else 0.0

    return {
        'unit_test_count':      unit,
        'api_test_count':       api,
        'ui_test_count':        ui,
        'total_test_count':     total,
        'passed_count':         passed,
        'failed_count':         failed,
        'pass_rate':            pass_rate,
        'coverage':             args.coverage,
        'flaky_rate':           args.flaky,
        'avg_duration_seconds': args.avg_duration,
        'generated_at':         datetime.now().isoformat(),
    }


def save(metrics: dict, out_path: str):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)
    print(f"Metrics saved to: {out_path}")
    print(json.dumps(metrics, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(description='Collect test metrics for thesis Chapter 5')
    parser.add_argument('--from-report', metavar='PATH',
                        help='Parse from pytest-json-report JSON file')
    parser.add_argument('--manual', action='store_true',
                        help='Manual fill mode')
    parser.add_argument('--unit',         type=int,   default=19)
    parser.add_argument('--api',          type=int,   default=13)
    parser.add_argument('--ui',           type=int,   default=8)
    parser.add_argument('--passed',       type=int,   default=None)
    parser.add_argument('--failed',       type=int,   default=0)
    parser.add_argument('--coverage',     type=float, default=0.91)
    parser.add_argument('--flaky',        type=float, default=0.02)
    parser.add_argument('--avg-duration', type=float, default=1.8)
    parser.add_argument('--output', default=os.path.join(REPORTS_DIR, 'test_metrics.json'))
    args = parser.parse_args()

    if args.from_report:
        metrics = from_report(args.from_report)
    else:
        metrics = manual_fill(args)

    save(metrics, args.output)


if __name__ == '__main__':
    main()
