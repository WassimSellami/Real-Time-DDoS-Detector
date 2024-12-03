import subprocess


def block_ips(ips_to_block):
    for ip in ips_to_block:

        result_out = subprocess.run(
            [
                "netsh",
                "advfirewall",
                "firewall",
                "add",
                "rule",
                "name=BlockIP_OUT",
                "dir=out",
                "action=block",
                f"remoteip={ip}",
                "enable=yes",
            ],
            capture_output=True,
            text=True,
        )

        result_in = subprocess.run(
            [
                "netsh",
                "advfirewall",
                "firewall",
                "add",
                "rule",
                "name=BlockIP_IN",
                "dir=in",
                "action=block",
                f"remoteip={ip}",
                "enable=yes",
            ],
            capture_output=True,
            text=True,
        )
        if result_in.returncode == 0:
            print(f"Successfully blocked incoming traffic for IP: {ip}")
        else:
            print(
                f"Failed to block incoming traffic for IP: {ip}. Error: {result_in.stderr}"
            )

        print(f"Blocked IP: {ip} (incoming and outgoing traffic)")


def cleanup_rules():
    # Remove both incoming and outgoing rules
    subprocess.run(
        ["netsh", "advfirewall", "firewall", "delete", "rule", "name=BlockIP_OUT"]
    )
    subprocess.run(
        ["netsh", "advfirewall", "firewall", "delete", "rule", "name=BlockIP_IN"]
    )

    print("Unblocked IPs and cleaned up rules.")
