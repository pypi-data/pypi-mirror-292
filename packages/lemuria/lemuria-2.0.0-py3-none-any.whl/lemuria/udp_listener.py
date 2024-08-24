import logging
import select
import socket
import struct
import sys
import threading
from typing import Optional

from .tcp_device import TCPDevice

logger = logging.getLogger(__name__)


ASPHODEL_MULTICAST_ADDRESS = "224.0.6.150"
ASPHODEL_MULTICAST_PORT = 5760


class UDPListener:
    def __init__(self, iface: Optional[str] = None):
        self.devices: list[TCPDevice] = []
        self.device_lock = threading.Lock()

        self.is_finished = threading.Event()
        self.thread = threading.Thread(target=self.thread_run)

        self.create_socket(iface)

        self.thread.start()

    def __del__(self) -> None:
        self.close()
        self.join()

    def create_socket(self, iface: Optional[str]) -> None:
        # create a UDP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM,
                                  socket.IPPROTO_UDP)

        # allow port reuse
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if sys.platform != "win32":
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

        # bind to multicast address and port
        self.sock.bind((iface if iface else "", ASPHODEL_MULTICAST_PORT))

        # join the IGMP group and let the NIC know to pick up the packets
        group = socket.inet_aton(ASPHODEL_MULTICAST_ADDRESS)
        if iface is None:
            mreq = struct.pack("4sl", group, socket.INADDR_ANY)
        else:
            mreq = struct.pack("4s4s", group, socket.inet_aton(iface))
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    def add_device(self, device: TCPDevice) -> None:
        with self.device_lock:
            self.devices.append(device)

    def remove_device(self, device: TCPDevice) -> None:
        with self.device_lock:
            self.devices.remove(device)

    def thread_run(self) -> None:
        while not self.is_finished.is_set():
            try:
                ready, _, _ = select.select([self.sock], [], [])
                if ready:
                    _data, address = self.sock.recvfrom(4096)
                    logger.debug("Got multicast packet")
                    with self.device_lock:
                        for device in self.devices:
                            device.send_advertisement(address)
            except OSError:
                pass
            except Exception:
                logger.exception("unhandled exception in thread_run")

    def close(self) -> None:
        self.is_finished.set()
        self.sock.close()

    def join(self) -> None:
        self.thread.join()
