from machine import I2C, Pin
import time

# Constants
PN532_I2C_ADDRESS = 0x24

# Commands
PN532_COMMAND_GETFIRMWAREVERSION = 0x02
PN532_COMMAND_SAMCONFIGURATION = 0x14
PN532_COMMAND_INLISTPASSIVETARGET = 0x4A
PN532_COMMAND_INDATAEXCHANGE = 0x40
PN532_COMMAND_INJUMPFORDEP = 0x56
PN532_COMMAND_TGINITASTARGET = 0x8C
PN532_COMMAND_TGGETDATA = 0x86
PN532_COMMAND_TGSETDATA = 0x8E
PN532_COMMAND_SETPARAMETERS = 0x12

# Response bytes
PN532_PREAMBLE = 0x00
PN532_STARTCODE1 = 0x00
PN532_STARTCODE2 = 0xFF
PN532_POSTAMBLE = 0x00
PN532_HOSTTOPN532 = 0xD4

# Frame Identifiers
NFC_FRAME_ID_INDEX = 6

# Mifare Commands
MIFARE_CMD_AUTH_A = 0x60
MIFARE_CMD_AUTH_B = 0x61
MIFARE_CMD_READ = 0x30
MIFARE_CMD_WRITE = 0xA0

class NFC_Module:
    def __init__(self, i2c):
        self.i2c = i2c
        self.nfc_buf = bytearray(64)  # Buffer for commands/responses
        
    def begin(self):
        """Initialize the NFC module"""
        pass  # No specific initialization needed for MicroPython
        
    def get_version(self):
        """Get PN532 firmware version"""
        self.nfc_buf[0] = PN532_COMMAND_GETFIRMWAREVERSION
        if not self._write_cmd_check_ack(self.nfc_buf, 1):
            return 0
            
        self._wait_ready()
        data = self._read_data(12)
        if data[5] != 0xD5:
            return 0
            
        version = (data[7] << 24) | (data[8] << 16) | (data[9] << 8) | data[10]
        return version
        
    def sam_configuration(self, mode=0x01, timeout=0x14, irq=0x00):
        """Configure the Secure Access Module"""
        self.nfc_buf[0] = PN532_COMMAND_SAMCONFIGURATION
        self.nfc_buf[1] = mode
        self.nfc_buf[2] = timeout
        self.nfc_buf[3] = irq
        
        if not self._write_cmd_check_ack(self.nfc_buf, 4):
            return False
            
        data = self._read_data(8)
        return data[6] == PN532_COMMAND_SAMCONFIGURATION
        
    def in_list_passive_target(self, brty=0x00, maxtg=0x01):
        """Look for NFC tags"""
        self.nfc_buf[0] = PN532_COMMAND_INLISTPASSIVETARGET
        self.nfc_buf[1] = maxtg
        self.nfc_buf[2] = brty
        
        if not self._write_cmd_check_ack(self.nfc_buf, 3):
            return None
            
        self._wait_ready()
        data = self._read_data(20)
        
        if data[NFC_FRAME_ID_INDEX] != (PN532_COMMAND_INLISTPASSIVETARGET + 1):
            return None
            
        if data[NFC_FRAME_ID_INDEX + 1] != 1:
            return None
            
        uid_length = data[12]
        uid = data[13:13 + uid_length]
        return uid
        
    def mifare_authenticate(self, auth_type, block, uid, key):
        """Authenticate a Mifare card block"""
        self.nfc_buf[0] = PN532_COMMAND_INDATAEXCHANGE
        self.nfc_buf[1] = 1  # Card number
        self.nfc_buf[2] = MIFARE_CMD_AUTH_A + (auth_type & 0x01)
        self.nfc_buf[3] = block
        
        # Copy key and UID
        self.nfc_buf[4:10] = key
        self.nfc_buf[10:10 + len(uid)] = uid
        
        if not self._write_cmd_check_ack(self.nfc_buf, 10 + len(uid)):
            return False
            
        self._wait_ready()
        data = self._read_data(8)
        
        return (data[NFC_FRAME_ID_INDEX] == (PN532_COMMAND_INDATAEXCHANGE + 1) and 
                data[NFC_FRAME_ID_INDEX + 1] == 0)
    
    def mifare_read_block(self, block):
        """Read a Mifare card block"""
        self.nfc_buf[0] = PN532_COMMAND_INDATAEXCHANGE
        self.nfc_buf[1] = 1  # Card number
        self.nfc_buf[2] = MIFARE_CMD_READ
        self.nfc_buf[3] = block
        
        if not self._write_cmd_check_ack(self.nfc_buf, 4):
            return None
            
        self._wait_ready()
        data = self._read_data(26)
        
        if (data[NFC_FRAME_ID_INDEX] != (PN532_COMMAND_INDATAEXCHANGE + 1) or
            data[NFC_FRAME_ID_INDEX + 1] != 0):
            return None
            
        return bytes(data[8:24])  # Return 16 bytes of block data
        
    def mifare_write_block(self, block, data):
        """Write data to a Mifare card block"""
        if len(data) != 16:
            return False
            
        self.nfc_buf[0] = PN532_COMMAND_INDATAEXCHANGE
        self.nfc_buf[1] = 1  # Card number
        self.nfc_buf[2] = MIFARE_CMD_WRITE
        self.nfc_buf[3] = block
        self.nfc_buf[4:20] = data
        
        if not self._write_cmd_check_ack(self.nfc_buf, 20):
            return False
            
        self._wait_ready()
        resp = self._read_data(26)
        
        return (resp[NFC_FRAME_ID_INDEX] == (PN532_COMMAND_INDATAEXCHANGE + 1) and
                resp[NFC_FRAME_ID_INDEX + 1] == 0)
    
    def _write_cmd(self, cmd, cmd_len):
        """Write a command to the PN532"""
        # Calculate checksum
        checksum = PN532_PREAMBLE + PN532_PREAMBLE + PN532_STARTCODE2
        frame = bytearray([
            PN532_PREAMBLE,
            PN532_PREAMBLE,
            PN532_STARTCODE2,
            cmd_len + 1,
            -(cmd_len + 1) & 0xFF,
            PN532_HOSTTOPN532
        ])
        checksum += PN532_HOSTTOPN532
        
        # Add command bytes
        for i in range(cmd_len):
            checksum += cmd[i]
            frame.append(cmd[i])
            
        # Add checksum and postamble
        frame.append(~checksum & 0xFF)
        frame.append(PN532_POSTAMBLE)
        
        # Write to I2C
        try:
            self.i2c.writeto(PN532_I2C_ADDRESS, frame)
            return True
        except:
            return False
    
    def _read_data(self, count):
        """Read data from the PN532"""
        try:
            # Read raw data (add 1 for status byte)
            data = bytearray(count + 1)
            self.i2c.readfrom_into(PN532_I2C_ADDRESS, data)
            return data[1:]  # Skip status byte
        except Exception as e:
            print(f"Data read error: {e}")
            return None
    
    def _read_ack(self):
        """Read and verify ACK from PN532"""
        data = self._read_data(6)
        if not data:
            return False
            
        # Check for ACK pattern
        return (data[0] == 0x00 and
                data[1] == 0x00 and
                data[2] == 0xFF and
                data[3] == 0x00 and
                data[4] == 0xFF and
                data[5] == 0x00)
    
    def _write_cmd_check_ack(self, cmd, cmd_len):
        """Write command and check for ACK"""
        if not self._write_cmd(cmd, cmd_len):
            return False
            
        self._wait_ready()
        return self._read_ack()
    
    def _wait_ready(self, timeout_ms=100):
        """Wait for chip to be ready"""
        time.sleep_ms(timeout_ms)
        return True

    def p2p_initiator_init(self,  debug=True):
        """
        Configure PN532 as an initiator in Peer-to-Peer mode with correct commands.
        """
        # Avoid resend command
        if not hasattr(self, '_send_flag'):
            self._send_flag = 1  # Initialize static variable equivalent

        # Prepare the command buffer
        self.nfc_buf[0] = 0x56  # Command code for INJUMPFORDEP
        self.nfc_buf[1] = 0x01  # Active mode (0x01 for active, 0x00 for passive)
        self.nfc_buf[2] = 0x02  # Baud rate (201 Kbps: 0x02, 424 Kbps: 0x02)
        self.nfc_buf[3] = 0x01  # Presence of NFCID3i field and General Bytes Gi

        # NFCID3i (optional identifier)
        self.nfc_buf[4:13] = b'\xAA\xBB\xCC\xDD\xEE\xFF\x00\x11\x22'

        # General Bytes Gi (optional parameters)
        self.nfc_buf[13] = 0x02  # Length of General Bytes Gi
        self.nfc_buf[14:16] = b'\x00\xFF'  # Example general bytes

        # Send the command if send_flag is set
        cmd_length = 16  # Adjust length based on the buffer
        if self._send_flag:
            self._send_flag = 0
            if not self._write_cmd_check_ack(self.nfc_buf, cmd_length):
                print("InJumpForDEP send failed")
                return False
            print("InJumpForDEP command sent")
    
        # Wait for response
        self._wait_ready(10)
        self._read_data(25)

        # Debug: Print the full response
        if debug:
            print("Response after InJumpForDEP command:")
            print(" ".join(f"{byte:02X}" for byte in self.nfc_buf[:25]))



        # Verify response
        if self.nfc_buf[5] != 0xD5:
            print("InJumpForDEP read failed")
            return False
    
        if self.nfc_buf[6] != 0x57:  # Response should be 0x57
            print("Initiator init failed")
            return False
    
        if self.nfc_buf[7] != 0:
            print("Initiator init error")
            return False
    
        print("InJumpForDEP read success")
        self._send_flag = 1
        return True
    
    def send_command_get_response(self, command, response_length):
        """
        Send a command and get the response
        
        Args:
            command (bytearray): Command to send
            response_length (int): Expected length of response
        
        Returns:
            bytearray or None: Response data or None if failed
        """
        if not self.write_command(command):
            print("Failed to send command")
            return None
        
        # Wait a short time for the module to process (adjust as needed)
        import time
        time.sleep_ms(10)
        
        return self.read_data(response_length)
    
    
    def write_command(self, command):
        """
        Write command to PN532 module
        
        Args:
            command (bytearray): Command to send
        
        Returns:
            bool: True if command sent successfully, False otherwise
        """
        try:
            # Typical I2C write method
            self.i2c.writeto(PN532_I2C_ADDRESS, command)
            return True
        except Exception as e:
            print(f"Command write error: {e}")
            return False
        
    def read_data(self, count):
        """
        Read data from the PN532
        
        Args:
            count (int): Number of bytes to read
        
        Returns:
            bytearray or None: Read data (excluding status byte) or None if read fails
        """
        try:
            # Read raw data (add 1 for status byte)
            data = bytearray(count + 1)
            self.i2c.readfrom_into(PN532_I2C_ADDRESS, data)
            return data[1:]  # Skip status byte
        except Exception as e:
            print(f"Data read error: {e}")
            return None
        
#     def p2p_initiator_init(self):
#         """
#         Configure PN532 as an initiator in Peer-to-Peer mode.
#         """
#         # Avoid resend command
#         if not hasattr(self, '_send_flag'):
#             self._send_flag = 1  # Initialize static variable equivalent
# 
#         # Prepare the command buffer
#         self.nfc_buf[0] = PN532_COMMAND_INJUMPFORDEP
#         self.nfc_buf[1] = 0x01  # Active mode
#         self.nfc_buf[2] = 0x02  # 201 Kbps
#         self.nfc_buf[3] = 0x01
#         self.nfc_buf[4] = 0x00
#         self.nfc_buf[5] = 0xFF
#         self.nfc_buf[6] = 0xFF
#         self.nfc_buf[7] = 0x00
#         self.nfc_buf[8] = 0x00
# 
#         # Send the command if send_flag is set
#         if self._send_flag:
#             self._send_flag = 0
#             if not self._write_cmd_check_ack(self.nfc_buf, 9):
#                 print("InJumpForDEP send failed")
#                 return 0
#             print("InJumpForDEP command sent")
# 
#         # Wait for response
#         self._wait_ready(10)
#         self._read_data(25)
#     
#         # Verify response
#         if self.nfc_buf[5] != 0xD5:
#             print("InJumpForDEP read failed")
#             return 0
# 
#         if self.nfc_buf[self.NFC_FRAME_ID_INDEX] != (PN532_COMMAND_INJUMPFORDEP + 1):
#             print("Initiator init failed")
#             return 0
# 
#         if self.nfc_buf[self.NFC_FRAME_ID_INDEX + 1] != 0:
#             print("Initiator init error")
#             return 0
# 
#         print("InJumpForDEP read success")
#         self._send_flag = 1
#         return 1
    