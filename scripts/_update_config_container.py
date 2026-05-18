import re
from xml.sax.saxutils import escape as xml_escape

with open('/tmp/Jenkinsfile', 'r') as f:
    script = f.read()
with open('/var/jenkins_home/jobs/MockCPE-DevOps/config.xml', 'r') as f:
    xml = f.read()
escaped = xml_escape(script)
new_xml = re.sub(r'(<script>).*?(</script>)', r'\1' + escaped + r'\2', xml, flags=re.DOTALL)
new_xml = new_xml.replace("encoding='1.1'", "encoding='1.0'")
with open('/var/jenkins_home/jobs/MockCPE-DevOps/config.xml', 'w') as f:
    f.write(new_xml)
print('Config updated OK')