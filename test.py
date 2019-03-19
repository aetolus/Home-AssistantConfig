import pygatt
import logging
import time

logging.basicConfig()
logging.getLogger('pygatt').setLevel(logging.DEBUG)

from binascii import hexlify

adapter = pygatt.GATTToolBackend()

def handle_data(handle, value):
    """
    handle -- integer, characteristic read handle the data was received on
    value -- bytearray, the data returned in the notification
    """
    print("Received data: %s" % hexlify(value))

try:
    adapter.start()
    device = adapter.connect('D5:D3:E0:82:10:BD', 30, pygatt.BLEAddressType.random)
    time.sleep(35)
    adapter.char_write_handle(0x0014, bytearray([0x01, 0x00, 0x00, 0x20]))

finally:
    adapter.stop()

# Battery handle?
#[D5:D3:E0:82:10:BD][LE]> char-read-hnd 0x0008                                                                                                                                                                                       
#Characteristic value/descriptor: 01 18                                                                                                                                                                                              
#[D5:D3:E0:82:10:BD][LE]> char-read-hnd 0x0001                                                                                                                                                                                       
#Characteristic value/descriptor: 00 18                                                                                                                                                                                              
