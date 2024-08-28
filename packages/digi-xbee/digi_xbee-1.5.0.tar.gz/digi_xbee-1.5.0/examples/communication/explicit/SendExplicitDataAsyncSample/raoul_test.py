import logging
import sys
import time

from digidevice import xbee

#from digi.xbee.devices import ZigBeeDevice
from digi.xbee.util.utils import enable_logger, int_to_bytes
from digi.xbee.models.atcomm import ATStringCommand
from digi.xbee.models.status import TransmitStatus
from digi.xbee.packets.aft import ApiFrameType
from digi.xbee.packets.common import ExplicitAddressingPacket
from digi.xbee.models.options import TransmitOptions
from digi.xbee.devices import RemoteXBeeDevice
from digi.xbee.models.address import XBee64BitAddress, XBee16BitAddress

REMOTE_NODE_ID = "R"
DATA_TO_SEND = "Hello XBee!"

SOURCE_ENDPOINT = 0xA0
DESTINATION_ENDPOINT = 0xA1
CLUSTER_ID = 0x1554
PROFILE_ID = 0x1234

routes = {}
sent_frame_ids = []


def new_route_cb(src, dest, hops):
    """
    Callback method to handle new received routes.

    Args
        src (:class`digi.xbee.devices.XBeeDevice`): The route source node.
        dest (:class`digi.xbee.devices.RemoteXBeeDevice`): The route
            destination node.
        hops (List): List of intermediate hops, from closest to source to
            closest to destination node.
    """
    routes.update({dest: hops})


def ack_cb(rcv_packet):
    """
    Callback to receive XBee packets. It filters the received packets to
    find the response that corresponds to the sent packet: by id, by
    command (for local or remote AT commands), by socket ID, etc.

    Args:
        rcv_packet (:class:`.XBeePacket`): Received packet.
    """
    if rcv_packet.get_frame_type() != ApiFrameType.TRANSMIT_STATUS:
        return

    if rcv_packet.frame_id not in sent_frame_ids:
        return

    time.sleep(1)
    sent_frame_ids.remove(rcv_packet.frame_id)
    if rcv_packet.transmit_status == TransmitStatus.SUCCESS:
        print("Success transmission for frame ID '%s': %s"
              % (rcv_packet.frame_id, rcv_packet.transmit_status.description))
    else:
        print("Received transmit status for frame ID '%s': %s"
              % (rcv_packet.frame_id, rcv_packet.transmit_status.description))


def get_hops(node):
    hops = routes.get(node, None)
    if hops is not None:
        return hops

    status, route = node.get_local_xbee_device().get_route_to_node(node, timeout=2, force=True)
    if not status:
        print("Could not get route to node %s" % node)
        return None
    if status != TransmitStatus.SUCCESS:
        print("Error getting route to %s :%s" %(node, status.description))
        return None
    if not route or len(route) < 3:
        print("Route for %s not received" % node)
        return None

    return route[2]


def main():
    print(" +--------------------------------------------------------------+")
    print(" | XBee Python Library Send Explicit Data Asynchronously Sample |")
    print(" +--------------------------------------------------------------+\n")

    enable_logger("digi.xbee.devices", logging.DEBUG)
    enable_logger("digi.xbee.reader", logging.DEBUG)
    enable_logger("digi.xbee.sender", logging.DEBUG)
    # enable_logger("digi.xbee.firmware", logging.DEBUG)
    # enable_logger("digi.xbee.profile", logging.DEBUG)
    # enable_logger("digi.xbee.recovery", logging.DEBUG)

    #local_node = ZigBeeDevice(PORT, BAUD_RATE)
    local_node = xbee.get_device()

    try:
        local_node.open()
        #local_node.set_parameter(ATStringCommand.DO, int_to_bytes(0x40), apply=True)

        local_node.add_route_received_callback(new_route_cb)
        local_node.add_packet_received_callback(ack_cb)

        # # Obtain the remote XBee from the XBee network
        # network = local_node.get_network()
        # remote_node = network.discover_device(REMOTE_NODE_ID)
        # print("Sent discovery request")
        # if remote_node is None:
        #     print("Could not find the remote local_xbee")
        #     sys.exit(1)

        # remotes = [RemoteXBeeDevice(local_node,
        #                             x64bit_addr=XBee64BitAddress.from_hex_string("0013A2004195C88B"),
        #                             x16bit_addr=XBee16BitAddress.UNKNOWN_ADDRESS,
        #                             node_id=None),
        #            RemoteXBeeDevice(local_node,
        #                             x64bit_addr=XBee64BitAddress.from_hex_string("0013A2004195C959"),
        #                             x16bit_addr=XBee16BitAddress.UNKNOWN_ADDRESS,
        #                             node_id=None),
        #            RemoteXBeeDevice(local_node,
        #                             x64bit_addr=XBee64BitAddress.from_hex_string("0013A2004195C88C"),
        #                             x16bit_addr=XBee16BitAddress.UNKNOWN_ADDRESS,
        #                             node_id=None)]

        network = local_node.get_network()
        # discover network...
        remotes = network.get_devices()

        for remote_node in remotes:
            # Get the cached route if any, otherwise force to get it
            #route = get_hops(remote_node)
            route = routes.get(remote_node, None)

            # Create the source route before sending data
            if route is not None:
                local_node.create_source_route(remote_node, route)

            # Send the packet
            frame_id = local_node.get_next_frame_id()
            print("Sending to %s (frame ID %s)" % (remote_node, frame_id))
            local_node.send_packet(
                ExplicitAddressingPacket(frame_id, remote_node.get_64bit_addr(),
                                         remote_node.get_16bit_addr(), SOURCE_ENDPOINT,
                                         DESTINATION_ENDPOINT, CLUSTER_ID, PROFILE_ID,
                                         broadcast_radius=0,
                                         transmit_options=TransmitOptions.NONE.value,
                                         rf_data=DATA_TO_SEND.encode(encoding="utf8", errors='ignore')))
            print("Sent to %s (frame ID %s)" % (remote_node, frame_id))

            sent_frame_ids.append(frame_id)

        while sent_frame_ids:
            time.sleep(1)



    finally:
        if local_node is not None and local_node.is_open():
            local_node.close()


if __name__ == '__main__':
    main()
