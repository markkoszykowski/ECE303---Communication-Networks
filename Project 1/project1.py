import sys
import socket
import argparse
from concurrent.futures import ThreadPoolExecutor


# usage: py project1.py hostname [-p m:n] [-h]


services = {
    20: "FTP Data Transfer",
    21: "FTP Command Control",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    119: "NNTP",
    123: "NTP",
    143: "IMAP",
    161: "SNMP",
    194: "IRC",
    443: "HTTPS"
}


def scanPort(args):
    (hostname, port) = args
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect_ex((hostname, port))
        if s == 0:
            if port in services.keys():
                print(F"Port {port} - {services.get(port)} - Open")
            else:
                print(F"Port {port} - Open")
            s.close()
    except socket.gaierror:
        sys.exit("Hostname could not be resolved")
    except socket.error:
        sys.exit("Server not responding")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("hostname", help="host IP to scan")
    parser.add_argument("-p", nargs='?', help="range of ports to scan, e.g. m:n", default="1:1024")
    ins = parser.parse_args()
    ports = None

    try:
        nums = ins.p.split(':')
        begin = int(nums[0])
        end = int(nums[1])
        if begin > end:
            sys.exit("Input range should be ascending, or equal to scan a single port")
        ports = range(begin, end + 1)
    except:
        sys.exit("Improper input format\nusage: py project1.py hostname [-p m:n] [-h]")

    params = ((ins.hostname, val) for val in ports)
    with ThreadPoolExecutor(max_workers=4) as executor:
        executor.map(scanPort, params)
