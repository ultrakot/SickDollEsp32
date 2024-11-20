from machine import I2C, Pin
import time
from NFCModule import NFC_Module  # Assuming the provided NFC library is named 'library.py'
import testNFC  

# Initialize I2C and NFC module
i2c = I2C(0, scl=Pin(22), sda=Pin(21))  # Modify pins as per your setup
nfc = NFC_Module(i2c)

# Define RX and TX buffers
tx_buf = b"Hi, this message comes from NFC INITIATOR."
tx_len = len(tx_buf)
rx_buf = bytearray(50)

def setup():
    """Setup NFC module"""
    print("P2P Initiator Demo BY ELECHOSUE!")
    nfc.begin()
    
    version_data = nfc.get_version()
    if version_data == 0:
        print("Didn't find PN53x board")
        while True:
            pass  # Halt
    
    print(f"Found chip PN5{(version_data >> 24) & 0xFF:X}")
    print(f"Firmware ver. {(version_data >> 16) & 0xFF}.{(version_data >> 8) & 0xFF}")
    
    # Set normal mode, disable SAM
    #testNFC.configure_sam_debug()
#     if not nfc.sam_configuration():
#         print("Failed to configure SAM mode")
#         while True:
#             pass  # Halt
    nfc.p2p_initiator_init()



def loop():
    """Run NFC initiator process"""
    if nfc.in_list_passive_target():
        print("Target is sensed.")
        
        rx_len = bytearray(1)
        if nfc.mifare_write_block(tx_buf, tx_len):
            print("Data sent successfully")
            data_received = nfc.mifare_read_block(tx_len)
            print(f"Data Received: {data_received.decode('utf-8')}")
        else:
            print("Data exchange failed")

# Main code
setup()
while True:
    loop()
    time.sleep(1)
