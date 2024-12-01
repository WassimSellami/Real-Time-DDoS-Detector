import subprocess

# List of blocked IPs
# blocked_ips = ["142.251.37.14"]  # Add IPs you want to block here


def block_ips(ips_to_block):
    for ip in ips_to_block:
        # Block incoming traffic
        subprocess.run(
            [
                "netsh",
                "advfirewall",
                "firewall",
                "add",
                "rule",
                "name=BlockIP_OUT",
                "dir=in",
                "action=block",
                f"remoteip={ip}",
                "enable=yes",
            ]
        )
        subprocess.run(
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
            ]
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
