"""Deploy local Jenkinsfile into the Jenkins job config via docker exec."""
import re, subprocess, sys, os
from xml.sax.saxutils import escape as xml_escape

WORKSPACE = r"c:\Users\LPC\mock-cpe-devops-test"
JENKINS_CONTAINER = os.environ.get("JENKINS_CONTAINER", "jenkins")
JENKINS_JOB_NAME = os.environ.get("JENKINS_JOB_NAME", "MockCPE-DevOps")
JENKINS_URL = os.environ.get("JENKINS_URL", "http://localhost:8080")

def main():
    os.chdir(WORKSPACE)

    # 1. Read local Jenkinsfile
    jf_path = os.path.join(WORKSPACE, "Jenkinsfile")
    with open(jf_path, "r", encoding="utf-8") as f:
        new_script = f.read()
    print(f"[1/4] Read Jenkinsfile: {len(new_script)} bytes", flush=True)

    # 2. Read current config from container
    r = subprocess.run(
        ["docker", "exec", JENKINS_CONTAINER, "cat", f"/var/jenkins_home/jobs/{JENKINS_JOB_NAME}/config.xml"],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    if r.returncode != 0 or not r.stdout.strip():
        print(f"FAIL: cannot read config. stderr={r.stderr}", flush=True)
        sys.exit(1)
    config_xml = r.stdout
    print(f"[2/4] Read container config: {len(config_xml)} bytes", flush=True)

    # 3. Replace <script>...</script>
    escaped = xml_escape(new_script)
    new_config = re.sub(
        r"(<script>).*?(</script>)",
        lambda m: m.group(1) + escaped + m.group(2),
        config_xml,
        flags=re.DOTALL,
    )
    new_config = new_config.replace("encoding='1.1'", "encoding='1.0'")
    print(f"[3/4] Replaced script: {len(new_config)} bytes", flush=True)

    # Verify the new script is in the config
    if new_script[:50] not in new_config:
        print("WARNING: new script content not found in config!", flush=True)

    # 4. Write to local temp file, then docker cp
    tmp_path = os.path.join(WORKSPACE, "temp_config.xml")
    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write(new_config)
    print(f"[4/4] Written temp file: {os.path.getsize(tmp_path)} bytes", flush=True)

    cp = subprocess.run(
        ["docker", "cp", tmp_path, f"{JENKINS_CONTAINER}:/var/jenkins_home/jobs/{JENKINS_JOB_NAME}/config.xml"],
        capture_output=True, text=True, encoding="utf-8"
    )
    print(f"docker cp RC={cp.returncode} stderr={cp.stderr}", flush=True)

    if cp.returncode != 0:
        # Try as root user with tee
        cmd_root = ["docker", "exec", "-u", "0", "-i", JENKINS_CONTAINER, "tee", f"/var/jenkins_home/jobs/{JENKINS_JOB_NAME}/config.xml"]
        w2 = subprocess.run(cmd_root, input=new_config, capture_output=True, text=True, encoding="utf-8")
        print(f"tee-as-root RC={w2.returncode} stderr={w2.stderr}", flush=True)

    # Cleanup temp file
    os.remove(tmp_path)

    # Verify
    v = subprocess.run(
        ["docker", "exec", JENKINS_CONTAINER, "sh", "-c", f"head -5 /var/jenkins_home/jobs/{JENKINS_JOB_NAME}/config.xml; echo '---SIZE---'; wc -c /var/jenkins_home/jobs/{JENKINS_JOB_NAME}/config.xml"],
        capture_output=True, text=True, encoding="utf-8"
    )
    print(f"Verify:\n{v.stdout}", flush=True)

    # Reload config
    reload_url = JENKINS_URL.rstrip("/") + "/reload-configuration"
    try:
        import urllib.request
        urllib.request.urlopen(reload_url)
        print("Jenkins config reload triggered.", flush=True)
    except Exception as e:
        print(f"Reload note: {e}", flush=True)

    print("\nDONE. Jenkins job config updated.", flush=True)


if __name__ == "__main__":
    main()