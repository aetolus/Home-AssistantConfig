import pygatt
import logging

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
    device = adapter.connect('d5:d3:e0:82:10:bd', 10, pygatt.BLEAddressType.random)

    characteristic = "0000f006-0000-1000-8000-00805f9b34fb"
    device.char_write(characteristic, bytearray([0x01000015]))

    device.subscribe("0000f006-0000-1000-8000-00805f9b34fb",
                     callback=handle_data)
finally:
    adapter.stop()