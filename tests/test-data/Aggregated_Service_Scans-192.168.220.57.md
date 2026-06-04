# Host Service Scan Results - 192.168.220.57

**Generated:** 2026-06-04T12:07:27.919950+00:00
**Total Services Scanned:** 7

---

## Host Services Overview

**All Services Detected:**

- [x] **WebRecon** - Scanned
- [x] **ftp-21_vsftpd_3.0.2** (vsftpd 3.0.2) - Scanned
- [x] **mysql-3306_MariaDB__unauthorized** (MariaDB (unauthorized)) - Scanned
- [x] **netbios-139_Samba_smbd_3.X_-_4.X__workgroup__SAMBA** (Samba smbd 3.X - 4.X (workgroup: SAMBA)) - Scanned
- [x] **rpc-111_2-4__RPC__100000** (2-4 (RPC #100000)) - Scanned
- [x] **smb-445_Samba_smbd_3.X_-_4.X__workgroup__SAMBA** (Samba smbd 3.X - 4.X (workgroup: SAMBA)) - Scanned
- [x] **ssh-22_OpenSSH_7.4__protocol_2.0** (OpenSSH 7.4 (protocol 2.0)) - Scanned

---

# ftp-21_vsftpd_3.0.2 — vsftpd 3.0.2

# ftp-21_vsftpd_3.0.2
**Version:** vsftpd 3.0.2
**Generated:** 2026-06-04T12:06:29.049715+00:00

---

# Information Gathering

## Nmap Version Detection
*Fingerprint FTP service version and run default scripts*
### Command
```bash
sudo nmap 192.168.220.57 -p 21 -sV -sC
```
### Output
```bash
Starting Nmap 7.94SVN ( https://nmap.org ) at 2026-06-04 07:05 CDT
Nmap scan report for 192.168.220.57
Host is up (0.050s latency).

PORT   STATE SERVICE VERSION
21/tcp open  ftp     vsftpd 3.0.2
| ftp-syst: 
|   STAT: 
| FTP server status:
|      Connected to ::ffff:192.168.45.208
|      Logged in as ftp
|      TYPE: ASCII
|      No session bandwidth limit
|      Session timeout in seconds is 300
|      Control connection is plain text
|      Data connections will be plain text
|      At session startup, client count was 4
|      vsFTPd 3.0.2 - secure, fast, stable
|_End of status
| ftp-anon: Anonymous FTP login allowed (FTP code 230)
|_Can't get directory listing: TIMEOUT
Service Info: OS: Unix

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 31.30 seconds
```
#### Hit
```bash
vsftpd 2.3.4 → backdoor (CVE-2011-2523): nc target 6200
ProFTPD 1.3.3c → mod_copy RCE (CVE-2015-3306)
Note FTP version for searchsploit
```

---

## Banner Grab
*Manual banner grab to read FTP welcome message*
### Command
```bash
timeout 10 nc -nv 192.168.220.57 21
```
### Output
```bash
220 (vsFTPd 3.0.2)
```
#### Hit
```bash
220 banner → version info, note for CVE check
331 Password required → auth needed
```

---

# Misconfiguration Checks

## Anonymous Login Check
*Automated check for anonymous FTP login and directory listing*
### Command
```bash
sudo nmap -sV --host-timeout 60s 192.168.220.57 -p 21 --script=ftp-anon
```
### Output
```bash
Starting Nmap 7.94SVN ( https://nmap.org ) at 2026-06-04 07:05 CDT
Nmap scan report for 192.168.220.57
Host is up (0.050s latency).

PORT   STATE SERVICE VERSION
21/tcp open  ftp     vsftpd 3.0.2
| ftp-anon: Anonymous FTP login allowed (FTP code 230)
|_Can't get directory listing: TIMEOUT
Service Info: OS: Unix

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 30.67 seconds
```
#### Hit
```bash
230 Login successful → anonymous read access confirmed
530 Login failed → anonymous disabled
```

---

## FTP System Type
*Detect OS and FTP daemon via SYST command*
### Command
```bash
sudo nmap -sV --host-timeout 60s 192.168.220.57 -p 21 --script=ftp-syst
```
### Output
```bash
Starting Nmap 7.94SVN ( https://nmap.org ) at 2026-06-04 07:06 CDT
Nmap scan report for 192.168.220.57
Host is up (0.048s latency).

PORT   STATE SERVICE VERSION
21/tcp open  ftp     vsftpd 3.0.2
| ftp-syst: 
|   STAT: 
| FTP server status:
|      Connected to ::ffff:192.168.45.208
|      Logged in as ftp
|      TYPE: ASCII
|      No session bandwidth limit
|      Session timeout in seconds is 300
|      Control connection is plain text
|      Data connections will be plain text
|      At session startup, client count was 1
|      vsFTPd 3.0.2 - secure, fast, stable
|_End of status
Service Info: OS: Unix

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 0.80 seconds
```
#### Hit
```bash
UNIX / Windows → OS confirmation
Affects path separators and privilege escalation paths
```

---

# Authentication Testing

## Anonymous FTP Login
*lftp anonymous login — exit code 0 confirms auth success, non-zero means failed*
### Command
```bash
lftp -u anonymous,anonymous -e "quit" ftp://192.168.220.57:21
```
### Output
#### ✅ CONFIRMED — anonymous:anonymous
*Exit code: 0 — credential valid*
```bash
exit 0 → anonymous login confirmed
non-zero → anonymous disabled
```

---

# Vulnerability Scanning

## vsftpd Backdoor Check
*Test for vsftpd 2.3.4 backdoor (CVE-2011-2523) — shell on port 6200*
### Command
```bash
sudo nmap -sV --host-timeout 60s 192.168.220.57 -p 21 --script=ftp-vsftpd-backdoor
```
### Output
```bash
Starting Nmap 7.94SVN ( https://nmap.org ) at 2026-06-04 07:06 CDT
Nmap scan report for 192.168.220.57
Host is up (0.048s latency).

PORT   STATE SERVICE VERSION
21/tcp open  ftp     vsftpd 3.0.2
Service Info: OS: Unix

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 0.41 seconds
```
#### Hit
```bash
VULNERABLE → backdoor on port 6200: nc target 6200
Trigger: open FTP connection with user ending in :)
```

---

## ProFTPD Backdoor Check
*Test for ProFTPD pre-auth backdoor (CVE-2010-4221)*
### Command
```bash
sudo nmap -sV --host-timeout 60s 192.168.220.57 -p 21 --script=ftp-proftpd-backdoor
```
### Output
```bash
Starting Nmap 7.94SVN ( https://nmap.org ) at 2026-06-04 07:06 CDT
Nmap scan report for 192.168.220.57
Host is up (0.049s latency).

PORT   STATE SERVICE VERSION
21/tcp open  ftp     vsftpd 3.0.2
Service Info: OS: Unix

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 0.37 seconds
```
#### Hit
```bash
VULNERABLE → mod_copy: CPFR /etc/passwd CPTO /var/www/html/passwd.txt
No auth required to copy arbitrary files
```

---

## FTP Vulnerability Scripts
*Run all ftp-vuln nmap NSE scripts against the service*
### Command
```bash
sudo nmap -sV --host-timeout 60s 192.168.220.57 -p 21 --script="ftp-vuln-*"
```
### Output
```bash
Starting Nmap 7.94SVN ( https://nmap.org ) at 2026-06-04 07:06 CDT
Nmap scan report for 192.168.220.57
Host is up (0.049s latency).

PORT   STATE SERVICE VERSION
21/tcp open  ftp     vsftpd 3.0.2
Service Info: OS: Unix

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 0.39 seconds
```

---



---

# mysql-3306_MariaDB__unauthorized — MariaDB (unauthorized)

# mysql-3306_MariaDB__unauthorized
**Version:** MariaDB (unauthorized)
**Generated:** 2026-06-04T12:05:26.802146+00:00

---

# Information Gathering

## Nmap MySQL Scripts
*Fingerprint MySQL version and basic info*
### Command
```bash
sudo nmap --host-timeout 60s 192.168.220.57 -p 3306 -sV --script=mysql-info
```
### Output
```bash
Starting Nmap 7.94SVN ( https://nmap.org ) at 2026-06-04 07:05 CDT
Nmap scan report for 192.168.220.57
Host is up (0.048s latency).

PORT     STATE SERVICE VERSION
3306/tcp open  mysql   MariaDB (unauthorized)

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 0.42 seconds
```
#### Hit
```bash
Version → check for CVEs: searchsploit mysql VERSION
mysql_native_password → password auth
```

---

## Banner Grab
*Read MySQL greeting banner*
### Command
```bash
timeout 10 nc -nv 192.168.220.57 3306
```
### Output

---

# Misconfiguration Checks

## Empty Password Check
*Check for accounts with no password set*
### Command
```bash
sudo nmap --host-timeout 60s 192.168.220.57 -p 3306 -sV --script=mysql-empty-password
```
### Output
```bash
Starting Nmap 7.94SVN ( https://nmap.org ) at 2026-06-04 07:05 CDT
Nmap scan report for 192.168.220.57
Host is up (0.050s latency).

PORT     STATE SERVICE VERSION
3306/tcp open  mysql   MariaDB (unauthorized)
|_mysql-empty-password: Host '192.168.45.208' is not allowed to connect to this MariaDB server

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 0.52 seconds
```
#### Hit
```bash
Login success → root with no password → full DB access
Read files: SELECT LOAD_FILE('/etc/passwd');
Write files: SELECT 'shell' INTO OUTFILE '/var/www/html/shell.php';
```

---

## MySQL Enumeration Scripts
*Enumerate variables and databases without credentials*
### Command
```bash
sudo nmap --host-timeout 60s 192.168.220.57 -p 3306 -sV --script=mysql-variables,mysql-databases
```
### Output
```bash
Starting Nmap 7.94SVN ( https://nmap.org ) at 2026-06-04 07:05 CDT
Nmap scan report for 192.168.220.57
Host is up (0.050s latency).

PORT     STATE SERVICE VERSION
3306/tcp open  mysql   MariaDB (unauthorized)

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 0.41 seconds
```
#### Hit
```bash
Databases listed → identify sensitive DBs
Variables → datadir, plugin_dir, secure_file_priv ('' = write anywhere)
```

---

# Authentication Testing

## MySQL root empty password
*Test root login with no password — exit 0 confirms access*
### Command
```bash
mysql -h 192.168.220.57 -P 3306 -u root --connect-timeout=10 -e "quit" 2>/dev/null
```
### Output
#### ✗ FAILED — root:
*Exit code: 1*

---

## MySQL root password root
*Test root login with password root — exit 0 confirms access*
### Command
```bash
mysql -h 192.168.220.57 -P 3306 -u root -proot --connect-timeout=10 -e "quit" 2>/dev/null
```
### Output
#### ✗ FAILED — root:root
*Exit code: 1*

---

## MySQL root password mysql
*Test root login with password mysql — exit 0 confirms access*
### Command
```bash
mysql -h 192.168.220.57 -P 3306 -u root -pmysql --connect-timeout=10 -e "quit" 2>/dev/null
```
### Output
#### ✗ FAILED — root:mysql
*Exit code: 1*

---

## MySQL root password admin
*Test root login with password admin — exit 0 confirms access*
### Command
```bash
mysql -h 192.168.220.57 -P 3306 -u root -padmin --connect-timeout=10 -e "quit" 2>/dev/null
```
### Output
#### ✗ FAILED — root:admin
*Exit code: 1*

---



---

# netbios-139_Samba_smbd_3.X_-_4.X__workgroup__SAMBA — Samba smbd 3.X - 4.X (workgroup: SAMBA)

# netbios-139_Samba_smbd_3.X_-_4.X__workgroup__SAMBA
**Version:** Samba smbd 3.X - 4.X (workgroup: SAMBA)
**Generated:** 2026-06-04T12:07:27.919020+00:00

---

# Information Gathering

## Nmap Version Detection
*Fingerprint NetBIOS service and enumerate names*
### Command
```bash
sudo nmap -sV -p 139,445 --script=nbstat,smb-os-discovery --host-timeout 60s 192.168.220.57
```
### Output
```bash
Starting Nmap 7.94SVN ( https://nmap.org ) at 2026-06-04 07:05 CDT
Nmap scan report for 192.168.220.57
Host is up (0.050s latency).

PORT    STATE SERVICE     VERSION
139/tcp open  netbios-ssn Samba smbd 3.X - 4.X (workgroup: SAMBA)
445/tcp open  netbios-ssn Samba smbd 4.10.4 (workgroup: SAMBA)
Service Info: Host: QUACKERJACK

Host script results:
| smb-os-discovery: 
|   OS: Windows 6.1 (Samba 4.10.4)
|   Computer name: quackerjack
|   NetBIOS computer name: QUACKERJACK\x00
|   Domain name: \x00
|   FQDN: quackerjack
|_  System time: 2026-06-04T08:05:27-04:00

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 15.69 seconds
```
#### Hit
```bash
Hostname, domain, MAC address disclosed
Workgroup/domain membership visible
```

---

## NBTScan Name Query
*Get NetBIOS names, workgroup, and MAC address*
### Command
```bash
nbtscan 192.168.220.57
```
### Output
```bash
Doing NBT name scan for addresses from 192.168.220.57

IP address       NetBIOS Name     Server    User             MAC address      
------------------------------------------------------------------------------
```

---

## Enum4linux
*Comprehensive NetBIOS/SMB enumeration — users, shares, groups*
### Command
```bash
enum4linux-ng -A 192.168.220.57
```
### Output
```bash
ENUM4LINUX - next generation (v1.3.10)

 ==========================
|    Target Information    |
 ==========================
[*] Target ........... 192.168.220.57
[*] Username ......... ''
[*] Random Username .. 'oalysofa'
[*] Password ......... ''
[*] Timeout .......... 10 second(s)

 =======================================
|    Listener Scan on 192.168.220.57    |
 =======================================
[*] Checking LDAP
[-] Could not connect to LDAP on 389/tcp: timed out
[*] Checking LDAPS
[-] Could not connect to LDAPS on 636/tcp: timed out
[*] Checking SMB
[+] SMB is accessible on 445/tcp
[*] Checking SMB over NetBIOS
[+] SMB over NetBIOS is accessible on 139/tcp
```
#### Hit
```bash
Users enumerated → target list for password spray
Shares accessible → browse for credentials, configs
Password policy → lockout threshold for spray
```

---

# Misconfiguration Checks

## RPC Null Session Enum Users
*Test for anonymous NetBIOS/SMB access*
### Command
```bash
rpcclient -U "" -N 192.168.220.57 -c "enumdomusers"
```
### Output
#### Hit
```bash
Users returned → null session enum works
Usernames for password spray or AS-REP roasting
```

---

## SMB Null Session List Shares
*Test for anonymous NetBIOS/SMB access*
### Command
```bash
smbclient -L //192.168.220.57 -N
```
### Output
```bash
Anonymous login successful

	Sharename       Type      Comment
	---------       ----      -------
	print$          Disk      Printer Drivers
	IPC$            IPC       IPC Service (Samba 4.10.4)
SMB1 disabled -- no workgroup available
```
#### Hit
```bash
Shares listed → browse without credentials
NETLOGON, SYSVOL → GPP passwords, login scripts
```

---

## SMB Null Session
*Test for anonymous NetBIOS/SMB access*
### Command
```bash
nxc smb 192.168.220.57 -u "" -p ""
```
### Output
```bash
SMB                      192.168.220.57  445    QUACKERJACK      [*] Unix - Samba (name:QUACKERJACK) (domain:) (signing:False) (SMBv1:True) (Null Auth:True)
SMB                      192.168.220.57  445    QUACKERJACK      [+] \:
```
#### Hit
```bash
Shares listed → browse without credentials
NETLOGON, SYSVOL → GPP passwords, login scripts
```

---

## SMB Guest List Shares
*Test if guest account is enabled*
### Command
```bash
smbclient -L //192.168.220.57 -U "guest%"
```
### Output
```bash
session setup failed: NT_STATUS_LOGON_FAILURE
```
#### Hit
```bash
Guest access → low-priv share browsing
Search for: passwords.txt, config files, backup files
```

---

## SMB Guest Session
*Test if guest account is enabled*
### Command
```bash
nxc smb 192.168.220.57 -u guest -p ""
```
### Output
```bash
SMB                      192.168.220.57  445    QUACKERJACK      [*] Unix - Samba (name:QUACKERJACK) (domain:) (signing:False) (SMBv1:True) (Null Auth:True)
SMB                      192.168.220.57  445    QUACKERJACK      [-] \guest: STATUS_LOGON_FAILURE
```
#### Hit
```bash
Guest access → low-priv share browsing
Search for: passwords.txt, config files, backup files
```

---

# Authentication Testing

## SMB Null Session List Shares
*NetBIOS authentication via SMB null and guest sessions*
### Command
```bash
smbclient -L //192.168.220.57 -N
```
### Output
```bash
Anonymous login successful

	Sharename       Type      Comment
	---------       ----      -------
	print$          Disk      Printer Drivers
	IPC$            IPC       IPC Service (Samba 4.10.4)
SMB1 disabled -- no workgroup available
```
#### Hit
```bash
Shares listed → browse without credentials
NETLOGON, SYSVOL → GPP passwords, login scripts
```

---

## SMB Null Session
*NetBIOS authentication via SMB null and guest sessions*
### Command
```bash
nxc smb 192.168.220.57 -u "" -p ""
```
### Output
```bash
SMB                      192.168.220.57  445    QUACKERJACK      [*] Unix - Samba (name:QUACKERJACK) (domain:) (signing:False) (SMBv1:True) (Null Auth:True)
SMB                      192.168.220.57  445    QUACKERJACK      [+] \:
```
#### Hit
```bash
Shares listed → browse without credentials
NETLOGON, SYSVOL → GPP passwords, login scripts
```

---

## SMB Anonymous Session
*NetBIOS authentication via SMB null and guest sessions*
### Command
```bash
nxc smb 192.168.220.57 -u "a" -p ""
```
### Output
```bash
SMB                      192.168.220.57  445    QUACKERJACK      [*] Unix - Samba (name:QUACKERJACK) (domain:) (signing:False) (SMBv1:True) (Null Auth:True)
SMB                      192.168.220.57  445    QUACKERJACK      [-] \a: STATUS_LOGON_FAILURE
```

---

# Vulnerability Scanning

## Nmap NetBIOS Scripts 1
*Run NetBIOS and SMB vulnerability enumeration*
### Command
```bash
sudo nmap -sU -p 139 --script=nbstat --max-retries 1 --host-timeout 30s 192.168.220.57
```
### Output
```bash
Starting Nmap 7.94SVN ( https://nmap.org ) at 2026-06-04 07:06 CDT
Nmap scan report for 192.168.220.57
Host is up (0.048s latency).

PORT    STATE         SERVICE
139/udp open|filtered netbios-ssn

Nmap done: 1 IP address (1 host up) scanned in 0.68 seconds
```

---

## Nmap NetBIOS Scripts 2
*Run NetBIOS and SMB vulnerability enumeration*
### Command
```bash
sudo nmap -sV -p 139,445 --script=smb-vuln* --host-timeout 60s 192.168.220.57
```
### Output
```bash
Starting Nmap 7.94SVN ( https://nmap.org ) at 2026-06-04 07:06 CDT
Nmap scan report for 192.168.220.57
Host is up (0.048s latency).

PORT    STATE SERVICE     VERSION
139/tcp open  netbios-ssn Samba smbd 3.X - 4.X (workgroup: SAMBA)
445/tcp open  netbios-ssn Samba smbd 3.X - 4.X (workgroup: SAMBA)
Service Info: Host: QUACKERJACK

Host script results:
|_smb-vuln-ms10-061: false
| smb-vuln-regsvc-dos: 
|   VULNERABLE:
|   Service regsvc in Microsoft Windows systems vulnerable to denial of service
|     State: VULNERABLE
|       The service regsvc in Microsoft Windows 2000 systems is vulnerable to denial of service caused by a null deference
|       pointer. This script will crash the service if it is vulnerable. This vulnerability was discovered by Ron Bowes
|       while working on smb-enum-sessions.
|_          
|_smb-vuln-ms10-054: false

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 47.29 seconds
```

---



---

# rpc-111_2-4__RPC__100000 — 2-4 (RPC #100000)

# rpc-111_2-4__RPC__100000
**Version:** 2-4 (RPC #100000)
**Generated:** 2026-06-04T12:06:42.148378+00:00

---

# Information Gathering

## Nmap Version Detection
*Fingerprint rpcbind and confirm the portmapper is responding*
### Command
```bash
sudo nmap -sV -p 111 192.168.220.57
```
### Output
```bash
Starting Nmap 7.94SVN ( https://nmap.org ) at 2026-06-04 07:05 CDT
Nmap scan report for 192.168.220.57
Host is up (0.048s latency).

PORT    STATE SERVICE VERSION
111/tcp open  rpcbind 2-4 (RPC #100000)

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 6.61 seconds
```
#### Hit
```bash
rpcbind 2-4 → portmapper responding, enumerate programs next
Note version for searchsploit
```

---

## RPC Program Dump (rpcinfo -p)
*List every registered RPC program, version, protocol and port*
### Command
```bash
rpcinfo -p 192.168.220.57
```
### Output
```bash
program vers proto   port  service
    100000    4   tcp    111  portmapper
    100000    3   tcp    111  portmapper
    100000    2   tcp    111  portmapper
    100000    4   udp    111  portmapper
    100000    3   udp    111  portmapper
    100000    2   udp    111  portmapper
```
#### Hit
```bash
nfs / mountd listed → NFS exported, pivot to NFS.toml
nlockmgr / status → NFS lock manager present
ypserv / yppasswdd → NIS in use, enumerate maps
rusersd / rstatd / rwalld → info-disclosure daemons
```
#### Miss
```bash
No programs listed → portmapper filtered or empty
```

---

## Nmap rpcinfo Script
*Scripted RPC program dump (works when rpcinfo binary is unavailable)*
### Command
```bash
sudo nmap -sV -p 111 --script=rpcinfo 192.168.220.57
```
### Output
```bash
Starting Nmap 7.94SVN ( https://nmap.org ) at 2026-06-04 07:05 CDT
Nmap scan report for 192.168.220.57
Host is up (0.048s latency).

PORT    STATE SERVICE VERSION
111/tcp open  rpcbind 2-4 (RPC #100000)
| rpcinfo: 
|   program version    port/proto  service
|   100000  2,3,4        111/tcp   rpcbind
|   100000  2,3,4        111/udp   rpcbind
|   100000  3,4          111/tcp6  rpcbind
|_  100000  3,4          111/udp6  rpcbind

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 6.61 seconds
```
#### Hit
```bash
100003 nfs → NFS present
100005 mountd → exports available via showmount
```

---

# Misconfiguration Checks

## NFS Exports via Portmapper
*If mountd is registered, list NFS exports advertised through the portmapper*
### Command
```bash
showmount -e 192.168.220.57
```
### Output
```bash
clnt_create: RPC: Timed out
```
#### Hit
```bash
Exports listed → mountable shares, continue in NFS.toml
Export allows '*' or no host restriction → world-accessible
```
#### Miss
```bash
clnt_create RPC error → mountd not exposed or filtered
```

---

## Full RPC Service Inventory
*Enumerate all RPC endpoints (newer rpcinfo lists netid/address/service)*
### Command
```bash
rpcinfo 192.168.220.57
```
### Output
```bash
program version netid     address                service    owner
    100000    4    tcp6      ::.0.111               portmapper superuser
    100000    3    tcp6      ::.0.111               portmapper superuser
    100000    4    udp6      ::.0.111               portmapper superuser
    100000    3    udp6      ::.0.111               portmapper superuser
    100000    4    tcp       0.0.0.0.0.111          portmapper superuser
    100000    3    tcp       0.0.0.0.0.111          portmapper superuser
    100000    2    tcp       0.0.0.0.0.111          portmapper superuser
    100000    4    udp       0.0.0.0.0.111          portmapper superuser
    100000    3    udp       0.0.0.0.0.111          portmapper superuser
    100000    2    udp       0.0.0.0.0.111          portmapper superuser
    100000    4    local     /var/run/rpcbind.sock  portmapper superuser
    100000    3    local     /var/run/rpcbind.sock  portmapper superuser
```
#### Hit
```bash
Unexpected daemons exposed → review each for known CVEs
Same program on tcp and udp → both transports reachable
```

---

# Authentication Testing

## Anonymous Portmapper Query
*The portmapper answers without authentication — successful dump confirms anonymous RPC enumeration is possible*
### Command
```bash
rpcinfo -p 192.168.220.57
```
### Output
```bash
program vers proto   port  service
    100000    4   tcp    111  portmapper
    100000    3   tcp    111  portmapper
    100000    2   tcp    111  portmapper
    100000    4   udp    111  portmapper
    100000    3   udp    111  portmapper
    100000    2   udp    111  portmapper
```
#### Hit
```bash
Program list returned → anonymous query allowed (expected)
```
#### Miss
```bash
Connection refused / timeout → port filtered
```

---

# Vulnerability Scanning

## RPC NSE Scripts
*Run RPC-related nmap NSE scripts against the portmapper*
### Command
```bash
sudo nmap -sV -p 111 --script "rpc-*" --host-timeout 60s 192.168.220.57
```
### Output
```bash
Starting Nmap 7.94SVN ( https://nmap.org ) at 2026-06-04 07:06 CDT
Nmap scan report for 192.168.220.57
Host is up (0.048s latency).

PORT    STATE SERVICE VERSION
111/tcp open  rpcbind 2-4 (RPC #100000)
| rpcinfo: 
|   program version    port/proto  service
|   100000  2,3,4        111/tcp   rpcbind
|   100000  2,3,4        111/udp   rpcbind
|   100000  3,4          111/tcp6  rpcbind
|_  100000  3,4          111/udp6  rpcbind

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 6.61 seconds
```
#### Hit
```bash
Script flags a daemon version → check searchsploit for that daemon
```

---

## Searchsploit RPC Daemons
*Re-read daemon versions from rpcinfo output, then run searchsploit on any exposed daemon (e.g. rpc.statd, ypserv) and its version*
### Command
```bash
sudo nmap -sV -p 111 --script=rpcinfo 192.168.220.57
```
### Output
```bash
Starting Nmap 7.94SVN ( https://nmap.org ) at 2026-06-04 07:06 CDT
Nmap scan report for 192.168.220.57
Host is up (0.048s latency).

PORT    STATE SERVICE VERSION
111/tcp open  rpcbind 2-4 (RPC #100000)
| rpcinfo: 
|   program version    port/proto  service
|   100000  2,3,4        111/tcp   rpcbind
|   100000  2,3,4        111/udp   rpcbind
|   100000  3,4          111/tcp6  rpcbind
|_  100000  3,4          111/udp6  rpcbind

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 6.60 seconds
```
#### Hit
```bash
Old rpc.statd / ypserv → check searchsploit for the exact version
```

---



---

# smb-445_Samba_smbd_3.X_-_4.X__workgroup__SAMBA — Samba smbd 3.X - 4.X (workgroup: SAMBA)

# smb-445_Samba_smbd_3.X_-_4.X__workgroup__SAMBA
**Version:** Samba smbd 3.X - 4.X (workgroup: SAMBA)
**Generated:** 2026-06-04T12:07:02.204701+00:00

---

# Information Gathering

## Nmap SMB Scripts
*Fingerprint OS, SMB protocol version, and security mode*
### Command
```bash
sudo nmap --host-timeout 60s 192.168.220.57 -p 445 -sV -Pn --script "smb-os-discovery,smb-protocols,smb-security-mode"
```
### Output
```bash
Starting Nmap 7.94SVN ( https://nmap.org ) at 2026-06-04 07:05 CDT
Nmap scan report for 192.168.220.57
Host is up (0.050s latency).

PORT    STATE SERVICE     VERSION
445/tcp open  netbios-ssn Samba smbd 4.10.4 (workgroup: SAMBA)
Service Info: Host: QUACKERJACK

Host script results:
| smb-security-mode: 
|   account_used: guest
|   authentication_level: user
|   challenge_response: supported
|_  message_signing: disabled (dangerous, but default)
| smb-os-discovery: 
|   OS: Windows 6.1 (Samba 4.10.4)
|   Computer name: quackerjack
|   NetBIOS computer name: QUACKERJACK\x00
|   Domain name: \x00
|   FQDN: quackerjack
|_  System time: 2026-06-04T08:05:24-04:00
| smb-protocols: 
|   dialects: 
|     NT LM 0.12 (SMBv1) [dangerous, but default]
|     2:0:2
|     2:1:0
|     3:0:0
|     3:0:2
|_    3:1:1

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 16.31 seconds
```
#### Hit
```bash
signing: false → NTLM relay attack possible (ntlmrelayx)
SMBv1 enabled → EternalBlue (MS17-010) attack surface
OS version → check for EternalBlue, PrintNightmare
```

---

## SMB Share and User Enumeration
*Enumerate shares, users, and processes via SMB scripts*
### Command
```bash
sudo nmap --host-timeout 60s 192.168.220.57 -p 445 -sV -Pn --script "smb-enum-shares,smb-enum-users,smb-enum-processes"
```
### Output
```bash
Starting Nmap 7.94SVN ( https://nmap.org ) at 2026-06-04 07:05 CDT
Nmap scan report for 192.168.220.57
Host is up (0.048s latency).

PORT    STATE SERVICE     VERSION
445/tcp open  netbios-ssn Samba smbd 3.X - 4.X (workgroup: SAMBA)
Service Info: Host: QUACKERJACK

Host script results:
| smb-enum-shares: 
|   account_used: <blank>
|   \\192.168.220.57\IPC$: 
|     Type: STYPE_IPC_HIDDEN
|     Comment: IPC Service (Samba 4.10.4)
|     Users: 1
|     Max Users: <unlimited>
|     Path: C:\tmp
|     Anonymous access: READ/WRITE
|   \\192.168.220.57\print$: 
|     Type: STYPE_DISKTREE
|     Comment: Printer Drivers
|     Users: 0
|     Max Users: <unlimited>
|     Path: C:\var\lib\samba\drivers
|_    Anonymous access: <none>

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 27.73 seconds
```
#### Hit
```bash
ADMIN$, C$ accessible → admin-level share access
READ access → credential files, configs, scripts
WRITE access → drop files, potential code execution
```

---

# Misconfiguration Checks

## SMB Null Session
*Check for anonymous/null session access to SMB*
### Command
```bash
nxc smb 192.168.220.57 -u "" -p ""
```
### Output
```bash
SMB                      192.168.220.57  445    QUACKERJACK      [*] Unix - Samba (name:QUACKERJACK) (domain:) (signing:False) (SMBv1:True) (Null Auth:True)
SMB                      192.168.220.57  445    QUACKERJACK      [+] \:
```
#### ✅ CONFIRMED — 
*Exit code: 0 — credential valid*
```bash
[+] → null session works → user/share enumeration
```

---

## SMB Null Session List Shares
*Check for anonymous/null session access to SMB*
### Command
```bash
smbclient -L //192.168.220.57 -N
```
### Output
```bash
Anonymous login successful

	Sharename       Type      Comment
	---------       ----      -------
	print$          Disk      Printer Drivers
	IPC$            IPC       IPC Service (Samba 4.10.4)
SMB1 disabled -- no workgroup available
```
#### Hit
```bash
ADMIN$, C$ accessible → admin-level share access
READ access → credential files, configs, scripts
WRITE access → drop files, potential code execution
```

---

## SMB Anonymous Session
*Check if guest account allows share listing*
### Command
```bash
nxc smb 192.168.220.57 -u "a" -p ""
```
### Output
```bash
SMB                      192.168.220.57  445    QUACKERJACK      [*] Unix - Samba (name:QUACKERJACK) (domain:) (signing:False) (SMBv1:True) (Null Auth:True)
SMB                      192.168.220.57  445    QUACKERJACK      [-] \a: STATUS_LOGON_FAILURE
```

---

## SMB Guest List Shares
*Check if guest account allows share listing*
### Command
```bash
smbclient -L //192.168.220.57 -U "guest%"
```
### Output
```bash
session setup failed: NT_STATUS_LOGON_FAILURE
```
#### Hit
```bash
ADMIN$, C$ accessible → admin-level share access
READ access → credential files, configs, scripts
WRITE access → drop files, potential code execution
```

---

# Authentication Testing

## SMB Null Session
*Confirm null session access — exit 0 confirms anonymous login*
### Command
```bash
smbclient -L //192.168.220.57 -N -p 445
```
### Output
```bash
Anonymous login successful

	Sharename       Type      Comment
	---------       ----      -------
	print$          Disk      Printer Drivers
	IPC$            IPC       IPC Service (Samba 4.10.4)
SMB1 disabled -- no workgroup available
```
#### ✅ CONFIRMED — 
*Exit code: 0 — credential valid*
```bash
[+] → null session works → user/share enumeration
```

---

## SMB Guest Session
*Confirm guest session access — exit 0 confirms guest login*
### Command
```bash
smbclient -L //192.168.220.57 -U "guest%" -p 445
```
### Output
```bash
session setup failed: NT_STATUS_LOGON_FAILURE
```
#### ✗ FAILED — guest:
*Exit code: 1*

---

# Vulnerability Scanning

## EternalBlue Check
*Check for MS17-010 EternalBlue — unauthenticated RCE*
### Command
```bash
sudo nmap --host-timeout 60s 192.168.220.57 -p 445 -sV -Pn --script "smb-vuln-ms17-010"
```
### Output
```bash
Starting Nmap 7.94SVN ( https://nmap.org ) at 2026-06-04 07:06 CDT
Nmap scan report for 192.168.220.57
Host is up (0.049s latency).

PORT    STATE SERVICE     VERSION
445/tcp open  netbios-ssn Samba smbd 3.X - 4.X (workgroup: SAMBA)
Service Info: Host: QUACKERJACK

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 7.74 seconds
```
#### Hit
```bash
VULNERABLE → MS17-010 EternalBlue → SYSTEM RCE no creds
Exploit: use exploit/windows/smb/ms17_010_eternalblue
```

---

## SMB Vulnerability Scripts
*Run all SMB vulnerability detection scripts*
### Command
```bash
sudo nmap --host-timeout 60s 192.168.220.57 -p 445 -sV -Pn --script "smb-vuln*"
```
### Output
```bash
Starting Nmap 7.94SVN ( https://nmap.org ) at 2026-06-04 07:06 CDT
Nmap scan report for 192.168.220.57
Host is up (0.050s latency).

PORT    STATE SERVICE     VERSION
445/tcp open  netbios-ssn Samba smbd 3.X - 4.X (workgroup: SAMBA)
Service Info: Host: QUACKERJACK

Host script results:
|_smb-vuln-ms10-061: false
| smb-vuln-regsvc-dos: 
|   VULNERABLE:
|   Service regsvc in Microsoft Windows systems vulnerable to denial of service
|     State: VULNERABLE
|       The service regsvc in Microsoft Windows 2000 systems is vulnerable to denial of service caused by a null deference
|       pointer. This script will crash the service if it is vulnerable. This vulnerability was discovered by Ron Bowes
|       while working on smb-enum-sessions.
|_          
|_smb-vuln-ms10-054: false

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 41.13 seconds
```
#### Hit
```bash
VULNERABLE output → prioritise that CVE
MS17-010 → EternalBlue, MS08-067 → NetAPI
```

---



---

# ssh-22_OpenSSH_7.4__protocol_2.0 — OpenSSH 7.4 (protocol 2.0)

# ssh-22_OpenSSH_7.4__protocol_2.0
**Version:** OpenSSH 7.4 (protocol 2.0)
**Generated:** 2026-06-04T12:05:42.179822+00:00

---

# Information Gathering

## Nmap Version Detection
*Fingerprint SSH server version and hostkey algorithms*
### Command
```bash
sudo nmap --host-timeout 60s 192.168.220.57 -p 22 -Pn -sV --script=ssh-hostkey
```
### Output
```bash
Starting Nmap 7.94SVN ( https://nmap.org ) at 2026-06-04 07:05 CDT
Nmap scan report for 192.168.220.57
Host is up (0.049s latency).

PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 7.4 (protocol 2.0)
| ssh-hostkey: 
|   2048 a2:ec:75:8d:86:9b:a3:0b:d3:b6:2f:64:04:f9:fd:25 (RSA)
|   256 b6:d2:fd:bb:08:9a:35:02:7b:33:e3:72:5d:dc:64:82 (ECDSA)
|_  256 08:95:d6:60:52:17:3d:03:e4:7d:90:fd:b2:ed:44:86 (ED25519)

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 1.85 seconds
```
#### Hit
```bash
OpenSSH < 7.7 → username enumeration (CVE-2018-15473)
OpenSSH < 8.3 → double-free (CVE-2023-38408 if agent forwarding)
Note version for searchsploit
```

---

## Auth Methods Check
*List accepted authentication methods — confirms if password auth is on*
### Command
```bash
sudo nmap -sV --host-timeout 60s 192.168.220.57 -p 22 -Pn --script=ssh-auth-methods --script-args="ssh.user=root"
```
### Output
```bash
Starting Nmap 7.94SVN ( https://nmap.org ) at 2026-06-04 07:05 CDT
Nmap scan report for 192.168.220.57
Host is up (0.050s latency).

PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 7.4 (protocol 2.0)
| ssh-auth-methods: 
|   Supported authentication methods: 
|     publickey
|     gssapi-keyex
|     gssapi-with-mic
|_    password

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 0.63 seconds
```
#### Hit
```bash
keyboard-interactive enabled → password bruteforce viable
password enabled → try default credentials
```
#### Miss
```bash
publickey only → need key, bruteforce not viable
```

---

# Misconfiguration Checks

## Password Auth Confirmation
*Confirm password authentication is accepted before brute forcing*
### Command
```bash
ssh -p 22 -o StrictHostKeyChecking=no -o PreferredAuthentications=none -o BatchMode=yes root@192.168.220.57 2>&1
```
### Output
```bash
Warning: Permanently added '192.168.220.57' (ED25519) to the list of known hosts.
root@192.168.220.57: Permission denied (publickey,gssapi-keyex,gssapi-with-mic,password).
```
#### Hit
```bash
password auth enabled → bruteforce / spray viable
```
#### Miss
```bash
PasswordAuthentication no → key auth only
```

---

## Username Enumeration
*Check for CVE-2018-15473 OpenSSH user enumeration*
### Command
```bash
sudo nmap -sV --host-timeout 60s 192.168.220.57 -p 22 --script=ssh-auth-methods
```
### Output
```bash
Starting Nmap 7.94SVN ( https://nmap.org ) at 2026-06-04 07:05 CDT
Nmap scan report for 192.168.220.57
Host is up (0.050s latency).

PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 7.4 (protocol 2.0)
| ssh-auth-methods: 
|   Supported authentication methods: 
|     publickey
|     gssapi-keyex
|     gssapi-with-mic
|_    password

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 0.75 seconds
```
#### Hit
```bash
valid user returns different timing/error → enumerate usernames
use: ssh-audit or custom script with CVE-2018-15473
```

---

# Authentication Testing

## Default Credentials root empty
*Test root login with empty password — exit 0 confirms access*
### Command
```bash
sshpass -p '' ssh -p 22 -o StrictHostKeyChecking=no -o ConnectTimeout=5 -o BatchMode=no root@192.168.220.57 id 2>/dev/null && echo "[+] root:empty worked"
```
### Output
#### ✗ FAILED — root:
*Exit code: 5*

---

## Default Credentials root root
*Test root login with password root — exit 0 confirms access*
### Command
```bash
sshpass -p 'root' ssh -p 22 -o StrictHostKeyChecking=no -o ConnectTimeout=5 -o BatchMode=no root@192.168.220.57 id 2>/dev/null && echo "[+] root:root worked"
```
### Output
#### ✗ FAILED — root:root
*Exit code: 5*

---

## Default Credentials root toor
*Test root login with password toor — exit 0 confirms access*
### Command
```bash
sshpass -p 'toor' ssh -p 22 -o StrictHostKeyChecking=no -o ConnectTimeout=5 -o BatchMode=no root@192.168.220.57 id 2>/dev/null && echo "[+] root:toor worked"
```
### Output
#### ✗ FAILED — root:toor
*Exit code: 5*

---

## Default Credentials admin admin
*Test admin login with password admin — exit 0 confirms access*
### Command
```bash
sshpass -p 'admin' ssh -p 22 -o StrictHostKeyChecking=no -o ConnectTimeout=5 -o BatchMode=no admin@192.168.220.57 id 2>/dev/null && echo "[+] admin:admin worked"
```
### Output
#### ✗ FAILED — admin:admin
*Exit code: 5*

---

## Default Credentials admin password
*Test admin login with password password — exit 0 confirms access*
### Command
```bash
sshpass -p 'password' ssh -p 22 -o StrictHostKeyChecking=no -o ConnectTimeout=5 -o BatchMode=no admin@192.168.220.57 id 2>/dev/null && echo "[+] admin:password worked"
```
### Output
#### ✗ FAILED — admin:password
*Exit code: 5*

---

## Default Credentials ubuntu ubuntu
*Common Ubuntu cloud image default*
### Command
```bash
sshpass -p 'ubuntu' ssh -p 22 -o StrictHostKeyChecking=no -o ConnectTimeout=5 root@192.168.220.57 id 2>/dev/null && echo "[+] ubuntu:ubuntu worked"
```
### Output
#### ✗ FAILED — ubuntu:ubuntu
*Exit code: 5*

---

## Default Credentials pi raspberry
*Raspberry Pi default credentials*
### Command
```bash
sshpass -p 'raspberry' ssh -p 22 -o StrictHostKeyChecking=no -o ConnectTimeout=5 pi@192.168.220.57 id 2>/dev/null && echo "[+] pi:raspberry worked"
```
### Output
#### ✗ FAILED — pi:raspberry
*Exit code: 5*

---

## Default Credentials user user
*Generic user account with matching password*
### Command
```bash
sshpass -p 'user' ssh -p 22 -o StrictHostKeyChecking=no -o ConnectTimeout=5 user@192.168.220.57 id 2>/dev/null && echo "[+] user:user worked"
```
### Output
#### ✗ FAILED — user:user
*Exit code: 5*

---

## Default Credentials vagrant vagrant
*Vagrant default — extremely common on lab and CTF boxes*
### Command
```bash
sshpass -p 'vagrant' ssh -p 22 -o StrictHostKeyChecking=no -o ConnectTimeout=5 -o BatchMode=no vagrant@192.168.220.57 id 2>/dev/null && echo "[+] vagrant:vagrant worked"
```
### Output
#### ✗ FAILED — vagrant:vagrant
*Exit code: 5*

---

## Default Credentials kali kali
*Kali default credentials — seen on misconfigured Kali instances*
### Command
```bash
sshpass -p 'kali' ssh -p 22 -o StrictHostKeyChecking=no -o ConnectTimeout=5 -o BatchMode=no kali@192.168.220.57 id 2>/dev/null && echo "[+] kali:kali worked"
```
### Output
#### ✗ FAILED — kali:kali
*Exit code: 5*

---



---

