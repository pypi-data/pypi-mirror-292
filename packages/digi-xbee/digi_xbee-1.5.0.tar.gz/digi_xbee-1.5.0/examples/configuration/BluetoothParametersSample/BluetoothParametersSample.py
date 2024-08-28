# Copyright 2017, Digi International Inc.
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

from digi.xbee.devices import XBeeDevice
from digi.xbee.util import utils
from digi.xbee.models.atcomm import ATStringCommand

# TODO: Replace with the serial port where your local module is connected to.
PORT = "/dev/ttyUSB4"
# TODO: Replace with the baud rate of your local module.
BAUD_RATE = 9600


def main():
    print(" +-------------------------------------------------+")
    print(" | XBee Python Library Bluetooth parameters Sample |")
    print(" +-------------------------------------------------+\n")

    device = XBeeDevice(PORT, BAUD_RATE)

    try:
        device.open(force_settings=True)

        # Set parameters.
        #device.enable_apply_changes(False)
        #device.execute_command('RE')
        #device.execute_command('WR')
        #device.enable_apply_changes(True)

        user = "apiservice"
        pwd = "1257c"

        device.disable_bluetooth()
        # Configure the Bluetooth password.
        device.update_bluetooth_password(pwd)
        device.enable_bluetooth()
        return

        import digi.xbee.util.srp
        salt, verifier = digi.xbee.util.srp.create_salted_verification_key(
            user, pwd, hash_alg=digi.xbee.util.srp.HAType.SHA256,
            ng_type=digi.xbee.util.srp.NgGroupParams.NG_1024, salt_len=4)

        print("Salt: %s" % utils.hex_to_string(salt, False))
        print("Verifier: %s" % utils.hex_to_string(verifier, False))


        # #import srp
        # #s1, v1 = srp.create_salted_verification_key(
        # #    "apiservice", "1257c", hash_alg=srp.SHA256,
        # #    ng_type=srp.NG_1024, salt_len=4)
        # import srp._pysrp
        # _mod = srp._pysrp
        # s1, v1 = _mod.create_salted_verification_key(
        #     user, pwd, hash_alg=srp.SHA256,
        #     ng_type=srp.NG_1024, salt_len=4)
        # print("S1: %s" % utils.hex_to_string(s1, False))
        # print("V1: %s" % utils.hex_to_string(v1, False))
        # ctx = digi.xbee.util.srp.SRPContext(user, pwd, hash_alg=digi.xbee.util.srp.HAType.SHA256,
        #                                     ng_type=digi.xbee.util.srp.NgGroupParams.NG_1024, salt_len=4)
        # v = ctx.get_verifier(s1)
        # print("Check verifier (%s): %s" % (v1 == v, utils.hex_to_string(v, False)))
        #
        # device.update_bluetooth_salt_verifier(salt, verifier, apply=True, save=True)
        #
        # print("All parameters were set correctly!")
        # print(utils.hex_to_string(device.get_parameter(ATStringCommand.DOLLAR_S), pretty=False))
        # print(utils.hex_to_string(device.get_parameter(ATStringCommand.DOLLAR_V), pretty=False), end="")
        # print(utils.hex_to_string(device.get_parameter(ATStringCommand.DOLLAR_W), pretty=False), end="")
        # print(utils.hex_to_string(device.get_parameter(ATStringCommand.DOLLAR_X), pretty=False), end="")
        # print(utils.hex_to_string(device.get_parameter(ATStringCommand.DOLLAR_Y), pretty=False))

        print("All parameters were set correctly!")

    finally:
        if device is not None and device.is_open():
            device.close()


if __name__ == '__main__':
    main()
