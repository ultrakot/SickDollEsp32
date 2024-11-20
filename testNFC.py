from machine import I2C, Pin
import time
from NFCModule import NFC_Module  # Ensure this matches your library filename

# Initialize I2C and NFC module
i2c = I2C(0, scl=Pin(22), sda=Pin(21))  # Adjust pins for your setup
nfc = NFC_Module(i2c)

def configure_sam_debug():
    """
    Configure Secure Access Module (SAM) with detailed debugging.
    """
    print("Starting SAM configuration with debug info...")
    
    # SAM configuration parameters
    command = bytearray([0x14, 0x01, 0x14, 0x00])  # Command: SAMConfiguration
    # 0x14 = Command code
    # 0x01 = Normal mode
    # 0x14 = Timeout of 50ms
    # 0x00 = IRQ disabled
    
    print(f"Sending SAM configuration command: {command}")
    if not nfc._write_cmd(command, len(command)):
        print("Failed to send the command to NFC hardware. Check I2C connection.")
        return
    
    print("Waiting for acknowledgment...")
    if not nfc._read_ack():
        print("Did not receive acknowledgment from the NFC hardware. Possible issues:")
        print("  - Incorrect wiring.")
        print("  - I2C communication issues.")
        print("  - Faulty NFC module.")
        return
    
    print("Acknowledgment received. Reading response from hardware...")
    response = nfc._read_data(8)  # Adjust length as necessary for SAM Configuration response
    
    if not response:
        print("No response received from hardware. Possible causes:")
        print("  - Timeout or communication issue.")
        print("  - Incorrect command structure.")
        return
    
    print(f"Response received: {response}")
    
    # Check the response for SAM Configuration success
    if len(response) >= 7 and response[6] == 0x15:  # 0x15 indicates success
        print("SAM configured successfully!")
    else:
        print("SAM configuration failed. Response details:")
        print(f"  Full response: {response}")
        print("  Possible causes:")
        print("    - Invalid command parameters.")
        print("    - Unsupported SAM configuration by the NFC hardware.")
        print("    - Hardware fault.")

# Run the SAM configuration with debugging
configure_sam_debug()
