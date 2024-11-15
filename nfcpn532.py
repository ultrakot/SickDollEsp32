import py532lib.frame as p532
import py532lib.i2c as i2c
from machine import I2C, Pin

def read_nfc_data():
    """
    Read data from an NFC device using the py532lib library.

    Returns:
        dict: A dictionary containing the read data, or None if no data was read.
    """
    try:
        # Initialize the PN532 device
        i2c.i2c_init()
        pn532 = p532.Frame()

        # Check if a card is present
        if pn532.SAMConfiguration():
            # Read the card data
            data = pn532.Readpassive()

            if data:
                return {
                    'uid': data['uid'],
                    'type': data['type'],
                    'data': data['data']
                }
            else:
                return None
        else:
            return None
    except Exception as e:
        print(f"Error reading NFC data: {e}")
        return None
    
    




# Initialize the I2C bus on ESP32
# i2c = I2C(sda=Pin(21), scl=Pin(22), freq=100000)
# 
# # Create a list of the PN532 device addresses
# pn532_addresses = [0x24, 0x25, 0x26]
# 
# def read_nfc_data(address):
#     """
#     Read data from an NFC device using the py532lib library.
# 
#     Parameters:
#     address (int): The I2C address of the PN532 device.
# 
#     Returns:
#         dict: A dictionary containing the read data, or None if no data was read.
#     """
#     try:
#         # Create a PN532 Frame object for the given address
#         pn532 = p532.Frame(i2c=i2c, address=address)
# 
#         # Check if a card is present
#         if pn532.SAMConfiguration():
#             # Read the card data
#             data = pn532.Readpassive()
# 
#             if data:
#                 # Extract the card UID
#                 uid = ''.join(f'{b:02X}' for b in data['uid'])
#                 print(f"NFC Card UID (address {address}): {uid}")
# 
#                 return {
#                     'uid': data['uid'],
#                     'type': data['type'],
#                     'data': data['data']
#                 }
#             else:
#                 return None
#         else:
#             return None
#     except Exception as e:
#         print(f"Error reading NFC data (address {address}): {e}")
#         return None
# 
# # Read data from all PN532 devices
# for address in pn532_addresses:
#     nfc_data = read_nfc_data(address)
#     if nfc_data:
#         print(f"Data from PN532 at address {address}: {nfc_data}")
#     else:
#         print(f"No data read from PN532 at address {address}")