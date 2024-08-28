# Copyright 2019, Digi International Inc.
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

import logging

from digi.xbee.devices import XBeeDevice
from digi.xbee.exception import FirmwareUpdateException, OperationNotSupportedException, XBeeException
from digi.xbee import firmware
from digi.xbee.util import utils

# TODO: Replace with the serial port where your local module is connected to.
PORT = "/dev/ttyUSB5"
# TODO: Replace with the baud rate of your local module.
BAUD_RATE = 115200
# TODO: Replace with the location of the firmware files to update.
#XML_FIRMWARE_FILE = "/media/tleon/data/programs/xctu/xctu_6.5.1/XCTU-NG/radio_firmwares/XB3-24Z/XB3-24Z_1009.xml"
#BOOTLOADER_FIRMWARE_FILE = "/media/tleon/data/programs/xctu/xctu_6.5.1/XCTU-NG/radio_firmwares/XB3-boot-rf/xb3-boot-rf_1.8.1.gbl"
#XBEE_FIRMWARE_FILE = "/media/tleon/data/programs/xctu/xctu_6.5.1/XCTU-NG/radio_firmwares/XB3-24Z/XB3-24Z_1009.gbl"
XML_FIRMWARE_FILE = "/media/tleon/data/programs/xctu/xctu_6.5.1/XCTU-NG/radio_firmwares/XB3-24Z/XB3-24Z_1009-th.xml"


def main():
    print(" +--------------------------------------------------+")
    print(" | XBee Python Library Local Firmware Update Sample |")
    print(" +--------------------------------------------------+\n")

    utils.enable_logger("digi.xbee.reader", logging.DEBUG)
    utils.enable_logger("digi.xbee.sender", logging.DEBUG)
    utils.enable_logger("digi.xbee.devices", logging.DEBUG)
    utils.enable_logger("digi.xbee.recovery", logging.INFO)
    utils.enable_logger("digi.xbee.models.zdo", logging.INFO)
    utils.enable_logger("XBeeNetwork", logging.INFO)
    utils.enable_logger("digi.xbee.firmware", logging.DEBUG)
    utils.enable_logger("digi.xbee.profile", logging.DEBUG)

#    device = XBeeDevice(PORT, BAUD_RATE)

    try:
#        device.open()
        print("Starting firmware update process...")
#        device.update_firmware(XML_FIRMWARE_FILE,
#                               xbee_firmware_file=XBEE_FIRMWARE_FILE,
#                               bootloader_firmware_file=BOOTLOADER_FIRMWARE_FILE,
#                               progress_callback=progress_callback,)
        firmware.update_local_firmware(PORT, XML_FIRMWARE_FILE,
                                       #xbee_firmware_file=XBEE_FIRMWARE_FILE,
                                       #bootloader_firmware_file=BOOTLOADER_FIRMWARE_FILE,
                                       progress_callback=progress_callback)
        print("Firmware updated successfully!")
    except (XBeeException, FirmwareUpdateException, OperationNotSupportedException) as e:
        print("ERROR: %s" % str(e))
        exit(1)
    finally:
        print("Finally")
#        if device is not None and device.is_open():
#            device.close()


def progress_callback(task, percent):
    print("%s: %d%%" % (task, percent))


if __name__ == '__main__':
    main()
