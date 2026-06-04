import xml.etree.ElementTree as ET

from scantriage.schema import Finding

import yaml

FILE_XML = "./../tests/test-data/H_192.168.220.57.xml"

tree = ET.parse(FILE_XML)
root = tree.getroot()


FINDINGS = []
HOST_IP  = root.find("address").get("addr")
HOST_STATUS = root.find("host").get("state")


for port in root.iter("port"):
    port_number = port.get("portid")
    port_protocol = port.get("protocol")
    port_status = port.find("state").get("state")


    port_service_tag= port.find("service")
    port_service_name = port_service_tag.get("name")
    port_service_product = port_service_tag.get("product")
    port_service_version = port_service_tag.get("version")
    port_common_protocol_enumeration_tag = port_service_tag.find("cpe")
    if port_common_protocol_enumeration_tag is not None: 
        port_common_protocol_text = port_common_protocol_enumeration_tag.text
    else:
        port_common_protocol_text = None
    finding = Finding(host_ip=HOST_IP,host_status=)
    
    

