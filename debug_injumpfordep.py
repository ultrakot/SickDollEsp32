from machine import I2C, Pin
import time
from NFCModule import NFC_Module

def debug_injumpfordep(nfc):
    """
    Send InJumpForDEP command and analyze NFC hardware response
    
    Args:
        nfc (PN532_Module): Initialized PN532 module
    """
    print("Starting InJumpForDEP command debug...")
    
    # Command buffer for InJumpForDEP
    command = bytearray([
        0x56,   # Command code for InJumpForDEP
        0x01,   # Active mode (0x01 for active, 0x00 for passive)
        0x02,   # Baud rate (424 Kbps: 0x02)
        0x01,   # Presence of NFCID3i field and General Bytes Gi
        0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF,  # Some example bytes
        0x00, 0x11, 0x22,  # NFCID3i
        0x02,   # Length of General Bytes Gi
        0x00, 0xFF  # General Bytes Gi
    ])
    
    # Send command and get response
    response = nfc.send_command_get_response(command, 25)
    
    if not response:
        print("No response received from hardware.")
        return
    
    # Print raw response for debugging
    print("Raw Response:", ' '.join(f'{byte:02X}' for byte in response))
    
    # Basic response analysis
    if len(response) >= 7:
        # Check for expected response markers
        if response[0] == 0xD5 and response[1] == 0x57:
            print("InJumpForDEP executed successfully!")
            print(f"  Target Type: {response[2]:02X}")
            print(f"  Number of Targets: {response[3]}")
            
            # Print additional target data
            if len(response) > 4:
                print("  Target Data:", 
                      ' '.join(f'{byte:02X}' for byte in response[4:]))
        else:
            print("Unexpected response format.")
    else:
        print("Response too short.")

def main():
    """
    Main function to initialize I2C and NFC module, then run debug
    """
    try:
        # Initialize I2C (adjust pins for your specific setup)
        i2c = I2C(0, scl=Pin(22), sda=Pin(21))
        
        # Initialize NFC Module
        nfc = NFC_Module(i2c)
        
        # Run debug function
        debug_injumpfordep(nfc)
    
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()