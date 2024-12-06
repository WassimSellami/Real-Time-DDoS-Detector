import subprocess


def block_ips(ips_to_block):
    for ip in ips_to_block:
        # Block outgoing traffic
        result_out = subprocess.run(
            [
                "sudo",
                "iptables",
                "-A",  # Append a rule
                "OUTPUT",
                "-d", ip,  # Destination IP
                "-j", "DROP",  # Drop packets
            ],
            capture_output=True,
            text=True,
        )

        # Block incoming traffic
        result_in = subprocess.run(
            [
                "sudo",
                "iptables",
                "-A",  # Append a rule
                "INPUT",
                "-s", ip,  # Source IP
                "-j", "DROP",  # Drop packets
            ],
            capture_output=True,
            text=True,
        )

        if result_in.returncode == 0:
            print(f"Successfully blocked incoming traffic for IP: {ip}")
        else:
            print(f"Failed to block incoming traffic for IP: {ip}. Error: {result_in.stderr}")

        if result_out.returncode == 0:
            print(f"Successfully blocked outgoing traffic for IP: {ip}")
        else:
            print(f"Failed to block outgoing traffic for IP: {ip}. Error: {result_out.stderr}")


def cleanup_rules():
    # Remove all rules created for blocking incoming and outgoing traffic
    subprocess.run(["sudo", "iptables", "-F"], check=True)  # Flush all rules
    print("All iptables rules cleared.")
