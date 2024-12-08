import subprocess


def block_ips(ips_to_block):
    for ip in ips_to_block:
        result_out = subprocess.run(
            [
                "sudo",
                "iptables",
                "-A",
                "OUTPUT",
                "-d",
                ip,
                "-j",
                "DROP",
            ],
            capture_output=True,
            text=True,
        )

        result_in = subprocess.run(
            [
                "sudo",
                "iptables",
                "-A",
                "INPUT",
                "-s",
                ip,
                "-j",
                "DROP",
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

        if result_out.returncode == 0:
            print(f"Successfully blocked outgoing traffic for IP: {ip}")
        else:
            print(
                f"Failed to block outgoing traffic for IP: {ip}. Error: {result_out.stderr}"
            )


def cleanup_rules():
    subprocess.run(["sudo", "iptables", "-F"], check=True)
    print("All iptables rules cleared.")
