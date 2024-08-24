import argparse
import logging
import time
from typing import cast, Optional

from asphodel import apdparse
from asphodel.device_info import DeviceInfo

from . import protocol
from lemuria.device_command_handler import DeviceCommandHandler, ScanResult
from lemuria.streaming_sequencer import StreamingSequencer
from lemuria.tcp_device import TCPDevice
from lemuria.udp_listener import UDPListener

logger = logging.getLogger(__name__)


def main() -> None:
    logging.basicConfig(format='%(levelname)s:%(message)s',
                        level=logging.DEBUG)

    parser = argparse.ArgumentParser()
    parser.add_argument("files", type=argparse.FileType("rb"), nargs='+',
                        metavar='file')
    parser.add_argument(
        "--offset", type=float, metavar='time', dest="offset",
        help="offset in seconds from start of first file")
    parser.add_argument(
        "-s", "--serial", metavar='sn', dest="serial",
        help="override serial number of main device")
    parser.add_argument(
        "--radio-file", metavar='apd', dest="radio_file",
        help="create a radio device (i.e. WMR) with remote as the main device")
    parser.add_argument(
        "--radio-serial", metavar='sn', dest="radio_serial",
        help="override serial number of radio device")

    args = parser.parse_args()

    file_times, header = apdparse.load_batch(f.name for f in args.files)

    offset = cast(Optional[float], args.offset)
    if offset is None:
        offset = 0.0
    start_time = min(file_times.keys()) + offset

    device_info = DeviceInfo.from_apd_header(header)

    serial_number = args.serial
    if not serial_number:
        serial_number = header["serial_number"]

    if args.radio_file:
        _, radio_header = apdparse.load_batch([args.radio_file])
        radio_serial_number = args.radio_serial
        if not radio_serial_number:
            radio_serial_number = radio_header["serial_number"]
        radio_device_info = DeviceInfo.from_apd_header(radio_header)

        remote_command_handler = DeviceCommandHandler(
            serial_number, protocol.ASPHODEL_PROTOCOL_TYPE_REMOTE, device_info)

        scan_results = [ScanResult(
            remote_command_handler.serial_number_int, False,
            protocol.ASPHODEL_PROTOCOL_TYPE_REMOTE, 0, -15)]

        radio_command_handler = DeviceCommandHandler(
            radio_serial_number, protocol.ASPHODEL_PROTOCOL_TYPE_RADIO,
            radio_device_info, scan_results)
        tcp_device = TCPDevice(radio_command_handler, remote_command_handler)
        sequencer = StreamingSequencer(
            file_times, start_time, remote_command_handler,
            tcp_device.send_remote_stream_packet)
    else:
        main_command_handler = DeviceCommandHandler(
            serial_number, protocol.ASPHODEL_PROTOCOL_TYPE_BASIC, device_info)
        tcp_device = TCPDevice(main_command_handler)
        sequencer = StreamingSequencer(
            file_times, start_time, main_command_handler,
            tcp_device.send_stream_packet)

    udp_listener = UDPListener()
    udp_listener.add_device(tcp_device)

    try:
        while True:
            time.sleep(1)
    finally:
        udp_listener.close()
        sequencer.close()
        tcp_device.close()
        udp_listener.join()
        sequencer.join()
        tcp_device.join()


if __name__ == '__main__':
    main()
