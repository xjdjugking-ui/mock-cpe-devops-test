"""Wait for a Jenkins build to complete, then write result + console to files."""
import urllib.request, json, base64, os, time, sys

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
    # Wait for new build (> 17)
    max_wait = 180  # seconds
    new_num = None
    for i in range(max_wait // 3):
        info = api(f"/job/{JOB_NAME}/api/json")
        num = info.get("lastBuild", {}).get("number", 0)
        if num > 17:
            new_num = num
            print(f"Build #{new_num} detected after {i * 3}s")
            break
        time.sleep(3)
    else:
        print(f"No new build after {max_wait}s, checking current...")
        info = api(f"/job/{JOB_NAME}/api/json")
        new_num = info.get("lastBuild", {}).get("number", 0)

    if new_num <= 17:
        print("ERROR: No new build started")
        sys.exit(1)

    # Wait for build to finish
    for i in range(max_wait // 3):
        build = api(f"/job/{JOB_NAME}/{new_num}/api/json")
        if not build.get("building", True):
            result = build.get("result", "UNKNOWN")
            dur = build.get("duration", 0)
            url = build.get("url", "")
            print(f"Build #{new_num} finished: {result} ({dur // 1000}s)")
            print(f"URL: {url}")

            # Fetch console output
            try:
                req_log = urllib.request.Request(
                    f"{JENKINS_URL}/job/{JOB_NAME}/{new_num}/consoleText"
                )
                req_log.add_header("Authorization", f"Basic {auth_b64}")
                with urllib.request.urlopen(req_log) as resp:
                    console = resp.read().decode("utf-8", errors="replace")

                console_path = os.path.join(
                    WORKSPACE, f"console_full_{new_num}.txt"
                )
                with open(console_path, "w", encoding="utf-8") as f:
                    f.write(console)
                print(f"Console written: {console_path}")

                # Summary
                lines = console.strip().split("\n")
                tail = lines[-15:]
                print("\n--- Last 15 lines ---")
                for line in tail:
                    print(line)
            except Exception as e:
                print(f"Console error: {e}")

            # Result summary
            result_path = os.path.join(WORKSPACE, f"build_result_{new_num}.txt")
            with open(result_path, "w", encoding="utf-8") as f:
                f.write(f"Build: #{new_num}\n")
                f.write(f"Result: {result}\n")
                f.write(f"Duration: {dur // 1000}s\n")
                f.write(f"URL: {url}\n")
                artifacts = build.get("artifacts", [])
                f.write(f"Artifacts: {len(artifacts)}\n")
                for a in artifacts:
                    f.write(f"  - {a.get('relativePath', a.get('fileName', '?'))}\n")
            print(f"Result written: {result_path}")
            return result == "SUCCESS"
        time.sleep(3)
    else:
        print(f"Build still running after {max_wait}s")
        sys.exit(1)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 0)  # Always exit 0 for scripting