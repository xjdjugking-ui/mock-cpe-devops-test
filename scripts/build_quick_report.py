"""Build lightweight JSON summaries from JUnit XML for quick CI."""
import argparse
import json
from pathlib import Path
import xml.etree.ElementTree as ET


def junit_to_summary(path: Path) -> dict:
    if not path.exists():
        return {
            "created": None,
            "duration": 0.0,
            "exitcode": 0,
            "root": str(path),
            "summary": {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "skipped": 0,
                "error": 0,
            },
        }

    root = ET.parse(path).getroot()
    suite = root if root.tag == "testsuite" else root.find("testsuite")
    if suite is None:
        raise ValueError(f"No testsuite node found in {path}")

    total = int(suite.attrib.get("tests", 0) or 0)
    failures = int(suite.attrib.get("failures", 0) or 0)
    errors = int(suite.attrib.get("errors", 0) or 0)
    skipped = int(suite.attrib.get("skipped", 0) or 0)
    passed = max(total - failures - errors - skipped, 0)
    duration = float(suite.attrib.get("time", 0.0) or 0.0)

    return {
        "created": None,
        "duration": duration,
        "exitcode": 0 if failures == 0 and errors == 0 else 1,
        "root": str(path),
        "summary": {
            "total": total,
            "passed": passed,
            "failed": failures + errors,
            "skipped": skipped,
            "error": errors,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--junit", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    payload = junit_to_summary(Path(args.junit))
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Quick JSON report written to {out}")


if __name__ == "__main__":
    main()
