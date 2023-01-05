#/usr/bin/env python3

import argparse
import subprocess

def execute_cmd(args: str) -> str:
    proc = subprocess.run(args, shell=True, text=True, stdout=subprocess.PIPE)
    proc.check_returncode()
    return proc.stdout

def get_opts() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="Bootstrap Arch",
        description="Helper program ton install an archlinux hardened distribution.",
    )

    parser.add_argument(
        "--hostname",
        default="arch",
        help="Set the hostname of the archlinux."
    )

    parser.add_argument(
        "--disks",
        nargs="+",
        help="Disks to use for the lvm partition.",
    )

    parser.add_argument(
        "--bootloader-installation-disk",
        help="On which disk install the bootloader, example /dev/sda.",
    )

    parser.add_argument(
        "--mirror-regions",
        nargs="*",
        help="Select the mirror regions used for Arch.",
    )

    parser.add_argument(
        "--sudouser",
        nargs="+",
        help="Add user with sudo permissions.",
    )

    parser.add_argument(
        "--copy-ssh-key",
        help="Copy the authorized ssh keys from /root/.ssh/authorized_keys in the home directory of the given user.",
    )

    parser.add_argument(
        "--network-manager",
        default="NetworkManager",
        help="Defaut network manager to use.",
    )

    parser.add_argument(
        "--network",
        default="dhcpd",
        help="configure an ipv4 address on a specified interface. Use this format: interface|XXX.XXX.XXX.XXX, default is dhcpd on the all intefaces.",
    )

    parser.add_argument(
        "--dns-server",
        help="Use a specific dns server."
    )
    args = parser.parse_args()
    print(args)
    return args

def main():
    get_opts()
    return
if __name__ == "__main__":
    main()
