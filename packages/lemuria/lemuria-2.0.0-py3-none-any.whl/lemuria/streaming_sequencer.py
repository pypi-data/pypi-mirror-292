import logging
import lzma
import struct
import time
import threading
from typing import Callable, cast, Optional

from .device_command_handler import DeviceCommandHandler

logger = logging.getLogger(__name__)


class StreamingSequencer:
    def __init__(self, file_times: dict[float, str], start_time: float,
                 device_command_handler: DeviceCommandHandler,
                 send_stream_packet: Callable[[bytes], None]) -> None:
        self.file_times = file_times
        self.start_time = start_time
        self.device_command_handler = device_command_handler
        self.send_stream_packet = send_stream_packet

        self.device_command_handler.stream_state_callback = \
            self.stream_state_callback

        self.is_finished = threading.Event()
        self.streaming_started = threading.Event()
        self.streaming_stopped = threading.Event()
        self.stream_thread = threading.Thread(target=self._stream_thread_run)
        self.stream_thread.start()

        self.file_lock = threading.Lock()
        self.current_file: Optional[lzma.LZMAFile] = None
        self.next_packet_timestamp: Optional[float] = None
        self.next_packet_bytes: Optional[bytes] = None

        self.streaming = False

        self._setup_streaming()

    def close(self) -> None:
        self.is_finished.set()

        # set both events to force _stream_thread_run to wake up
        self.streaming_started.set()
        self.streaming_stopped.set()

    def join(self) -> None:
        self.stream_thread.join()

    def _start_streaming(self) -> None:
        self.streaming = True
        logger.debug("Starting streaming")
        self.stream_start_time = time.monotonic()
        self.streaming_stopped.clear()
        self.streaming_started.set()

    def _stop_streaming(self) -> None:
        self.streaming = False
        logger.debug("Stopping streaming")
        self.streaming_started.clear()
        self.streaming_stopped.set()
        self._setup_streaming()

    def stream_state_callback(self, index: int, enable: bool,
                              warmup: bool) -> None:
        any_running = any(self.device_command_handler.stream_enable_status)

        if enable:
            if any_running and not self.streaming:
                # starting our first stream
                self._start_streaming()
        else:
            if not any_running and self.streaming:
                # stopping our last stream
                self._stop_streaming()

    def _setup_streaming(self) -> None:
        with self.file_lock:
            self.remaining_timestamps = sorted(self.file_times.keys())
            timestamp = self.remaining_timestamps.pop(0)
            filename = self.file_times[timestamp]

            self.next_packet_timestamp = None
            self.next_packet_bytes = None

            if self.current_file:
                self.current_file.close()
                self.current_file = None

            self._open_file(filename, timestamp)
            if self.current_file is None:
                self._open_next_file()

    def _open_file(self, filename: str, timestamp: float) -> None:
        logger.debug("Opening file %s", filename)

        lzmafile = lzma.LZMAFile(filename, "rb")

        # skip over the header (since it's already been processed)
        header_leader = struct.unpack(">dI", lzmafile.read(12))
        _ = lzmafile.read(header_leader[1])  # header_bytes

        packet_leader = struct.Struct(">dI")

        if timestamp < self.start_time:
            while True:
                leader_bytes = lzmafile.read(packet_leader.size)
                if not leader_bytes or len(leader_bytes) != packet_leader.size:
                    logger.debug("Finished file")
                    lzmafile.close()
                    return  # file is finished

                leader = packet_leader.unpack(leader_bytes)
                packet_timestamp = leader[0]
                packet_length = leader[1]
                packet_bytes = lzmafile.read(packet_length)
                if not packet_bytes or len(packet_bytes) != packet_length:
                    logger.debug("Finished file")
                    lzmafile.close()
                    return  # file is finished

                if self.start_time < packet_timestamp:
                    # start streaming from this packet
                    self.next_packet_timestamp = packet_timestamp
                    self.next_packet_bytes = packet_bytes
                    break
        self.current_file = lzmafile

    def _open_next_file(self) -> None:
        while self.current_file is None:
            try:
                timestamp = self.remaining_timestamps.pop(0)
            except IndexError:
                # hit the end of all of the files
                return
            filename = self.file_times[timestamp]
            self._open_file(filename, timestamp)

    def _process_packets(self, timestamp: float) -> None:
        if self.current_file is None:
            return

        if self.next_packet_timestamp is not None:
            if self.next_packet_timestamp <= timestamp:
                # logger.debug("sending stashed packet %s",
                #              timestamp - self.next_packet_timestamp)
                self.send_stream_packet(cast(bytes, self.next_packet_bytes))
                self.next_packet_timestamp = None
                self.next_packet_bytes = None
            else:
                # not time to send this yet
                # logger.debug("stash not ready %s",
                #              timestamp - self.next_packet_timestamp)
                return

        packet_leader = struct.Struct(">dI")
        while True:
            leader_bytes = self.current_file.read(packet_leader.size)
            if not leader_bytes or len(leader_bytes) != packet_leader.size:
                logger.debug("Finished file")
                self.current_file.close()
                self.current_file = None
                return  # file is finished

            leader = packet_leader.unpack(leader_bytes)
            packet_timestamp = leader[0]
            packet_length = leader[1]
            packet_bytes = self.current_file.read(packet_length)
            if not packet_bytes or len(packet_bytes) != packet_length:
                logger.debug("Finished file")
                self.current_file.close()
                self.current_file = None
                return  # file is finished

            if packet_timestamp <= timestamp:
                # logger.debug("sending packet %s",
                #              timestamp - packet_timestamp)
                self.send_stream_packet(packet_bytes)
            else:
                # not time for this packet yet
                # logger.debug("not ready %s", timestamp - packet_timestamp)
                self.next_packet_timestamp = packet_timestamp
                self.next_packet_bytes = packet_bytes
                break

    def _stream_thread_run(self) -> None:
        while not self.is_finished.is_set():
            # wait for streaming to start
            self.streaming_started.wait()

            if self.is_finished.is_set():
                # close() was called
                return

            logger.debug("Streaming beginning")

            while not self.streaming_stopped.is_set():
                now = time.monotonic()
                timestamp = self.start_time + (now - self.stream_start_time)

                with self.file_lock:
                    if self.current_file is not None:
                        self._process_packets(timestamp)
                    else:
                        self._open_next_file()
                        if self.current_file is None:
                            break

                if self.next_packet_timestamp is not None:
                    delay = self.next_packet_timestamp - timestamp
                    self.streaming_stopped.wait(delay)

            logger.debug("Streaming finished")
            self.streaming_stopped.wait()
