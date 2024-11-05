from machine import I2C, Pin

# Initialize the I2C bus
i2c = I2C(sda=Pin(21), scl=Pin(22), freq=400000)

# Scan the I2C bus for available addresses
def scan_i2c_addresses():
    addresses = []
    for addr in range(0x01, 0x80):
        try:
            i2c.writeto(addr, b'')
            addresses.append(hex(addr))
        except OSError:
            pass
    return addresses

# Scan for NFC reader addresses and print the results
nfc_addresses = scan_i2c_addresses()
if nfc_addresses:
    print("NFC reader addresses found:")
    for address in nfc_addresses:
        print(address)
else:
    print("No NFC readers found on the I2C bus.")