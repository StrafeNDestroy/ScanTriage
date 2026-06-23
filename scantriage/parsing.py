import yaml 
import logging 
from dataclasses import dataclass


from rich.logging import RichHandler
from pydantic import ValidationError
from pathlib import Path
from pprint import pprint
import xml.etree.ElementTree as ET

from scantriage.enums import HostStatus, PortStatus
from scantriage.schema import Authentication, Finding, Misconfiguration, Vulnerability

@dataclass 
class HostInfo:
    ip:str 
    status:HostStatus

@dataclass
class OSInfo:
    name: str 
    accuracy: int 

@dataclass
class PortInfo:
    number: int
    protocol: str
    state: str
    service: str



PROJECT_ROOT = Path(__file__).parent.parent
FILE_XML = f"{PROJECT_ROOT}/tests/test-data/H_192.168.220.57.xml"
FILE_YAML = f"{PROJECT_ROOT}/tests/test-data/scan_results.yaml"


logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        handlers=[RichHandler()],
)


def Extract_Host( root:ET.Element[str]) -> HostInfo:

    host_el = root.find("host")
    if host_el is None:
        raise ValueError("No host element found")

    address_el = host_el.find("address")
    host_ip = address_el.get("addr") if address_el is not None else None 
    if host_ip is None:
        raise ValueError("Host IP value error")

    status_el = host_el.find("status")
    raw_status = status_el.get("state") if status_el is not None else None 
    if raw_status is None:
        raise ValueError("Host status value error")
    try:
        host_status = HostStatus(raw_status)
    except ValueError:
        host_status = HostStatus.UNKNOWN

    return HostInfo(ip=host_ip,status=host_status) 



def Extract_OS(root:ET.Element[str]) -> OSInfo | None:
    best_os_name = None
    best_accuracy = -1

    for osmatch in root.iter("osmatch"):
        os_name = osmatch.get("name")

        os_accuracy = osmatch.get("accuracy") 
        if os_accuracy is None:
            continue
        os_accuracy = int(os_accuracy)

        if os_accuracy > best_accuracy:
            best_accuracy = os_accuracy
            best_os_name = os_name

    if best_os_name is None:
        return None
    return OSInfo(name=best_os_name,accuracy=best_accuracy) 


def Extract_Ports(root:ET.Element[str]) -> PortStatus | None:

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
        evidence=f"{service_name} {product or ''} {version or ''}"
    return finding


def Parse_XML(file:Path):
    tree = ET.parse(str(file))
    root = tree.getroot()
    Extract_Host(root)
    Extract_OS(root)
    Extract_Ports(root)

def Assign_XML():
    vulnerability = Vulnerability(
        name=service_name,
        product=product,
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
        evidence=evidence
    )
    findings.append(finding)

for finding in findings:
    pprint(finding.model_dump())
    print()
    print()

def Yaml_Parse(file:Path): 
    findings = []
    errors = {}

    with file.open() as file_content: 
        data = yaml.safe_load(file_content)

    host_ip_yml = data["host"]
    port_number_yml=data["port"]
    service_name_yml = data["service"]

    for category in data["scans"]:
        checks = data["scans"][category]
        for check in checks:
            if  category == "misconfiguration_checks":
                name = check.get("name")
                command = check.get("command")
                exit_code = check.get("exit_code")
                stdout = check.get("stdout")
                stderr = check.get("stderr")
                skipped = check.get("skipped")
                skip_reason = check.get("skip_reason")

                evidence = f"""{exit_code or ''} 
                {stdout or ''} {stderr or ''} 
                {skipped or ''}
                {skip_reason or ''}"""

                try:
                    check_type =Misconfiguration(
                        name=name,
                        command=command,
                    )
            
                except ValidationError as error: 
                    logging.warning("Failed to build class %s: %s\n", check.get("name"),error)
                    errors[check.get("name")] = error
                    continue


            elif category == "authentication_testing":
                name = check.get("name")
                command = check.get("command")
                username = check.get("username")
                password = check.get("password")
                confirmed = check.get("confirmed")

                exit_code = check.get("exit_code")
                stdout = check.get("stdout")
                stderr = check.get("stderr")
                skipped = check.get("skipped")
                skip_reason = check.get("skip_reason")
                
                if skipped == True:
                    continue
                
                evidence = f"""{exit_code or ''} 
                {stdout or ''} {stderr or ''} 
                {skipped or ''}
                {skip_reason or ''}"""


                try:
                    check_type =  Authentication(
                        command=command,
                        username=username,
                        password=password,
                        authenticated=confirmed
                    )
                except ValidationError as error: 
                    logging.warning("Failed to build class %s: %s\n", check.get("name"),error)
                    errors[check.get("name")] = error
                    continue

            else: 
                continue
            
            try: 
                finding = Finding(
                    host_ip=host_ip_yml,
                    host_status=HostStatus.UP,
                    port_status=PortStatus.OPEN,
                    port_number=int(port_number_yml),
                    service_name=service_name_yml,
                    operating_system= None,
                    evidence= evidence,
                    finding_type= check_type
                )
                findings.append(finding)
            except ValidationError as error: 
                logging.warning("Failed to build class %s: %s\n", check.get("name"),error)
                errors[check.get("name")] = error
    return findings
 
                
PATH_YML = Path(FILE_YAML)
yaml_findings = Yaml_Parse(PATH_YML)
for finding in yaml_findings:
    pprint(finding.model_dump())
    print() 
        



