import logging
import queue
import selectors
import socket
import struct
import threading
from typing import Any, Optional

from asphodel.device_info import DeviceInfo

from .device_command_handler import DeviceCommandHandler

logger = logging.getLogger(__name__)


ASPHODEL_TCP_VERSION = 1
ASPHODEL_TCP_MSG_TYPE_DEVICE_CMD = 0x00
ASPHODEL_TCP_MSG_TYPE_DEVICE_STREAM = 0x01
ASPHODEL_TCP_MSG_TYPE_REMOTE_CMD = 0x02
ASPHODEL_TCP_MSG_TYPE_REMOTE_STREAM = 0x03
ASPHODEL_TCP_MSG_TYPE_REMOTE_NOTIFY = 0x06


def _read_user_tag(nvm: bytes, index: int, length: int) -> bytes:
    b = nvm[index:index + length]
    b = b.split(b'\x00', 1)[0]
    b = b.split(b'\xff', 1)[0]
    return b + b'\x00'


def create_advertisement(serial_number: str, protocol_type: int,
                         device_info: DeviceInfo, connected: bool,
                         remote_device_info: Optional[DeviceInfo]) -> bytes:
    prefix = struct.pack(
        ">BBHHHB", ASPHODEL_TCP_VERSION, connected,
        device_info.max_outgoing_param_length + 2,
        device_info.max_incoming_param_length + 2,
        device_info.stream_packet_length,
        protocol_type)

    serial = serial_number.encode("UTF-8") + b'\x00'
    board_rev = bytes((device_info.board_info[1],))
    board_name = device_info.board_info[0].encode("UTF-8") + b'\x00'
    build_info = device_info.build_info.encode("UTF-8") + b'\x00'
    build_date = device_info.build_date.encode("UTF-8") + b'\x00'

    tag1 = _read_user_tag(device_info.nvm, *device_info.tag_locations[0])
    tag2 = _read_user_tag(device_info.nvm, *device_info.tag_locations[1])

    if remote_device_info:
        remote_bytes = struct.pack(
            ">HHH", remote_device_info.max_incoming_param_length,
            remote_device_info.max_outgoing_param_length,
            remote_device_info.stream_packet_length)
    else:
        remote_bytes = b''

    packet = b''.join((prefix, serial, board_rev, board_name, build_info,
                       build_date, tag1, tag2, remote_bytes))
    return packet


class TCPDevice:
    def __init__(self, device_command_handler: DeviceCommandHandler,
                 remote_command_handler: Optional[DeviceCommandHandler] = None,
                 ) -> None:
        self.device_command_handler = device_command_handler
        self.remote_command_handler = remote_command_handler

        if self.remote_command_handler:
            self.device_command_handler.radio_connect_callback = \
                self._radio_connect_callback
            self.remote_command_handler.remote_restart_callback = \
                self._remote_restart_callback

        self.connected = False
        self.connected_sock: Optional[socket.socket] = None

        # create a TCP socket
        self.listen_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM,
                                         socket.IPPROTO_TCP)
        self.listen_sock.setblocking(False)
        self.listen_sock.bind(("", 0))
        self.listen_sock.listen(1)

        self.selector = selectors.DefaultSelector()
        self.selector.register(self.listen_sock, selectors.EVENT_READ,
                               self._accept_ready)

        # create a UDP socket
        self.udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM,
                                      socket.IPPROTO_UDP)

        # bind the UDP socket so outgoing packets have the TCP port as the src
        self.udp_sock.bind(self.listen_sock.getsockname())

        self.is_finished = threading.Event()
        self.read_buffer = bytearray()
        self.read_thread = threading.Thread(target=self._read_thread_run)
        self.write_thread = threading.Thread(target=self._write_thread_run)
        self.write_queue: queue.Queue[bytes] = queue.Queue()
        self.notifications: list[bytes] = []

        self.read_thread.start()
        self.write_thread.start()

    def __del__(self) -> None:
        self.close()
        self.join()

    def close(self) -> None:
        self.is_finished.set()

        self.listen_sock.close()
        self.udp_sock.close()
        if self.connected_sock:
            self.connected_sock.close()

    def join(self) -> None:
        self.read_thread.join()
        self.write_thread.join()

    def _radio_connect_callback(self, serial_number: Optional[int],
                                bootloader: bool) -> None:
        if serial_number is None:
            self.send_remote_notify_disconnect()
        elif self.remote_command_handler:
            serial_number = self.remote_command_handler.serial_number_int
            protocol_type = self.remote_command_handler.protocol_type
            self.send_remote_notify_connect(serial_number, protocol_type)

    def _remote_restart_callback(self) -> None:
        self.send_remote_notify_disconnect()
        if self.remote_command_handler:
            serial_number = self.remote_command_handler.serial_number_int
            protocol_type = self.remote_command_handler.protocol_type
            self.send_remote_notify_connect(serial_number, protocol_type)

    def send_advertisement(self, address: Any) -> None:
        if self.remote_command_handler:
            remote_device_info = self.remote_command_handler.device_info
        else:
            remote_device_info = None

        packet = create_advertisement(
            self.device_command_handler.serial_number,
            self.device_command_handler.protocol_type,
            self.device_command_handler.device_info, self.connected,
            remote_device_info)

        # send the advertisement
        try:
            self.udp_sock.sendto(packet, address)
        except OSError:
            pass

    def send_stream_packet(self, packet_bytes: bytes) -> None:
        prefix = struct.pack(">HB", len(packet_bytes) + 1,
                             ASPHODEL_TCP_MSG_TYPE_DEVICE_STREAM)
        self.write_queue.put(prefix + packet_bytes)

    def send_remote_stream_packet(self, packet_bytes: bytes) -> None:
        prefix = struct.pack(">HB", len(packet_bytes) + 1,
                             ASPHODEL_TCP_MSG_TYPE_REMOTE_STREAM)
        self.write_queue.put(prefix + packet_bytes)

    def send_remote_notify_connect(self, remote_serial_number: int,
                                   protocol_type: int) -> None:
        self.notifications.append(
            struct.pack(">HBIB", 6, ASPHODEL_TCP_MSG_TYPE_REMOTE_NOTIFY,
                        remote_serial_number, protocol_type))

    def send_remote_notify_disconnect(self) -> None:
        self.notifications.append(
            struct.pack(">HB", 1, ASPHODEL_TCP_MSG_TYPE_REMOTE_NOTIFY))

    def _process_buffer(self, buffer: bytes) -> None:
        if len(buffer) == 0:
            return

        if buffer[0] == ASPHODEL_TCP_MSG_TYPE_DEVICE_CMD:
            reply = self.device_command_handler.handle_command(buffer[1:])
            if reply:
                reply_prefix = struct.pack(">HB", len(reply) + 1,
                                           ASPHODEL_TCP_MSG_TYPE_DEVICE_CMD)
                reply_bytes = reply_prefix + reply
            else:
                reply_bytes = b''
        elif buffer[0] == ASPHODEL_TCP_MSG_TYPE_REMOTE_CMD:
            if not self.remote_command_handler:
                raise Exception("Remote command handler not set")
            reply = self.remote_command_handler.handle_command(buffer[1:])
            if reply:
                reply_prefix = struct.pack(">HB", len(reply) + 1,
                                           ASPHODEL_TCP_MSG_TYPE_REMOTE_CMD)
                reply_bytes = reply_prefix + reply
            else:
                reply_bytes = b''
        else:
            raise Exception("Unknown message type")

        if reply_bytes:
            self.write_queue.put(reply_bytes)

        for notification in self.notifications:
            self.write_queue.put(notification)
        self.notifications.clear()

    def _handle_data(self, data: bytes) -> None:
        self.read_buffer.extend(data)
        while len(self.read_buffer) >= 2:
            length = struct.unpack_from(">H", self.read_buffer, 0)[0]
            if length + 2 <= len(self.read_buffer):
                # have a full buffer
                buffer = bytes(self.read_buffer[2:2 + length])
                self._process_buffer(buffer)
                del self.read_buffer[0:2 + length]
            else:
                break

    def _accept_ready(self) -> None:
        try:
            conn, _addr = self.listen_sock.accept()  # Should be ready
            if self.connected:
                conn.close()
                logger.info("Rejected new connection attempt")
                return

            logger.info("Accepted new connection")

            self.connected = True
            self.connected_sock = conn
            self.connected_sock.setsockopt(
                socket.IPPROTO_TCP, socket.TCP_NODELAY, True)

            self.selector.register(
                self.connected_sock, selectors.EVENT_READ, self._read_ready)
        except OSError:
            pass
        except Exception:
            logger.exception("Unhandled exception in _accept_ready()")

    def _close_connected_socket(self) -> None:
        if self.connected_sock is None:
            return

        self.selector.unregister(self.connected_sock)
        self.connected_sock.close()
        self.connected_sock = None
        self.connected = False
        logger.info("Connection closed")

        # empty queue
        while True:
            try:
                self.write_queue.get(False)
            except queue.Empty:
                break

        # reset the device state
        self.device_command_handler.flush()

    def _read_ready(self) -> None:
        if self.connected_sock is None:
            return

        try:
            data = self.connected_sock.recv(16384)
            if data:
                self._handle_data(data)
            else:
                # socket closed
                self._close_connected_socket()
        except OSError:
            self._close_connected_socket()
        except Exception:
            logger.exception("Unhandled exception in _read_ready()")
            self._close_connected_socket()

    def _read_thread_run(self) -> None:
        while not self.is_finished.is_set():
            events = self.selector.select()
            for key, _mask in events:
                callback = key.data
                callback()

    def _write_thread_run(self) -> None:
        while not self.is_finished.is_set():
            try:
                data = self.write_queue.get(True, 0.1)
                if self.connected_sock:
                    self.connected_sock.send(data)
            except queue.Empty:
                pass
            except OSError:
                pass
