# DDoS Traffic Classification System

## Network Interface Configuration

1. Open the `constants.py` file
2. Locate the `NETWORK_INTERFACE` constant in the `Constants` class
3. Change its value based on your network interface:
   - For wired connection: `NETWORK_INTERFACE = "Ethernet"`
   - For wireless connection: `NETWORK_INTERFACE = "Wi-Fi"`

## Model Selection

In `main.py`, you can choose between two models for traffic classification:

### Using Decision Tree Model
Uncomment the following code and comment out the CNN code:
