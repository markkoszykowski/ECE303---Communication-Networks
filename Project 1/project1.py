import sys
import socket
import argparse


def portScan(hostname, ports):
    print(hostname)
    for port in ports:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        s.connect_ex((hostname, port))
        print(s == 0)
        print(port)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("hostname", help="host IP to scan")
    parser.add_argument("-p", nargs='?', help="range of ports to scan", default="1:1024")
    args = parser.parse_args()
    ports = None

    try:
        nums = args.p.split(':')
        begin = int(nums[0])
        end = int(nums[1])
        if begin > end:
            sys.exit("Input range should be ascending, or equal to scan a single port")
        ports = range(begin, end + 1)
    except:
        sys.exit("Improper input format\nusage: py project1.py hostname [-p m:n]")

    portScan(args.hostname, ports)
