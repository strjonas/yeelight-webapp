from yeelight import *
import sys

def notify(message):
    pass

def discover():
        ips = []
        print("HEll0")
        avb = discover_bulbs(timeout=3)
        print("HEllo again")
        if len(avb) == 0:
            print("No devices found!")
            notify("No devices Found!")
        for av in avb:
            ip = av.get("ip")
            if ip not in ips:
                ips.append(ip)
        return ips
        