#!/usr/bin/env python3
"""Update the Jenkins job config.xml with the local Jenkinsfile content."""
import urllib.request
import urllib.parse
import http.cookiejar
import base64
import os
import re
from xml.sax.saxutils import escape as xml_escape

JENKINS_URL = os.environ.get("JENKINS_URL", "http://localhost:8080")
JOB_NAME = os.environ.get("JENKINS_JOB_NAME", "MockCPE-DevOps")
USER = os.environ.get("JENKINS_USER", "admin")
PASS = os.environ.get("JENKINS_PASS", "admin")

def main():
    auth_b64 = base64.b64encode(f"{USER}:{PASS}".encode()).decode()
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

    # 1. Fetch crumb
    crumb_url = (
        JENKINS_URL + "/crumbIssuer/api/xml"
        "?xpath=concat(//crumbRequestField,\":\",//crumb)"
    )
    crumb_req = urllib.request.Request(crumb_url)
    crumb_req.add_header("Authorization", f"Basic {auth_b64}")
    with opener.open(crumb_req) as f:
        crumb_raw = f.read().decode("utf-8")
    field, val = crumb_raw.split(":")
    print(f"Crumb: {field}={val}")

    headers = {
        field: val,
        "Content-Type": "application/xml; charset=utf-8",
        "Authorization": f"Basic {auth_b64}",
    }

    # 2. Fetch current config
    config_url = f"{JENKINS_URL}/job/{JOB_NAME}/config.xml"
    req = urllib.request.Request(config_url, headers=headers)
    with opener.open(req) as f:
        config_xml = f.read().decode("utf-8")

    print(f"Fetched config: {len(config_xml)} bytes")

    # 3. Read new Jenkinsfile content (relative to workspace root)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_root = os.path.dirname(script_dir)
    jenkinsfile_path = os.path.join(workspace_root, "Jenkinsfile")
    with open(jenkinsfile_path, "r", encoding="utf-8") as f:
        new_script = f.read()
    print(f"New Jenkinsfile: {len(new_script)} bytes")

    # 4. Escape for XML safely
    escaped = xml_escape(new_script)

    # 5. Replace the <script>...</script> content
    new_config = re.sub(
        r"(<script>).*?(</script>)",
        lambda m: m.group(1) + escaped + m.group(2),
        config_xml,
        flags=re.DOTALL,
    )

    # Fix encoding version if needed
    new_config = new_config.replace("encoding='1.1'", "encoding='1.0'")

    # 6. POST back
    data = new_config.encode("utf-8")
    req_post = urllib.request.Request(
        config_url, data=data, headers=headers, method="POST"
    )
    try:
        with opener.open(req_post) as resp:
            print(f"POST status: {resp.status}")
            print("Jenkins job config updated successfully!")
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")[:500]
        print(f"HTTP {e.code}: {body}")
        raise


if __name__ == "__main__":
    main()