import xml.etree.ElementTree as ET
from pprint import pprint

from scantriage.schema import Finding, HostStatus, PortStatus, Vulnerability

FILE_XML = "./../tests/test-data/H_192.168.220.57.xml"

tree = ET.parse(FILE_XML)
root = tree.getroot()

findings = []

host_el = root.find("host")
if host_el is None:
    raise ValueError("No host element found")

address_el = host_el.find("address")
host_ip = address_el.get("addr") if address_el is not None else None
if host_ip is None:
    raise ValueError("Host IP value error")

status_el = host_el.find("status")
host_state = status_el.get("state") if status_el is not None else None
if host_state is None:
    raise ValueError("Host status value error")
host_status = HostStatus(host_state)

os_name = None
best_accuracy = -1
for osmatch in root.iter("osmatch"):
    name = osmatch.get("name")
    accuracy = osmatch.get("accuracy") 
    if accuracy == None:
        continue
    accuracy = int(accuracy)
    if accuracy is None: 
        raise ValueError ("accuracy error")
    if accuracy > best_accuracy:
        best_accuracy = accuracy
        os_name = name

for port_el in root.iter("port"):
    port_id = port_el.get("portid")
    if port_id is None:
        raise ValueError("Port number is missing")

    state_el = port_el.find("state")
    if state_el is None:
        raise ValueError(f"Port {port_id} has no state element")
    port_state = state_el.get("state")
    if port_state is None:
        raise ValueError(f"Port {port_id} has no state value")
    port_status = PortStatus(port_state)

    service_el = port_el.find("service")
    if service_el is None:
        continue

    service_name = service_el.get("name")
    if service_name is None:
        continue

    product = service_el.get("product")
    version = service_el.get("version")

    cpe_el = service_el.find("cpe")
    cpe = cpe_el.text if cpe_el is not None else None

    vulnerability = Vulnerability(
        name=service_name,
        product=product,
        evidence=f"{service_name} {product or ''} {version or ''}".strip(),
        version=version,
        common_platform_enumeration=cpe,
    )

    finding = Finding(
        host_ip=host_ip,
        host_status=host_status,
        port_status=port_status,
        port_number=int(port_id),
        service_name=service_name,
        operating_system= os_name,
        finding_type=vulnerability,
    )
    findings.append(finding)

for finding in findings:
    pprint(finding.model_dump())
    print()
    print()

