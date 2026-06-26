from typing import Annotated, Literal
from pydantic import BaseModel, Field

from scantriage.enums import HostStatus, PortStatus, Severity 


class Authentication(BaseModel):
    """An authentication finding from a credential or session test.

    Produced from the structured authentication_testing entries in a service
    scan, where the result is already determined by a confirmed flag rather
    than by interpreting tool output.

    Attributes:
        kind: Type discriminator. Always "authentication".
        username: The username tried. May be empty for null or anonymous sessions.
        password: The password tried. May be empty for null or anonymous sessions.
        authenticated: Whether the credentials successfully authenticated.
    """

    kind: Literal["authentication"] = "authentication"
    username: str
    password: str
    authenticated: bool
    command: str


class Misconfiguration(BaseModel):
    """A misconfiguration finding captured from a scan command.

    The parser does not interpret the output; it captures the command and its
    raw evidence so a later triage step can judge severity. This keeps brittle,
    tool version dependent interpretation out of the deterministic parser.

    Attributes:
        kind: Type discriminator. Always "misconfiguration".
        name: Short label for the check that produced this finding.
        command: The exact command that was run to surface the finding.
        evidence: Raw output (e.g. stdout) used as evidence for the finding.
    """

    kind: Literal["misconfiguration"] = "misconfiguration"
    name: str
    command: str


class Vulnerability(BaseModel):
    """A vulnerability finding tied to a specific service and version.

    Typically produced from nmap service detection. Carries the identifiers
    needed for later CVE lookup. Product, version, evidence, and CPE are all
    optional because not every detected service exposes them.

    Attributes:
        kind: Type discriminator. Always "vulnerability".
        name: The product or service name (e.g. "vsftpd", "http").
        product: The detected product if available (e.g. "Apache httpd"). None
            when nmap identified a service but not its product.
        evidence: Raw evidence supporting the finding, if available.
        version: Detected version string if available (e.g. "3.0.2", "3.X - 4.X").
        common_platform_enumeration: CPE identifier if available, the standardized
            vendor/product/version key used for CVE lookup
            (e.g. "cpe:/a:vsftpd:vsftpd:3.0.2").
    """

    kind: Literal["vulnerability"] = "vulnerability"
    name: str
    product: str | None = None
    version: str | None = None
    common_platform_enumeration: str | None = None




class Finding(BaseModel):
    """A single security finding for one issue on one host and port.

    The grain is one discrete issue, not one host or one port, so each finding
    can carry a single type and be triaged independently. Host and port are
    fields, so per host or per port views are obtained by grouping findings.

    The head fields below apply to every finding regardless of type. The
    type specific fields live on finding_type, whose concrete class is selected
    by its "kind" discriminator.

    Attributes:
        host_ip: IP address of the host the finding belongs to.
        host_status: Reachability state of the host.
        port_status: State of the port the finding was observed on.
        port_number: Port number the finding was observed on. Must be 1 to 65535.
        service_name: Service category on the port (e.g. "ftp", "smb", "mysql").
        operating_system: The proposed operating system of the host.
        finding_type: The type specific detail, one of Authentication,
            Misconfiguration, or Vulnerability, discriminated by its "kind" field.
    """

    host_ip: str
    host_status: HostStatus 
    port_status: PortStatus 
    port_number: int = Field(ge=1, le=65535)
    service_name: str
    operating_system: str | None
    evidence: str | None
    finding_type: Annotated[
        Authentication | Misconfiguration | Vulnerability,
        Field(discriminator="kind"),
    ]


class TriageResult(BaseModel):
    """The model's triage assessment of a single finding."""
    severity: Severity          
    rationale: str        
    remediation: str
    
