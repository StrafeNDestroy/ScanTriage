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
class ConnectivityInfo:
    """A host's network identity and reachability, extracted from a scan.

    Attributes:
        ip: The host's IP address.
        status: Whether the host was up, down, or unknown (HostStatus).
    """
    ip: str
    status: HostStatus

    ip:str 
    status:HostStatus

@dataclass
class OSInfo:
    """A detected operating system guess for a host.

    Attributes:
        name: The OS name nmap reported (e.g. "Linux 3.13").
        accuracy: The confidence percentage of the match, highest among all guesses.
    """
    name: str 
    accuracy: int 

@dataclass
class PortInfo:
    """One scanned port and its service details, extracted from nmap XML.

    An intermediate structure: the parser fills these per port, then flattens them into
    Finding objects. Product, version, and CPE are optional because not every service
    exposes them.

    Attributes:
        number: The port number.
        protocol: The transport protocol (e.g. "tcp").
        state: The port's status (open, closed, filtered, etc.).
        service: The service name detected on the port (e.g. "ssh", "http").
        cpe: The CPE identifier for the service, or None if not reported.
        evidence: A short human readable summary of the service and version.
        product: The product name behind the service (e.g. "Apache httpd"), or None.
        version: The detected version string, or None if not reported.
    """
    number: int
    protocol: str
    state: str
    service: str
    cpe: str | None
    evidence: str
    product: str | None       
    version: str | None



PROJECT_ROOT = Path(__file__).parent.parent
FILE_XML = f"{PROJECT_ROOT}/tests/test-data/H_192.168.220.57.xml"
FILE_YAML = f"{PROJECT_ROOT}/tests/test-data/scan_results.yaml"


logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        handlers=[RichHandler()],
        )


def extract_host( root:ET.Element) -> ConnectivityInfo:
    """Extract the host's IP and reachability status from an nmap XML tree.

    Reads the host element, its address, and its status. The raw status string is
    coerced to a HostStatus; an unrecognized value falls back to UNKNOWN rather than
    failing, since an odd status should not sink the parse.

    Args:
        root: The root element of a parsed nmap XML document.

    Returns:
        A ConnectivityInfo holding the host IP and its HostStatus.

    Raises:
        ValueError: If the host element, its address, or its status is missing. These
            are required for a usable finding, so their absence is a hard error.
    """
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

    return ConnectivityInfo(ip=host_ip,status=host_status) 



def extract_os(root:ET.Element) -> OSInfo | None:
    """Extract the best operating system guess from an nmap XML tree.

    Scans every osmatch entry and keeps the one with the highest accuracy. Entries
    without an accuracy value are skipped. OS detection often finds nothing, so a
    missing OS is a valid result, not an error.

    Args:
        root: The root element of a parsed nmap XML document.

    Returns:
        An OSInfo with the highest accuracy match, or None if no OS was detected.
    """
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



def extract_ports(root:ET.Element) -> list[PortInfo]:
    """Extract every scanned port and its service details from an nmap XML tree.

    Iterates all port elements, capturing protocol, number, state, and (when a service
    is present) service name, product, version, and CPE. Ports with no service element
    or no service name are skipped, since they yield no useful finding. Product,
    version, and CPE are optional and default to None when absent.

    Args:
        root: The root element of a parsed nmap XML document.

    Returns:
        A list of PortInfo objects, one per port that has an identifiable service.

    Raises:
        ValueError: If a port is missing its protocol, port number, state element, or
            state value. These are required for every port.
    """
    host_port_data = []

    for port_el in root.iter("port"):
        port_protocol = port_el.get("protocol")

        if port_protocol is None: 
            raise ValueError("Protocol is missing")

        port_number = port_el.get("portid")
        if port_number is None:
            raise ValueError("Port number is missing")
        port_number = int(port_number)

        state_el = port_el.find("state")
        if state_el is None:
            raise ValueError(f"Port {port_number} has no state element")

        port_state = state_el.get("state")
        if port_state is None:
            raise ValueError(f"Port {port_number} has no state value")
        port_status = PortStatus(port_state)

        service_el = port_el.find("service")
        if service_el is None:
            continue

        service_name = service_el.get("name")
        if service_name is None:
            continue



        product = service_el.get("product")
        version = service_el.get("version")

        port_cpe = service_el.find("cpe")
        port_cpe = port_cpe.text if port_cpe is not None else None

        port_evidence=f"{service_name} {product or ''} {version or ''}"

        port_data = PortInfo(
                protocol=port_protocol,
                number=port_number,
                state=port_status,
                service=service_name,
                cpe=port_cpe,
                evidence=port_evidence,
                product= product,
                version= version
        )
        host_port_data.append(port_data)
    return host_port_data


def assign_xml(connectivity:ConnectivityInfo,os_info:OSInfo | None,port:PortInfo) -> Finding:
    """Assemble one Finding from the host, OS, and a single port.

    Combines the host level data (shared across all of a host's findings) with one
    port's details into a flat Finding carrying a Vulnerability detail. The OS name is
    used when present and left as None when no OS was detected.

    Args:
        connectivity: The host's IP and status, shared by every finding for the host.
        os_info: The detected OS, or None if detection found nothing.
        port: The single port this finding describes.

    Returns:
        A Finding for the given port, with a Vulnerability finding_type.
    """
    finding = Finding(
        host_ip=connectivity.ip,
        host_status=connectivity.status,
        port_status=port.state,                              
        port_number=port.number,
        service_name=port.service,
        operating_system=os_info.name if os_info is not None else None,
        evidence=port.evidence,
        finding_type=Vulnerability(
            name=port.service,
            product=port.product,
            version=port.version,
            common_platform_enumeration=port.cpe,
        ),
    )
    return finding


def parse_xml(file:Path) -> list[Finding]:
    """Parse an nmap XML file into a flat list of Findings.

    Reads the file, extracts the host connectivity and OS once, then builds one Finding
    per discovered port. The host and OS data are copied onto each finding so the output
    stays flat (one discrete issue per record).

    Args:
        file: Path to the nmap XML file.

    Returns:
        A list of Findings, one per port with an identifiable service.
    """
    tree = ET.parse(file)
    root = tree.getroot()
    connectivity = extract_host(root)
    os_info = extract_os(root)

    findings = []
    for port in extract_ports(root):
        finding = assign_xml(
                    connectivity=connectivity,
                    os_info=os_info,
                    port=port
                  )
        findings.append(finding)

    return findings

def build_evidence(check: dict) -> str:
    """Build the raw evidence string from a check's output fields.

    Joins the check's exit code, stdout, stderr, skipped flag, and skip reason into one
    labeled, multiline string. The labels make the evidence easier for a later model to
    parse. Missing fields render as empty rather than the word None. The parser captures
    this raw output without interpreting it; judging it is a later layer's job.

    Args:
        check: One check dictionary from a scan category.

    Returns:
        A labeled multiline string of the check's output.
    """
    exit_code = check.get("exit_code")
    stdout = check.get("stdout")
    stderr = check.get("stderr")
    skipped = check.get("skipped")
    skip_reason = check.get("skip_reason")
    return (
        f"exit_code: {exit_code or ''}\n"
        f"stdout: {stdout or ''}\n"
        f"stderr: {stderr or ''}\n"
        f"skipped: {skipped or ''}\n"
        f"skip_reason: {skip_reason or ''}"
    )


def build_misconfiguration(check: dict) -> Misconfiguration:
    """Build a Misconfiguration detail from a check.

    Args:
        check: One check dictionary from the misconfiguration_checks category.

    Returns:
        A Misconfiguration carrying the check's name and command.
    """
    return Misconfiguration(
        name=check.get("name"),
        command=check.get("command"),
    )

def build_authentication(check: dict) -> Authentication:
    """Build an Authentication detail from a check.

    Maps the check's confirmed flag onto the authenticated field. Skipped checks lack
    credential fields and should be filtered out before this is called.

    Args:
        check: One check dictionary from the authentication_testing category.

    Returns:
        An Authentication carrying the command, credentials, and authenticated flag.
    """
    return Authentication(
        command=check.get("command"),
        username=check.get("username"),
        password=check.get("password"),
        authenticated=check.get("confirmed"),
    )


def build_yaml_finding(check_type, evidence, host_ip, port_number, service_name) -> Finding:
    """Assemble one Finding from a detail object and the host level fields.

    Host status and port status are set to UP and OPEN because a service scan implies a
    live host with an open port. Operating system is None, since the service scan data
    does not report it.

    Args:
        check_type: The detail object (Authentication or Misconfiguration) for this finding.
        evidence: The raw evidence string for the check.
        host_ip: The scanned host's IP.
        port_number: The scanned port (coerced to int).
        service_name: The scanned service name.

    Returns:
        A Finding combining the host level fields and the given detail.
    """
    return Finding(
        host_ip=host_ip,
        host_status=HostStatus.UP,
        port_status=PortStatus.OPEN,
        port_number=int(port_number),
        service_name=service_name,
        operating_system=None,
        evidence=evidence,
        finding_type=check_type,
    )


def parse_yaml(file: Path) -> list[Finding]:
    """Parse a service scan YAML file into a flat list of Findings.

    Reads the host, port, and service from the top level, then walks every check in
    every scan category. Authentication tests become Authentication findings; all other
    categories become Misconfiguration findings. Skipped checks are dropped before any
    building. A check that fails validation is logged and skipped rather than crashing
    the whole parse, so one bad check never sinks the batch.

    Args:
        file: Path to the service scan YAML file.

    Returns:
        A list of Findings, one per non skipped check that built successfully.
    """
    findings = []
    errors = {}

    with file.open() as f:
        data = yaml.safe_load(f)

    host_ip = data["host"]
    port_number = data["port"]
    service_name = data["service"]

    for category in data["scans"]:
        for check in data["scans"][category]:
            if check.get("skipped"):
                continue

            try:
                if category == "misconfiguration_checks":
                    check_type = build_misconfiguration(check)
                elif category == "authentication_testing":
                    check_type = build_authentication(check)
                else:
                    continue

                evidence = build_evidence(check)
                finding = build_yaml_finding(
                    check_type, evidence, host_ip, port_number, service_name
                )
                findings.append(finding)
            except ValidationError as error:
                logging.warning("Failed to build finding for %s: %s", check.get("name"), error)
                errors[check.get("name")] = error

    return findings


 
                



