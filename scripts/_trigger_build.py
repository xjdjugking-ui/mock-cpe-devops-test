"""Trigger a Jenkins build using crumb-based auth."""
import urllib.request
import urllib.parse
import http.cookiejar
import base64
import time
import json
import sys

JENKINS_URL = "http://localhost:8081"
JOB_NAME = "MockCPE-DevOps"
USER = "admin"
PASS = "admin"

def main():
    auth_b64 = base64.b64encode(f"{USER}:{PASS}".encode()).decode()
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

    # 1. Get crumb with session cookie
    crumb_url = f"{JENKINS_URL}/crumbIssuer/api/xml?xpath=concat(//crumbRequestField,\":\",//crumb)"
    req = urllib.request.Request(crumb_url)
    req.add_header("Authorization", f"Basic {auth_b64}")
    with opener.open(req) as resp:
        crumb_raw = resp.read().decode()
    field, val = crumb_raw.strip().split(":")
    print(f"Crumb obtained: {field}={val[:20]}...")

    # 2. Get last build number before trigger
    try:
        info_url = f"{JENKINS_URL}/job/{JOB_NAME}/api/json"
        req_info = urllib.request.Request(info_url)
        req_info.add_header("Authorization", f"Basic {auth_b64}")
        with opener.open(req_info) as resp:
            info = json.loads(resp.read().decode())
        last_build = info.get("lastBuild", {})
        prev_number = last_build.get("number", 0) if last_build else 0
        print(f"Last build number before trigger: {prev_number}")
    except Exception as e:
        print(f"Could not get last build: {e}")
        prev_number = 0

    # 3. Trigger build
    build_url = f"{JENKINS_URL}/job/{JOB_NAME}/buildWithParameters"
    payload = urllib.parse.urlencode({
        "RUN_UI_SMOKE": "true",
        "BASELINE_FIRMWARE_VERSION": "v2.0.1",
        "TARGET_FIRMWARE_VERSION": "v6.0.0",
    }).encode()
    req2 = urllib.request.Request(build_url, data=payload, method="POST")
    req2.add_header("Authorization", f"Basic {auth_b64}")
    req2.add_header(field, val)
    req2.add_header("Content-Type", "application/x-www-form-urlencoded")
    try:
        with opener.open(req2) as resp:
            print(f"Build triggered! Status: {resp.status}")
            print(f"Location: {resp.getheader('Location', 'none')}")
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")[:500]
        print(f"HTTP {e.code}: {body}")
        sys.exit(1)

    # 4. Wait a bit then check for new build
    time.sleep(3)
    try:
        req_info = urllib.request.Request(info_url)
        req_info.add_header("Authorization", f"Basic {auth_b64}")
        with opener.open(req_info) as resp:
            info = json.loads(resp.read().decode())
        last_build = info.get("lastBuild", {})
        new_number = last_build.get("number", 0) if last_build else 0
        print(f"New build number: {new_number}")
        if new_number > prev_number:
            print(f"BUILD TRIGGERED SUCCESSFULLY. New build: #{new_number}")
            # Check build status
            build_api = f"{JENKINS_URL}/job/{JOB_NAME}/{new_number}/api/json"
            req3 = urllib.request.Request(build_api)
            req3.add_header("Authorization", f"Basic {auth_b64}")
            with opener.open(req3) as resp:
                build_info = json.loads(resp.read().decode())
            print(f"Build result: {build_info.get('result', 'in-progress')}")
            print(f"Build URL: {build_info.get('url', 'none')}")
        else:
            print("No new build number detected yet. Build may be queued.")
    except Exception as e:
        print(f"Check error: {e}")


if __name__ == "__main__":
    main()
