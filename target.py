from machine import I2C, Pin
import time
from NFCModule import NFC_Module  
import testNFC  

# Initialize I2C and NFC module
i2c = I2C(0, scl=Pin(22), sda=Pin(21))  # Adjust pins for your setup
nfc = NFC_Module(i2c)

# Define RX and TX buffers
tx_buf = b"Hi, This message comes from NFC TARGET."
rx_buf = bytearray(50)  # Buffer for received data

def setup():
    """Setup NFC module as a Target"""
    print("P2P Target Demo From Elechouse!")
    nfc.begin()
    
    # Get version data from NFC module
    versiondata = nfc.get_version()
    if versiondata == 0:
        print("Didn't find PN53x board")
        while True:
            pass  # Halt execution
    
    print(f"Found chip PN5{(versiondata >> 24) & 0xFF:X}")
    print(f"Firmware ver. {(versiondata >> 16) & 0xFF}.{(versiondata >> 8) & 0xFF}")
    
    # Configure SAM (Set normal mode)
    testNFC.configure_sam_debug()
#     if not nfc.sam_configuration():
#         print("Failed to configure SAM mode")
#         while True:
#             pass  # Halt execution

def loop():
    """Main loop to handle P2P Target mode"""
    print("Waiting for an Initiator...")
    
    # Initialize as Target
    if nfc.P2PTargetInit():
        print("Initiator is sensed.")
        
        # Prepare to send and receive data
        tx_len = len(tx_buf)
        
        # Transmit and receive data
        if nfc.P2PTargetTxRx(tx_buf, tx_len, rx_buf):
            print("Data Received:")
            print(rx_buf.decode('utf-8'))  # Assuming received data is UTF-8 encoded
        else:
            print("Failed to send/receive data.")
    else:
        print("No Initiator detected.")

# Run the setup once
setup()

# Continuous loop
while True:
    loop()
    time.sleep(1)
