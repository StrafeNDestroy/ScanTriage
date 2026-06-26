from pathlib import Path 
from scantriage.parsing import parse_yaml, parse_xml
from scantriage.model import query_model
from scantriage.paths import PROJECT_ROOT, LOG_MAIN, LOG_ROOT
import logging


LOG_ROOT.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",  
    handlers=[logging.FileHandler(LOG_MAIN), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)



if __name__ == "__main__":
    PROJECT_ROOT = Path(__file__).parent.parent
    FILE_XML = PROJECT_ROOT / "tests" / "test-data" / "H_192.168.220.57.xml"
    FILE_YAML = PROJECT_ROOT / "tests" / "test-data" / "scan_results.yaml"
    xml_findings = parse_xml(FILE_XML)
    yaml_findings = parse_yaml(FILE_YAML)

    model_response_xml = query_model(xml_findings)
    model_response_yaml = query_model(yaml_findings)

    print("=" * 50)
    print("XML FINDINGS")
    print("=" * 50)
    for finding,response in model_response_xml:
        print(f"Host IP: {finding.host_ip}")
        print(f"Host Port: {finding.port_number}")
        print(f"Service Name: {finding.service_name}")
        print(f"Evidence: {finding.evidence}")
        print(f"CVSS: {response.severity}")
        print(f"Severity Rationale: {response.rationale}")
        print(f"Remediation: {response.remediation}")
        print("-" * 50 + "\n")

    print("=" * 50)
    print("YAML FINDINGS")
    print("=" * 50)
    for finding,response in model_response_yaml:
        print(f"Host IP: {finding.host_ip}")
        print(f"Host Port: {finding.port_number}")
        print(f"Service Name: {finding.service_name}")
        print(f"Evidence: {finding.evidence}")
        print(f"CVSS: {response.severity}")
        print(f"Severity Rationale: {response.rationale}")
        print(f"Remediation: {response.remediation}")
        print("-" * 50 + "\n")

