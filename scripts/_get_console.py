"""Fetch Jenkins build console output for a specific build."""
import urllib.request, base64, sys, os

JENKINS_URL = "http://localhost:8081"
JOB_NAME = "MockCPE-DevOps"
auth_b64 = base64.b64encode(b"admin:admin").decode()
WORKSPACE = r"c:\Users\LPC\mock-cpe-devops-test"

build_num = sys.argv[1] if len(sys.argv) > 1 else "17"

req = urllib.request.Request(f"{JENKINS_URL}/job/{JOB_NAME}/{build_num}/consoleText")
req.add_header("Authorization", f"Basic {auth_b64}")
with urllib.request.urlopen(req) as resp:
    text = resp.read().decode("utf-8", errors="replace")

out_path = os.path.join(WORKSPACE, f"console_full_{build_num}.txt")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(text)
print(f"Written {len(text)} bytes to {out_path}")