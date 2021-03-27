import sys
import socket
import argparse
from concurrent.futures import ThreadPoolExecutor


# usage: py project1.py hostname [-p m:n] [-h]


# https://www.netresec.com/?page=Blog&month=2011-11&post=Passive-OS-Fingerprinting
OS = {
    (64, 5840): "Linux (kernel 2.4 and 2.6)",
    (64, 5720): "Google's customized Linux",
    (64, 65535): "FreeBSD",
    (128, 65535): "Windows XP",
    (128, 8192): "Windows 7, Vista and Server 2008",
    (255, 4128): "Cisco Router (iOS 12.4)"
}


def scanPort(args):
    (hostname, port) = args
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        connect = s.connect_ex((hostname, port))
        if connect == 0:
            ttl = s.getsockopt(socket.IPPROTO_IP, socket.IP_TTL)
            # https://stackoverflow.com/questions/9615321/is-the-tcp-window-size-relevant-to-the-snd-buf-or-rcv-buf-of-the-tcp-socket
            winSize = s.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF)
            if OS.get((ttl, winSize)) is not None:
                print(F"Port {port} - {OS.get((ttl, winSize))}", end=" ")
            else:
                print(F"Port {port} - Unknown OS", end=" ")
            try:
                print(F"- {socket.getservbyport(port)} - Open")
            except:
                print(F"- Open")
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
