#!/usr/bin/python
# Copyright 2020, Digi International Inc.
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

import atexit
import mmap
import os
import re
import shutil
import sys

from digi.xbee.exception import XBeeException
from digi.xbee import firmware
from zipfile import BadZipFile, ZipFile

PORT = "/dev/ttyXBee"
EXTRACT_DIR_PATH = "/tmp/xbee-recovery"

_last_task = None


def main():
    print("Starting XBee recovery process...")

    if len(sys.argv) < 2:
        print("ERROR: Recovery zip file must be specified")
        exit(1)

    atexit.register(exit_handler)

    zip_file_path = sys.argv[1]
    if not os.path.isfile(zip_file_path):
        print("ERROR: Could not find recovery zip file '%s'" % zip_file_path)
        exit(1)

    try:
        with ZipFile(zip_file_path, 'r') as zip_file:
            zip_file.extractall(EXTRACT_DIR_PATH)
    except BadZipFile as e:
        print("ERROR: Could not decompress file '%s': %s" % (zip_file_path, str(e)))
        exit(1)

    xml_file_path = get_file(EXTRACT_DIR_PATH, name_pattern="^XB3-24.*.xml$")
    fw_file_path = get_file(EXTRACT_DIR_PATH, name_pattern="^XB3-24.*.gbl$",
                            strings_to_find=[b'\xEB\x17\xA6\x03'])
    bl_file_path = get_file(EXTRACT_DIR_PATH, name_pattern="^xb3-boot-rf.*.gbl$",
                            strings_to_find=[b'\xEB\x17\xA6\x03', b'Gecko Bootloader'])

    if not xml_file_path or not fw_file_path or not bl_file_path:
        print("ERROR: Invalid recovery zip file '%s'" % zip_file_path)
        exit(1)

    try:
        firmware.update_local_firmware(PORT, xml_file_path,
                                       xbee_firmware_file=fw_file_path,
                                       bootloader_firmware_file=bl_file_path,
                                       progress_callback=progress_callback)
        print("\nXBee successfully recovered!")
    except XBeeException as e:
        print("\nERROR: Unable to recover XBee: %s" % str(e))
        exit(1)


def progress_callback(task, percent):
    global _last_task

    sys.stdout.write("%s%s: %d%%" %
                     ("\r" if task == _last_task else "", task, percent))
    _last_task = task


def get_file(dir_path, name_pattern=None, strings_to_find=None):
    file_paths = []

    for file_name in os.listdir(dir_path):
        if not name_pattern or re.match(name_pattern, file_name):
            file_paths.append(os.path.join(dir_path, file_name))

    if not file_paths:
        return None

    if not strings_to_find:
        return file_paths[0]

    for file_path in file_paths:
        with open(file_path, 'rb', 0) as file, \
                mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ) as contents:
            matches = True
            for string in strings_to_find:
                if contents.find(string) == -1:
                    matches = False
                    break
            if matches:
                return file_path

    return None


def exit_handler():
    if os.path.isdir(EXTRACT_DIR_PATH):
        shutil.rmtree(EXTRACT_DIR_PATH, ignore_errors=True)


if __name__ == '__main__':
    main()
