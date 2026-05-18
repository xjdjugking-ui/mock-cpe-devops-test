"""Check Jenkins build status and write results to file."""
import urllib.request, json, base64, os, sys

JENKINS_URL = "http://localhost:8081"
JOB_NAME = "MockCPE-DevOps"
WORKSPACE = r"c:\Users\LPC\mock-cpe-devops-test"
auth_b64 = base64.b64encode(b"admin:admin").decode()


def api(path):
    req = urllib.request.Request(f"{JENKINS_URL}{path}")
    req.add_header("Authorization", f"Basic {auth_b64}")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def main():
    out_file = os.path.join(WORKSPACE, "build_result.txt")
    lines = []

    try:
        info = api(f"/job/{JOB_NAME}/api/json")
        num = info.get("lastBuild", {}).get("number", 0)
        lines.append(f"Last build: #{num}")

        if num > 0:
            build = api(f"/job/{JOB_NAME}/{num}/api/json")
            result = build.get("result", "IN-PROGRESS")
            building = build.get("building", False)
            dur_ms = build.get("duration", 0)
            url = build.get("url", "")
            lines.append(f"Result: {result}")
            lines.append(f"Building: {building}")
            lines.append(f"Duration: {dur_ms // 1000}s")
            lines.append(f"URL: {url}")

            # Check console output for errors
            try:
                req_log = urllib.request.Request(
                    f"{JENKINS_URL}/job/{JOB_NAME}/{num}/consoleText"
                )
                req_log.add_header("Authorization", f"Basic {auth_b64}")
                with urllib.request.urlopen(req_log) as resp:
                    console = resp.read().decode("utf-8", errors="replace")
                # Check for FAILURE indicators
                if "FAILED" in console:
                    lines.append("ERROR: Tests FAILED detected in console")
                if "SUCCESS" in console:
                    lines.append("OK: SUCCESS found in console")
                # Check for Allure
                if "Allure" in console or "allure" in console:
                    lines.append("OK: Allure referenced in console")
                # Get last 10 lines
                tail = console.strip().split("\n")[-10:]
                lines.append("\n--- Last 10 console lines ---")
                lines.extend(tail)
            except Exception as e:
                lines.append(f"Console error: {e}")

            # Check artifacts
            artifacts = build.get("artifacts", [])
            lines.append(f"\nArtifacts: {len(artifacts)}")
            for a in artifacts:
                lines.append(f"  - {a.get('relativePath', a.get('fileName', '?'))}")
        else:
            lines.append("No builds found!")
    except Exception as e:
        lines.append(f"ERROR: {e}")

    text = "\n".join(lines)
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"Written {len(text)} bytes to {out_file}")
    print(text)


if __name__ == "__main__":
    main()