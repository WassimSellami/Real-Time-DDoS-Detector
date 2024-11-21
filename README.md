# DDoS Traffic Classification System

## Network Interface Configuration

The system captures network traffic from your network interface. By default, it's configured to use the "Ethernet" interface. If you're using a wireless connection, you'll need to change this setting.

### How to Change Network Interface

1. Open the `constants.py` file
2. Locate the `NETWORK_INTERFACE` constant in the `Constants` class
3. Change its value based on your network interface:
   - For wired connection: `NETWORK_INTERFACE = "Ethernet"`
   - For wireless connection: `NETWORK_INTERFACE = "Wi-Fi"`

### How to Find Your Network Interface Name

#### Windows
1. Open Command Prompt
2. Type `ipconfig` and press Enter
3. Look for your active connection (either "Ethernet adapter" or "Wireless LAN adapter")

#### Linux
1. Open Terminal
2. Type `ip link show` or `ifconfig` and press Enter
3. Common names include:
   - Ethernet: `eth0`, `enp3s0`
   - Wi-Fi: `wlan0`, `wifi0`

#### macOS
1. Open Terminal
2. Type `networksetup -listallhardwareports` and press Enter
3. Look for your active connection and its corresponding device name