from pathlib import Path 
from pprint import pprint
from scantriage.parsing import parse_yaml, parse_xml

if __name__ == "__main__":
    PROJECT_ROOT = Path(__file__).parent.parent
    FILE_XML = PROJECT_ROOT / "tests" / "test-data" / "H_192.168.220.57.xml"
    FILE_YAML = PROJECT_ROOT / "tests" / "test-data" / "scan_results.yaml"
    xml_findings = parse_xml(FILE_XML)
    yaml_findings = parse_yaml(FILE_YAML)

    print("=" * 50)
    print("XML FINDINGS")
    print("=" * 50)
    for finding in xml_findings:
        print(finding.model_dump_json(indent=2))
        print("-" * 40)

    print("=" * 50)
    print("YAML FINDINGS")
    print("=" * 50)
    for finding in yaml_findings:
        print(finding.model_dump_json(indent=2))
        print("-" * 40)

