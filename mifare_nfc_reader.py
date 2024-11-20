from machine import I2C, Pin
import time
from NFCModule import NFC_Module  # Ensure this matches your library filename
import testNFC  

# Initialize I2C and NFC module
i2c = I2C(0, scl=Pin(22), sda=Pin(21))  # Adjust pins for your setup
nfc = NFC_Module(i2c)

def setup():
    """Setup NFC module"""
    print("MF1S50 Reader Demo From Elechouse!")
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
    """Main loop for polling and reading NFC cards"""
    buf = bytearray(32)
    print("Polling for an NFC card...")
    
    # Poll for MIFARE cards
    if nfc.in_list_passive_target():
        print("Card detected!")
        
        # Check the UID length and proceed if valid
        uid_length = buf[0]
        if uid_length == 4:  # MIFARE Classic card typically has a 4-byte UID
            print(f"UUID length: {uid_length}")
            uid = buf[1:1+uid_length]
            print(f"UUID: {uid.hex().upper()}")
            
            # Default KeyA for MIFARE: 0xFF 0xFF 0xFF 0xFF 0xFF 0xFF
            key = bytearray([0xFF] * 6)
            blocknum = 4
            
            # Authenticate block 4
            if nfc.mifare_authenticate(0, blocknum, uid, key):
                print("Authentication success.")
                
                # Uncomment below to write to block 4
                # block_data = bytearray(b"Elechouse - NFC")
                # if nfc.mifare_write_block(blocknum, block_data):
                #     print("Write block successfully.")
                
                # Read blocks 4 to 7
                for i in range(4):
                    block = nfc.mifare_read_block(blocknum + i)
                    if block:
                        print(f"Read block {blocknum + i} successfully: {block.hex().upper()}")
                    else:
                        print(f"Failed to read block {blocknum + i}.")
            else:
                print("Authentication failed.")
        else:
            print("Invalid UID length or unsupported card.")
    else:
        print("No card detected.")

# Run the setup once
setup()

# Continuous polling
while True:
    loop()
    time.sleep(1)
