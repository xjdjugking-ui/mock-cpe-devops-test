"""Generate a Jenkins-friendly HTML build dashboard."""
import argparse
import html
import json
from pathlib import Path
import xml.etree.ElementTree as ET


def load_report(path: Path) -> dict:
    if not path.exists():
        return {"summary": {}, "duration": 0.0}
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def summary(data: dict) -> dict:
    s = data.get("summary", {})
    total = int(s.get("total", 0) or 0)
    passed = int(s.get("passed", 0) or 0)
    failed = int(s.get("failed", 0) or 0)
    skipped = int(s.get("skipped", 0) or 0)
    duration = float(data.get("duration", 0.0) or 0.0)
    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
        "duration": duration,
    }


def coverage_rate(path: Path) -> str:
    if not path.exists():
        return "N/A"
    root = ET.parse(path).getroot()
    line_rate = float(root.attrib.get("line-rate", 0.0) or 0.0)
    return f"{line_rate * 100:.1f}%"


def card(title: str, value: str, detail: str, tone: str = "green") -> str:
    return f"""
      <section class="metric {tone}">
        <div class="metric-title">{html.escape(title)}</div>
        <div class="metric-value">{html.escape(value)}</div>
        <div class="metric-detail">{html.escape(detail)}</div>
      </section>
    """


def stage(name: str, command: str, seconds: str) -> str:
    return f"""
      <div class="stage">
        <div class="stage-dot">OK</div>
        <div class="stage-name">{html.escape(name)}</div>
        <div class="stage-command">{html.escape(command)}</div>
        <div class="stage-duration">{html.escape(seconds)}</div>
      </div>
    """


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reports", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--job-name", required=True)
    parser.add_argument("--build-number", required=True)
    parser.add_argument("--build-url", required=True)
    parser.add_argument("--blue-url", required=True)
    parser.add_argument("--allure-url", required=True)
    args = parser.parse_args()

    reports_dir = Path(args.reports)
    unit = summary(load_report(reports_dir / "unit_report.json"))
    api = summary(load_report(reports_dir / "api_report.json"))
    web = summary(load_report(reports_dir / "web_report.json"))
    ui = summary(load_report(reports_dir / "ui_report.json"))
    total = unit["total"] + api["total"] + web["total"] + ui["total"]
    passed = unit["passed"] + api["passed"] + web["passed"] + ui["passed"]
    failed = unit["failed"] + api["failed"] + web["failed"] + ui["failed"]
    pass_rate = round((passed / total) * 100, 2) if total else 0.0
    coverage = coverage_rate(reports_dir / "coverage.xml")
    status = "SUCCESS" if failed == 0 and total > 0 else "FAILED"
    status_tone = "green" if status == "SUCCESS" else "red"
    quick_flow_detail = "unit + api + web-ui + selenium under 10 min"

    html_text = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Mock CPE DevOps CI Dashboard</title>
  <style>
    :root {{
      --bg: #f5f7fb;
      --panel: #ffffff;
      --line: #d9e2ef;
      --text: #172033;
      --muted: #6b778c;
      --green: #24a148;
      --red: #da1e28;
      --blue: #0f62fe;
      --ink: #111827;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font: 14px/1.45 -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    header {{
      height: 56px;
      background: #0b0f19;
      color: white;
      display: flex;
      align-items: center;
      padding: 0 24px;
      gap: 14px;
    }}
    .brand {{
      width: 32px;
      height: 32px;
      border-radius: 6px;
      background: linear-gradient(135deg, #d33838, #f0b429 45%, #2e7d32 46%);
    }}
    .wrap {{ max-width: 1180px; margin: 0 auto; padding: 22px; }}
    .summary {{
      display: grid;
      grid-template-columns: 1.2fr repeat(4, .7fr);
      gap: 14px;
      margin-bottom: 18px;
    }}
    .panel, .metric, .console {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      box-shadow: 0 1px 2px rgba(15, 23, 42, .04);
    }}
    .build-card {{ padding: 18px; }}
    .build-title {{ font-size: 24px; font-weight: 700; margin-bottom: 8px; }}
    .badge {{
      display: inline-flex;
      align-items: center;
      min-height: 28px;
      padding: 4px 12px;
      border-radius: 6px;
      color: white;
      font-weight: 700;
      background: var(--green);
    }}
    .badge.red {{ background: var(--red); }}
    .links {{ display: flex; gap: 10px; flex-wrap: wrap; margin-top: 14px; }}
    .links a {{
      color: var(--blue);
      text-decoration: none;
      border: 1px solid #c8d7ff;
      border-radius: 6px;
      padding: 7px 10px;
      background: #f8fbff;
      font-weight: 600;
    }}
    .metric {{ padding: 14px; min-height: 112px; }}
    .metric-title {{ color: var(--muted); font-weight: 600; }}
    .metric-value {{ font-size: 28px; font-weight: 800; margin-top: 10px; }}
    .metric-detail {{ color: var(--muted); margin-top: 4px; }}
    .metric.green .metric-value {{ color: var(--green); }}
    .metric.red .metric-value {{ color: var(--red); }}
    .section-title {{ font-size: 18px; font-weight: 700; margin: 22px 0 12px; }}
    .stages {{
      display: grid;
      grid-template-columns: repeat(6, minmax(120px, 1fr));
      gap: 12px;
      align-items: stretch;
    }}
    .stage {{
      border: 2px solid #93d3a2;
      background: #f7fff8;
      border-radius: 8px;
      padding: 12px;
      min-height: 126px;
      display: grid;
      grid-template-rows: auto auto 1fr auto;
      gap: 7px;
    }}
    .stage-dot {{
      width: 24px;
      height: 24px;
      border-radius: 50%;
      background: var(--green);
      color: white;
      display: grid;
      place-items: center;
      font-weight: 800;
    }}
    .stage-name {{ font-weight: 700; }}
    .stage-command {{ color: var(--ink); font-family: Consolas, monospace; font-size: 12px; }}
    .stage-duration {{ color: var(--muted); font-size: 12px; }}
    .grid {{ display: grid; grid-template-columns: 1.2fr .8fr; gap: 14px; margin-top: 18px; }}
    .console {{ padding: 16px; background: #050a14; color: #d1e7dd; min-height: 320px; }}
    pre {{ margin: 0; white-space: pre-wrap; font: 13px/1.45 Consolas, monospace; }}
    .side {{ display: grid; gap: 14px; }}
    .mini {{ padding: 16px; }}
    .mini h3 {{ margin: 0 0 12px; font-size: 15px; }}
    .row {{ display: flex; justify-content: space-between; border-top: 1px solid var(--line); padding: 9px 0; }}
    .row:first-of-type {{ border-top: 0; }}
    @media (max-width: 920px) {{
      .summary, .grid, .stages {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <header><div class="brand"></div><strong>Jenkins</strong><span>Mock CPE DevOps Pipeline</span></header>
  <main class="wrap">
    <section class="summary">
      <div class="panel build-card">
        <div class="build-title">{html.escape(args.job_name)} <span style="color:#64748b">#{html.escape(args.build_number)}</span></div>
        <span class="badge {'' if status_tone == 'green' else 'red'}">{status}</span>
        <div class="links">
          <a href="{html.escape(args.build_url)}">Jenkins Build</a>
          <a href="{html.escape(args.blue_url)}">Blue Ocean</a>
          <a href="{html.escape(args.build_url)}console">Console</a>
          <a href="{html.escape(args.allure_url)}">HTML Report</a>
        </div>
      </div>
      {card("Unit Tests", f"{unit['passed']} passed", f"{unit['failed']} failed / {unit['total']} total", "green" if unit["failed"] == 0 else "red")}
      {card("API Tests", f"{api['passed']} passed", f"{api['failed']} failed / {api['total']} total", "green" if api["failed"] == 0 else "red")}
      {card("Web-UI Routes", f"{web['passed']} passed", f"{web['failed']} failed / {web['total']} total", "green" if web["failed"] == 0 else "red")}
      {card("Coverage", coverage, "coverage.xml", "green" if coverage != "N/A" else "red")}
    </section>

    <h2 class="section-title">Pipeline Stages</h2>
    <section class="stages">
      {stage("1. Checkout", "git checkout / poll SCM", "instant")}
      {stage("2. Verify Python", "python + pytest preinstalled", "no network install")}
      {stage("3. Prepare Reports", "junit xml -> json dashboard", "local scripts only")}
      {stage("4. Run Unit Tests", "pytest tests/unit", f"{unit['duration']:.1f}s")}
      {stage("5. Run API Tests", "pytest tests/api/test_api.py", f"{api['duration']:.1f}s")}
      {stage("6. Run Web-UI Routes", "pytest tests/api/test_routes_html.py", f"{web['duration']:.1f}s")}
    </section>

    <section class="grid">
      <div class="console">
        <pre>Pipeline summary
================
Unit tests : {unit['passed']}/{unit['total']} passed
API tests  : {api['passed']}/{api['total']} passed
Web-UI     : {web['passed']}/{web['total']} passed
Selenium UI: {ui['passed']}/{ui['total']} passed
Coverage   : {coverage}
HTML report: generated and published
Artifacts  : allure-results, reports
Status     : {status}</pre>
      </div>
      <aside class="side">
        <div class="panel mini">
          <h3>Quick CI Status</h3>
          <div class="row"><span>pipeline mode</span><strong style="color:var(--green)">full-ci</strong></div>
          <div class="row"><span>runner</span><strong style="color:var(--green)">docker + pytest</strong></div>
          <div class="row"><span>time budget</span><strong>10 minutes</strong></div>
        </div>
        <div class="panel mini">
          <h3>Report Links</h3>
          <div class="row"><span>HTML Report</span><a href="{html.escape(args.allure_url)}">Open</a></div>
          <div class="row"><span>Blue Ocean</span><a href="{html.escape(args.blue_url)}">Open</a></div>
          <div class="row"><span>Artifacts</span><a href="{html.escape(args.build_url)}artifact/">Open</a></div>
        </div>
      </aside>
    </section>
  </main>
</body>
</html>
"""
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html_text, encoding="utf-8")
    print(f"CI dashboard written to {out}")


if __name__ == "__main__":
    main()
