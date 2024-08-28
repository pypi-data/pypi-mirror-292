# Copyright 2024, Digi International Inc.
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
import time
import string
import random

from digi.xbee.util import utils


def main():
    print(" +-------------------------------------------------+")
    print(" | XBee Python Library Bluetooth parameters Sample |")
    print(" +-------------------------------------------------+\n")

    user = "apiservice"

    start = time.time()

    # pwds = ("NU'9", "*f;@Y\]bM'N<3hk0Ilh", "e")
    # salt = ("2DBC9B73", "008B0934", "00331CB8")
    # bad_ver = ("D79F40C2E237ACC68FEC98AB6CD3CF6D48A868649761E06964E7FA7B23515DA5181DB37495B92B7EA1E1411E907DCFF1972EED5352B4A95DE7C8E8DE1E28F2D81C50589AC83391BF7A9B38E9A79FD6949533D4DF5617153E014202BEEE4F757A747838A631503805468404DF29D0AD22A69631CDE099AF7E262D4A469BCB5786",
    #            "6E2E17870044AA03E3EB093AAE1DAD12CB93ECCAB58EAC4869439A51F27AFF17C57C6BE4E3E33CD1E6C4725F95466C6BFC175C741063784389AB9EEA46A082DA1BB2C5BC8D93D6C8A620F78E155A1B9590F020B63E0DF0D9F80E1B63868D219C82B198F15FA93F2E82821B0984546D94D51E1B2EBD26E99FA68F4CD136AF3635",
    #            "3D5A7E3DC59A23BF1AB48B9CDD1CC21877482161EDA6F49E2FBD64A16B8C1F966B665DD8D0B00DB4C9A2986EA6C9189097D427B8874665FB4D94965BDF9CA0289E561A0AC3D01272C5CAF2F9EBBDF38564E5E8D79C47DEBB3B9447C06C7074B23122A7B6C605301B0891E008E54AF3B5E067758CD9B89537F5B48BC40DDADE1F")
    #
    # for i in range(0, len(pwds)):
    #     print("---------------------- %d ----------------------" % i)
    #     s = utils.hex_string_to_bytes(salt[i])
    #     import digi.xbee.util.srp
    #     # ctx = digi.xbee.util.srp.SRPContext(
    #     #     user, pwds[i], hash_alg=digi.xbee.util.srp.HAType.SHA256,
    #     #     ng_type=digi.xbee.util.srp.NgGroupParams.NG_1024, salt_len=4)
    #     # v = ctx.get_verifier(s)
    #     v = digi.xbee.util.srp.generate_verifier(
    #         user, pwds[i], hash_alg=digi.xbee.util.srp.HAType.SHA256,
    #         ng_type=digi.xbee.util.srp.NgGroupParams.NG_1024, salt=s, sep=":")
    #     print("Password: %s" % pwds[i])
    #     print("Salt: %s" % salt[i])
    #     print("Verifier:     %s" % utils.hex_to_string(v, False))
    #
    #     import srptools
    #     srptools_ctx = srptools.SRPContext(user, password=pwds[i], prime=srptools.constants.PRIME_1024,
    #                                        generator=srptools.constants.PRIME_1024_GEN,
    #                                        hash_func=srptools.constants.HASH_SHA_256, multiplier=None,
    #                                        bits_random=1024, bits_salt=32)
    #     srptools_v = srptools_ctx.get_common_password_verifier(
    #         srptools_ctx.get_common_password_hash(utils.bytes_to_int(s)))
    #     srptools_v = utils.int_to_bytes(srptools_v)
    #     print("Check (%s): %s" % (v == srptools_v, utils.hex_to_string(srptools_v, False)))
    #     if v != srptools_v:
    #         print("==================== ERROR ====================")
    #         break
    # return

    for i in range(1, 1000000 + 1):
        print("---------------------- %d ----------------------" % i)
        length = random.randint(1, 20)
        pwd = ''.join(random.choice(string.printable) for _ in range(length))

        # import digi.xbee.util.srp
        # salt, verifier = digi.xbee.util.srp.create_salted_verification_key(
        #     user, pwd, hash_alg=digi.xbee.util.srp.HAType.SHA256,
        #     ng_type=digi.xbee.util.srp.NgGroupParams.NG_1024, salt_len=4)
        import srp._pysrp
        _mod = srp._pysrp
        salt, verifier = _mod.create_salted_verification_key(
            user, pwd, hash_alg=srp.SHA256, ng_type=srp.NG_1024, salt_len=4)

        print("Password: %s" % pwd)
        print("Salt: %s" % utils.hex_to_string(salt, False))
        print("Verifier:     %s" % utils.hex_to_string(verifier, False))

        # Recalculation of verifier with the same code
        # ctx = digi.xbee.util.srp.SRPContext(user, pwd, hash_alg=digi.xbee.util.srp.HAType.SHA256,
        #                                     ng_type=digi.xbee.util.srp.NgGroupParams.NG_1024, salt_len=4)
        # v = ctx.get_verifier(salt)
        # print("Check verifier (%s): %s" % (verifier == v, utils.hex_to_string(v, False)))
        # if verifier != v:
        #     print("==================== ERROR ====================")
        #     break

        # Recalculate verifier with srptools:
        # PyPI:   https://pypi.org/project/srptools/
        # GitHub: https://github.com/idlesign/srptools
        import srptools
        srptools_ctx = srptools.SRPContext(user, password=pwd, prime=srptools.constants.PRIME_1024,
                                           generator=srptools.constants.PRIME_1024_GEN,
                                           hash_func=srptools.constants.HASH_SHA_256, multiplier=None,
                                           bits_random=1024, bits_salt=32)
        srptools_v = srptools_ctx.get_common_password_verifier(
            srptools_ctx.get_common_password_hash(utils.bytes_to_int(salt)))
        srptools_v = utils.int_to_bytes(srptools_v)
        print("Check (%s): %s" % (verifier == srptools_v, utils.hex_to_string(srptools_v, False)))
        if verifier != srptools_v:
            print("==================== ERROR ====================")
            break

    print("\n\nDuration: %s s" % (time.time() - start))

    # import srp._pysrp
    # _mod = srp._pysrp
    # s1, v1 = _mod.create_salted_verification_key(
    #     user, pwd, hash_alg=srp.SHA256,
    #     ng_type=srp.NG_1024, salt_len=4)


if __name__ == '__main__':
    main()
