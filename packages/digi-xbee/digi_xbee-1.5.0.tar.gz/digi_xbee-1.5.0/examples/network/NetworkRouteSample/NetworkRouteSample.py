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
import threading
import time
from queue import Queue

from digi.xbee.exception import ATCommandException, XBeeException
from digi.xbee.models.address import XBee64BitAddress, XBee16BitAddress
from digi.xbee.models.mode import NeighborDiscoveryMode
from digi.xbee.models.protocol import Role
from digi.xbee.models.status import NetworkDiscoveryStatus, TransmitStatus
from digi.xbee.devices import XBeeDevice, RemoteXBeeDevice, ZigBeeDevice, XBeeNetwork, Raw802Device, DigiMeshDevice, NetworkEventType, NetworkRoute, \
    RemoteZigBeeDevice

# TODO: Replace with the serial port where your local module is connected to.
from digi.xbee.packets.common import ATCommPacket
from digi.xbee.util import utils

PORT = "/dev/ttyUSB2"
# TODO: Replace with the baud rate of your local module.
BAUD_RATE = 115200

all_routes = []


class _XBeeInitializer(threading.Thread):
    """
    This class represents an XBee initializer, a thread that initializes the
    XBees in a queue.
    """

    def __init__(self):
        """
        Class constructor. Instantiates a new :class:`._XBeeInitializer` object.
        """

        threading.Thread.__init__(self)

        self.daemon = True

        self.__discovered_xbees = Queue(100)

        self.__stop = False
        self.__running = False

    def run(self):
        """
        This is the method that will be executing for updating the list of XBee devices.
        """
        self.__running = True

        while not self.__stop:
            if not self.__discovered_xbees.empty():
                node = self.__discovered_xbees.get()
                #print("-------------------- Initializing node: %s" % node)

                route = None
                status = None
                if node.get_role() == Role.END_DEVICE:
                    if node.parent:
                        route = self._get_route_for(node.parent)
                        print("--------------------            Route: %s" % route)
                        if route:
                            route = NetworkRoute(route.source, node, [node.parent, *route.hops])
                else:
                    status, route = self._get_route_for(node)

                #print("--------------------            Route: %s" % route)

                if status == TransmitStatus.SUCCESS and route:
                    if route in all_routes:
                        all_routes.remove(route)
                    all_routes.append(route)

                try:
                    node.read_device_info(init=False)
                except ATCommandException as e:
                    print("Error while initializing XBee %s: %s (%s)"
                          % (str(node), str(e), e.status.description))
                except XBeeException as e:
                    print("Error while initializing XBee %s: %s" % (str(node), str(e)))

                #print("--------------------            Role: %s, FW: %s, HW: %s"
                #      % (node.get_role(), node.get_firmware_version(), node.get_hardware_version()))

                print_all_routes()

            time.sleep(1)

        self.__running = False

    def _get_route_for(self, remote):
        for route in all_routes:
            if route.destination == remote:
                return route

        return remote.get_local_xbee_device().get_route_to_node(remote)

    def add_discovered_xbee(self, xbee):
        """
        Adds the provided XBee to the list of discovered XBees, to be initiliazed later.

        Args:
             xbee (:class:`digi.xbee.devices.RemoteXBeeDevice`): The discovered XBee device.
        """
        if self.__discovered_xbees.full():
            self.__discovered_xbees.get()

        self.__discovered_xbees.put_nowait(xbee)

    def is_running(self):
        """
        Returns whether this instance is running or not.

        Returns:
            Boolean: ``True`` if this instance is running, ``False`` otherwise.
        """
        return self.__running

    def is_all_done(self):
        return self.__discovered_xbees.empty()

    def stop(self):
        self.__stop = True


def callback_discovery_finished(status):
    if status == NetworkDiscoveryStatus.SUCCESS:
        print("  Discovery process finished successfully.")
    else:
        print("  There was an error discovering devices: %s" % status.description)


def cb_network_modified(event_type, reason, node):
    print("  >>>> Network event:")
    print("         Type: %s (%d)" % (event_type.description, event_type.code))
    print("         Reason: %s (%d)" % (reason.description, reason.code))

    if node:
        print("         Node:")
        print("            %s" % node)


def callback_device_discovered(node):
    xbee_initializer.add_discovered_xbee(node)


def print_nodes(xbee):
    xb_net = xbee.get_network()
    #print("\n  Current network nodes:\n    ", end='')
    print("\n  Current network nodes: %d" % xb_net.get_number_devices())
    if xb_net.has_devices():
        print("    %s" % '\n    '.join(map(str, xb_net.get_devices())))

        print("  ALL Connections:\n    ", end='')
        print("%s" % '\n    '.join(map(str, xb_net.get_connections())))

        print("  %s\n      Connections:\n        " % xbee, end='')
        print("%s" % '\n        '.join(map(str, xb_net.get_node_connections(xbee))))
        list = xb_net.get_devices()
        for n in list:
            print("  %s\n      Connections:\n        " % n, end='')
            print("%s" % '\n        '.join(map(str, xb_net.get_node_connections(n))))

    else:
        print("None")


def print_all_routes():
    print("_____________________________Routes:")
    print("       %s" % '\n       '.join(map(str, all_routes)))


def main():
    print(" +----------------------------------------------------------+")
    print(" | XBee Python Library Network modifications Devices Sample |")
    print(" +----------------------------------------------------------+\n")

    global xbee_initializer

    xbee_network = None

    utils.enable_logger("digi.xbee.devices", logging.DEBUG)
    utils.enable_logger("XBeeNetwork", logging.DEBUG)
    utils.enable_logger("digi.xbee.reader", logging.DEBUG)
    utils.enable_logger("digi.xbee.models.zdo", logging.DEBUG)

    xbee_initializer = _XBeeInitializer()

    #xbee = XBeeDevice(PORT, BAUD_RATE)
    #xbee = Raw802Device(PORT, BAUD_RATE)
    xbee = ZigBeeDevice(PORT, BAUD_RATE)
    #xbee = DigiMeshDevice(PORT, BAUD_RATE)

    try:
        xbee.open()

        xbee_initializer.start()

        #xbee.build_aggregate_routes()
        xbee.set_many_to_one_broadcasting_time(0)

        xbee_network = xbee.get_network()

        # Do a network discovery (ND)
        #xbee_network.start_discovery_process(deep=False)
        #while xbee_network.is_discovery_running():
        #    time.sleep(0.5)

        xbee_network.set_discovery_timeout(15)  # 15 seconds.

        xbee_network.set_deep_discovery_options(deep_mode=NeighborDiscoveryMode.CASCADE,
                                                del_not_discovered_nodes_in_last_scan=False)
        xbee_network.set_deep_discovery_timeouts(
            #node_timeout=0,#XBeeNetwork.DEFAULT_MAX_NEIGHBOR_DISCOVERY_TIMEOUT,
            time_bw_requests=XBeeNetwork.DEFAULT_TIME_BETWEEN_REQUESTS,
            time_bw_scans=5)#XBeeNetwork.DEFAULT_TIME_BETWEEN_SCANS)

        xbee_network.add_device_discovered_callback(callback_device_discovered)
        xbee_network.add_discovery_process_finished_callback(callback_discovery_finished)

        xbee_network.add_network_modified_callback(cb_network_modified)

        c = True
        while c:
            print("* Discover remote XBee devices...")

            xbee_network.start_discovery_process(deep=True, n_deep_scans=1)#XBeeNetwork.SCAN_TIL_CANCEL)

            while xbee_network.is_discovery_running():
                time.sleep(1)

            print_nodes(xbee)

            #print(xbee.get_route_to_node(
            #    RemoteZigBeeDevice(xbee,
            #                       XBee64BitAddress.from_hex_string("0013A20040A9E7ED"),
            #                       XBee16BitAddress.from_hex_string("415E"),
            #                       "RT5-PALPATINE")))

            #xbee_initializer.start()
            while not xbee_initializer.is_all_done():
                print("not end!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                time.sleep(1)

            time.sleep(5)
            c = False

        """
        time.sleep(1)

        print("\n* Manually add a new remote XBee device...")
        remote = RemoteXBeeDevice(
            xbee,
            x64bit_addr=XBee64BitAddress.from_hex_string("1234567890ABCDEF"),
            node_id="manually_added")
        xbee_network.add_remote(remote)

        print_nodes(xbee)

        time.sleep(1)

        print("\n* Update the last added remote XBee device...")
        remote = RemoteXBeeDevice(xbee, x64bit_addr=remote.get_64bit_addr(), node_id="updated_node")
        xbee_network.add_remote(remote)

        print_nodes(xbee)

        time.sleep(1)

        print("\n* Manually remove a remote XBee device...")
        xbee_network.remove_device(remote)

        print_nodes(xbee)

        time.sleep(1)

        print("\n* Clear network...")
        xbee_network.clear()

        print_nodes(xbee)
        """

    finally:
        if xbee_initializer.is_running():
            xbee_initializer.stop()
            xbee_initializer.join()

        xbee.set_many_to_one_broadcasting_time(-1)

        print("____________________________________")
        print_all_routes()

        if xbee_network is not None:
            xbee_network.del_discovery_process_finished_callback(callback_discovery_finished)
            xbee_network.del_network_modified_callback(cb_network_modified)

        if xbee is not None and xbee.is_open():
            xbee.close()


if __name__ == '__main__':
    main()
