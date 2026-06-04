from pydantic import ValidationError

from scantriage.schema import Finding, HostStatus, PortStatus, Vulnerability


f1 = Finding(
        host_ip="192.168.45.208", 
        host_status=HostStatus.ALIVE, 
        port_status=PortStatus.OPEN,
        port_number=445,
        service_name="smb",
        finding_type=Vulnerability(name="ftp",evidence="testing evidence"))
print("Finding has printed fine")


try:
    f1 = Finding(
        host_ip="192.168.255.255", 
        host_status=HostStatus.ALIVE, 
        port_status=PortStatus.OPEN,
        port_number=23423423423434,
        service_name="smb",
        finding_type=Vulnerability(name="ftp",evidence="testing evidence"))
    print("Finding has printed fine")
except ValidationError as e:
    print(e)

