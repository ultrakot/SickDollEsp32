from machine import I2C, Pin
import time


# Commands for different modes
READER_MODE = b'\xD4\x14\x01'        # Standard reader/writer mode
CARD_EMULATION = b'\xD4\x8C\x00'     # Card emulation mode
P2P_MODE = b'\xD4\x14\x02'           # Peer to peer mode


# SAM (Secure Access Module) configuration is needed before mode changes
SAM_CONFIG = b'\xD4\x14\x01\x14\x01'

# Initialize the I2C bus
#i2c = I2C(sda=Pin(21), scl=Pin(22), freq=400000)

class PN532:
    def __init__(self, reset_pin):#i2c_bus, reset_pin):
        #self.i2c = machine.I2C(i2c_bus)
        self.i2c = I2C(sda=Pin(21), scl=Pin(22), freq=400000)
        self.reset = Pin(reset_pin, Pin.OUT)

#     def config_card_emulation(self):
#         #self.reset.value(1)
#         self.i2c.writeto(0x24, b'\xD4\x14\x01')
#         
#         response = self.i2c.readfrom(0x24, 3)
#         if response[0] != 0xD5 or response[1] != 0x15:
#             raise Exception("Failed to configure card emulation mode")

    def config_card_emulation(self):
        
        # 1. Configure SAM first
        self.i2c.writeto(0x24, SAM_CONFIG)
        time.sleep_ms(100)
        
         # 2. Set Card Emulation Mode
        CARD_MODE = b'\xD4\x8C\x00'
        self.i2c.writeto(0x24, CARD_MODE)
        time.sleep_ms(100)
        
        # 3. Configure Target Mode (necessary for card emulation)
        # Parameters: 
        # - MaxTg: number of targets to detect (usually 1)
        # - BrTy: Baud Rate (106 kbps)
        TARGET_CONFIG = b'\xD4\x4A\x01\x00'
        self.i2c.writeto(0x24, TARGET_CONFIG)
        time.sleep_ms(100)
        
        # 5. Set NDEF data configuration
        # Configure NDEF message format
        NDEF_CONFIG = b'\xD4\x8C\x00\x05'
        self.i2c.writeto(0x24, NDEF_CONFIG)
        time.sleep_ms(100)
        
        try:
            #self.i2c.writeto(0x24, b'\xD4\x14\x01')
            #time.sleep_ms(100)  # Give device time to process
            response = self.i2c.readfrom(0x24, 3)
            if response[0] != 0xD5 or response[1] != 0x15:
                raise Exception("Failed to configure card emulation mode" + str(response[0]))
        except Exception as e:
            print(f"Error in config_card_emulation: {str(e)}")
            raise

    def set_type2_tag(self, data):
        self.i2c.writeto(0x24, b'\xD4\x40\x01\x00' + data)
        response = self.i2c.readfrom(0x24, 3)
        if response[0] != 0xD5 or response[1] != 0x41:
            raise Exception("Failed to set Type 2 tag data")
        
    def reset_module(self):
        # Hardware reset
        self.reset.value(0)
        time.sleep_ms(100)
        self.reset.value(1)
        time.sleep_ms(100)


    def start_emulation(self):
        # 7. Start card emulation
        START_EMULATION = b'\xD4\x8C\x01'
        self.i2c.writeto(self.addr, START_EMULATION)
        time.sleep_ms(100)

    def stop_emulation(self):
        # 8. Stop card emulation
        STOP_EMULATION = b'\xD4\x8C\x02'
        self.i2c.writeto(self.addr, STOP_EMULATION)
        time.sleep_ms(100)

    def check_status(self):
        # 9. Check emulation status
        STATUS_CHECK = b'\xD4\x8C\x03'
        self.i2c.writeto(self.addr, STATUS_CHECK)
        time.sleep_ms(100)
        status = self.i2c.readfrom(self.addr, 3)
        return status
    
# Example usage
#nfc = PN532(i2c_bus=0, reset_pin=15)
nfc = PN532(reset_pin=15)
nfc.reset_module()

nfc.config_card_emulation()
#nfc.set_type2_tag(b'https://example.com')