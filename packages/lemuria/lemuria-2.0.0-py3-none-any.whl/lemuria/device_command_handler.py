import binascii
from dataclasses import dataclass
import enum
import re
import struct
from typing import Callable, cast, Optional

from asphodel.device_info import DeviceInfo

from . import protocol


RGBCallback = Callable[[int, tuple[int, int, int], bool], None]
LEDCallback = Callable[[int, int, bool], None]
StreamStateCallback = Callable[[int, bool, bool], None]
CtrlVarCallback = Callable[[int, int], None]
RadioConnectCallback = Callable[[Optional[int], bool], None]
RemoteRestartCallback = Callable[[], None]


class DeviceError(Exception):
    def __init__(self, error_code: int) -> None:
        self.error_code = error_code


def get_numeric_serial(serial_number: str) -> int:
    matches = re.findall(r'\d+', serial_number)
    return int(matches[-1]) if matches else 0


@dataclass()
class ScanResult:
    serial_number: int
    bootloader: bool
    protocol_type: int
    device_mode: int
    scan_strength: int


@enum.unique
class RadioState(enum.Enum):
    STOPPED = enum.auto()
    SCANNING_APP = enum.auto()
    SCANNING_BOOT = enum.auto()
    CONNECTED_APP = enum.auto()
    CONNECTED_BOOT = enum.auto()


class DeviceCommandHandler:
    def __init__(self, serial_number: str,
                 protocol_type: int,
                 device_info: DeviceInfo,
                 scan_results: Optional[list[ScanResult]] = None,
                 initial_rgb_values: Optional[
                     list[tuple[int, int, int]]] = None,
                 initial_led_values: Optional[list[int]] = None) -> None:
        self.device_info = device_info
        self.serial_number = serial_number
        self.protocol_type = protocol_type
        self.scan_results = scan_results or []

        self.radio_implemented = (self.protocol_type &
                                  protocol.ASPHODEL_PROTOCOL_TYPE_RADIO) != 0
        self.remote_implemented = (self.protocol_type &
                                   protocol.ASPHODEL_PROTOCOL_TYPE_REMOTE) != 0

        self.serial_number_int = get_numeric_serial(serial_number)
        if self.serial_number_int == 0:
            raise ValueError("Invalid serial number")

        # callbacks for use by external code
        self.rgb_callback: Optional[RGBCallback] = None
        self.led_callback: Optional[LEDCallback] = None
        self.stream_state_callback: Optional[StreamStateCallback] = None
        self.ctrl_var_callback: Optional[CtrlVarCallback] = None
        self.radio_connect_callback: Optional[RadioConnectCallback] = None
        self.remote_restart_callback: Optional[RemoteRestartCallback] = None

        # states
        self.stream_enable_status = [False] * len(self.device_info.streams)
        self.stream_warmup_status = [False] * len(self.device_info.streams)
        self.radio_state = RadioState.STOPPED
        self.connected_serial_number: Optional[int] = None
        self.remaining_scan_results: list[ScanResult] = []

        if initial_rgb_values is not None:
            if len(initial_rgb_values) != len(self.device_info.rgb_settings):
                raise ValueError(
                    "Initial RGB list not the same length as device info list")
            self.initial_rgb_values = initial_rgb_values
        else:
            self.initial_rgb_values = [(255, 0, 0)] * len(
                self.device_info.rgb_settings)

        if initial_led_values is not None:
            if len(initial_led_values) != len(self.device_info.led_settings):
                raise ValueError(
                    "Initial LED list not the same length as device info list")
            self.initial_led_values = initial_led_values
        else:
            self.initial_led_values = [0] * len(self.device_info.led_settings)

    def _update_rgb(self, index: int, new_value: tuple[int, int, int],
                    instant: bool) -> None:
        self.device_info.rgb_settings[index] = new_value
        if self.rgb_callback is not None:
            self.rgb_callback(index, new_value, instant)

    def _update_led(self, index: int, new_value: int, instant: bool) -> None:
        self.device_info.led_settings[index] = new_value
        if self.led_callback is not None:
            self.led_callback(index, new_value, instant)

    def _stream_set_enable(self, index: int, enable: bool) -> None:
        old_enable = self.stream_enable_status[index]
        if old_enable != enable:
            self.stream_enable_status[index] = enable
            if self.stream_state_callback is not None:
                self.stream_state_callback(
                    index, enable, self.stream_warmup_status[index])

    def _stream_set_warm_up(self, index: int, enable: bool) -> None:
        old_enable = self.stream_warmup_status[index]
        if old_enable != enable:
            self.stream_warmup_status[index] = enable
            if self.stream_state_callback is not None:
                self.stream_state_callback(
                    index, self.stream_enable_status[index], enable)

    def _channel_specific(self, index: int, cmd: int, params: bytes) -> bytes:
        # TODO: implement this as a callback
        raise DeviceError(protocol.ERROR_CODE_UNIMPLEMENTED_COMMAND)

    def _restart_remote(self) -> None:
        if self.remote_restart_callback is not None:
            self.remote_restart_callback()

    def _update_ctrl_var(self, index: int, value: int) -> None:
        old_tuple = self.device_info.ctrl_vars[index]
        if old_tuple[2] != value:
            new_tuple = (old_tuple[0], old_tuple[1], value)
            self.device_info.ctrl_vars[index] = new_tuple
            if self.ctrl_var_callback is not None:
                self.ctrl_var_callback(index, value)

    def _radio_stop(self) -> None:
        old_state = self.radio_state
        self.radio_state = RadioState.STOPPED
        self.connected_serial_number = None

        if self.radio_connect_callback is not None:
            if old_state == RadioState.CONNECTED_APP:
                self.radio_connect_callback(None, False)
            elif old_state == RadioState.CONNECTED_BOOT:
                self.radio_connect_callback(None, True)

    def _radio_connect(self, serial_number: int, bootloader: bool) -> None:
        self._radio_stop()

        if not bootloader:
            self.radio_state = RadioState.CONNECTED_APP
        else:
            self.radio_state = RadioState.CONNECTED_BOOT
        self.connected_serial_number = serial_number

        if self.radio_connect_callback is not None:
            self.radio_connect_callback(serial_number, bootloader)

    def _radio_start_scan(self, bootloader: bool) -> None:
        self._radio_stop()

        if not bootloader:
            self.radio_state = RadioState.SCANNING_APP
        else:
            self.radio_state = RadioState.SCANNING_BOOT

        filtered = []
        for scan_result in self.scan_results:
            if scan_result.bootloader == bootloader:
                filtered.append(scan_result)

        self.remaining_scan_results = filtered

    def _get_radio_scan_power(self, serial_number: int) -> bytes:
        for scan_result in self.scan_results:
            if scan_result.serial_number == serial_number:
                return struct.pack(">b", scan_result.scan_strength)
        return b'\x7F'  # not found

    def _get_scan_results(self, max_results: int) -> list[ScanResult]:
        return_results = self.remaining_scan_results[:max_results]
        self.remaining_scan_results = self.remaining_scan_results[max_results:]
        return return_results

    def _get_radio_status(self) -> tuple[bool, int, int, bool]:
        if self.radio_state == RadioState.STOPPED:
            return (False, 0, 0, False)
        elif (self.radio_state == RadioState.SCANNING_APP or
              self.radio_state == RadioState.SCANNING_BOOT):
            return (False, 0, 0, True)
        elif (self.radio_state == RadioState.CONNECTED_APP or
              self.radio_state == RadioState.CONNECTED_BOOT):
            serial_number = self.connected_serial_number or 0
            for scan_result in self.scan_results:
                if scan_result.serial_number == serial_number:
                    protocol_type = scan_result.protocol_type
                    break
            else:
                protocol_type = protocol.ASPHODEL_PROTOCOL_TYPE_REMOTE
            return (True, serial_number, protocol_type, False)
        else:
            raise Exception("Unknown radio state")

    def flush(self) -> None:
        for i in range(len(self.device_info.streams)):
            self._stream_set_enable(i, False)
            self._stream_set_warm_up(i, False)
        for i, rgb_value in enumerate(self.initial_rgb_values):
            self._update_rgb(i, rgb_value, True)
        for i, led_value in enumerate(self.initial_led_values):
            self._update_led(i, led_value, True)
        # TODO: packet queue empty

    def _handle_command_internal(self, cmd: int, params: bytes) -> bytes:
        if cmd == protocol.CMD_GET_PROTOCOL_VERSION:
            if len(params) != 0:
                raise DeviceError(protocol.ERROR_CODE_BAD_CMD_LENGTH)
            return bytes((protocol.ASPHODEL_PROTOCOL_VERSION_MAJOR,
                          (protocol.ASPHODEL_PROTOCOL_VERSION_MINOR << 4) |
                          protocol.ASPHODEL_PROTOCOL_VERSION_SUBMINOR))
        elif cmd == protocol.CMD_GET_BOARD_INFO:
            if len(params) != 0:
                raise DeviceError(protocol.ERROR_CODE_BAD_CMD_LENGTH)
            board_rev = bytes((self.device_info.board_info[1],))
            board_name = self.device_info.board_info[0].encode("UTF-8")
            return board_rev + board_name
        elif cmd == protocol.CMD_GET_USER_TAG_LOCATIONS:
            if len(params) != 0:
                raise DeviceError(protocol.ERROR_CODE_BAD_CMD_LENGTH)
            flat = (i // 4 for t in self.device_info.tag_locations for i in t)
            return struct.pack(">6H", *flat)
        elif cmd == protocol.CMD_GET_BUILD_INFO:
            if len(params) != 0:
                raise DeviceError(protocol.ERROR_CODE_BAD_CMD_LENGTH)
            return self.device_info.build_info.encode("UTF-8")
        elif cmd == protocol.CMD_GET_BUILD_DATE:
            if len(params) != 0:
                raise DeviceError(protocol.ERROR_CODE_BAD_CMD_LENGTH)
            return self.device_info.build_date.encode("UTF-8")
        elif cmd == protocol.CMD_GET_CHIP_FAMILY:
            if len(params) != 0:
                raise DeviceError(protocol.ERROR_CODE_BAD_CMD_LENGTH)
            return self.device_info.chip_family.encode("UTF-8")
        elif cmd == protocol.CMD_GET_CHIP_MODEL:
            if len(params) != 0:
                raise DeviceError(protocol.ERROR_CODE_BAD_CMD_LENGTH)
            return self.device_info.chip_model.encode("UTF-8")
        elif cmd == protocol.CMD_GET_CHIP_ID:
            if len(params) != 0:
                raise DeviceError(protocol.ERROR_CODE_BAD_CMD_LENGTH)
            return binascii.a2b_hex(self.device_info.chip_id)
        elif cmd == protocol.CMD_GET_NVM_SIZE:
            if len(params) != 0:
                raise DeviceError(protocol.ERROR_CODE_BAD_CMD_LENGTH)
            return struct.pack(">H", len(self.device_info.nvm) // 4)
        elif cmd == protocol.CMD_ERASE_NVM:
            if len(params) != 0:
                raise DeviceError(protocol.ERROR_CODE_BAD_CMD_LENGTH)
            self.device_info.nvm = b'\xff' * len(self.device_info.nvm)
        elif cmd == protocol.CMD_WRITE_NVM:
            if len(params) < 6 or len(params) % 4 != 2:
                raise DeviceError(protocol.ERROR_CODE_BAD_CMD_LENGTH)
            byte_address = struct.unpack(">H", params[0:2])[0] * 4
            if byte_address + len(params) - 2 > len(self.device_info.nvm):
                raise DeviceError(protocol.ERROR_CODE_BAD_CMD_LENGTH)

            nvm_buffer = bytearray(self.device_info.nvm)
            nvm_buffer[byte_address:byte_address + len(params) - 2] = \
                params[2:]
            self.device_info.nvm = bytes(nvm_buffer)
        elif cmd == protocol.CMD_READ_NVM:
            if len(params) != 2:
                raise DeviceError(protocol.ERROR_CODE_BAD_ADDRESS)
            byte_address = struct.unpack(">H", params)[0] * 4
            if byte_address >= len(self.device_info.nvm):
                raise DeviceError(protocol.ERROR_CODE_BAD_CMD_LENGTH)

            # round down to multiple of 4
            bytes_to_read = (
                self.device_info.max_outgoing_param_length // 4) * 4

            return self.device_info.nvm[
                byte_address:byte_address + bytes_to_read]
        elif cmd == protocol.CMD_FLUSH:
            if len(params) != 0:
                raise DeviceError(protocol.ERROR_CODE_BAD_CMD_LENGTH)
            self.flush()
        elif cmd == protocol.CMD_GET_BOOTLOADER_INFO:
            if len(params) != 0:
                raise DeviceError(protocol.ERROR_CODE_BAD_CMD_LENGTH)
            return b''  # bootloader not supported
        elif cmd == protocol.CMD_GET_RGB_COUNT:
            if len(params) != 0:
                raise DeviceError(protocol.ERROR_CODE_BAD_CMD_LENGTH)
            return bytes((len(self.device_info.rgb_settings),))
        elif cmd == protocol.CMD_GET_RGB_VALUES:
            if len(params) != 1:
                raise DeviceError(protocol.ERROR_CODE_BAD_CMD_LENGTH)
            index = params[0]
            return bytes(self.device_info.rgb_settings[index])
        elif cmd == protocol.CMD_SET_RGB:
            if len(params) != 4:
                raise DeviceError(protocol.ERROR_CODE_BAD_CMD_LENGTH)
            self._update_rgb(
                params[0], cast(tuple[int, int, int], tuple(params[1:])),
                False)
        elif cmd == protocol.CMD_SET_RGB_INSTANT:
            if len(params) != 4:
                raise DeviceError(protocol.ERROR_CODE_BAD_CMD_LENGTH)
            self._update_rgb(
                params[0], cast(tuple[int, int, int], tuple(params[1:])),
                True)
        elif cmd == protocol.CMD_GET_LED_COUNT:
            if len(params) != 0:
                raise DeviceError(protocol.ERROR_CODE_BAD_CMD_LENGTH)
            return bytes((len(self.device_info.led_settings),))
        elif cmd == protocol.CMD_GET_LED_VALUE:
            if len(params) != 1:
                raise DeviceError(protocol.ERROR_CODE_BAD_CMD_LENGTH)
            index = params[0]
            return bytes((self.device_info.led_settings[index],))
        elif cmd == protocol.CMD_SET_LED:
            if len(params) != 2:
                raise DeviceError(protocol.ERROR_CODE_BAD_CMD_LENGTH)
            self._update_led(params[0], params[1], False)
        elif cmd == protocol.CMD_SET_LED_INSTANT:
            if len(params) != 2:
                raise DeviceError(protocol.ERROR_CODE_BAD_CMD_LENGTH)
            self._update_led(params[0], params[1], True)
        elif cmd == protocol.CMD_GET_STREAM_COUNT_AND_ID:
            if len(params) != 0:
                raise DeviceError(protocol.ERROR_CODE_BAD_CMD_LENGTH)
            return bytes((len(self.device_info.streams),
                          self.device_info.stream_filler_bits,
                          self.device_info.stream_id_bits))
        elif cmd == protocol.CMD_GET_STREAM_CHANNELS:
            if len(params) != 1:
                raise DeviceError(protocol.ERROR_CODE_BAD_CMD_LENGTH)
            stream = self.device_info.streams[params[0]]
            channels = stream.channel_index_list[:stream.channel_count]
            return bytes(channels)
        elif cmd == protocol.CMD_GET_STREAM_FORMAT:
            if len(params) != 1:
                raise DeviceError(protocol.ERROR_CODE_BAD_CMD_LENGTH)
            stream = self.device_info.streams[params[0]]
            return struct.pack(
                ">BBfff", stream.filler_bits, stream.counter_bits, stream.rate,
                stream.rate_error, stream.warm_up_delay)
        elif cmd == protocol.CMD_ENABLE_STREAM:
            if len(params) != 2:
                raise DeviceError(protocol.ERROR_CODE_BAD_CMD_LENGTH)
            self._stream_set_enable(params[0], bool(params[1]))
        elif cmd == protocol.CMD_WARM_UP_STREAM:
            if len(params) != 2:
                raise DeviceError(protocol.ERROR_CODE_BAD_CMD_LENGTH)
            self._stream_set_warm_up(params[0], bool(params[1]))
        elif cmd == protocol.CMD_GET_STREAM_STATUS:
            if len(params) != 1:
                raise DeviceError(protocol.ERROR_CODE_BAD_CMD_LENGTH)
            return bytes([self.stream_enable_status[params[0]],
                          self.stream_warmup_status[params[0]]])
        elif cmd == protocol.CMD_GET_STREAM_RATE_INFO:
            # TODO: implement!
            raise DeviceError(protocol.ERROR_CODE_UNIMPLEMENTED_COMMAND)
        elif cmd == protocol.CMD_GET_CHANNEL_COUNT:
            if len(params) != 0:
                raise DeviceError(protocol.ERROR_CODE_BAD_CMD_LENGTH)
            return bytes((len(self.device_info.channels),))
        elif cmd == protocol.CMD_GET_CHANNEL_NAME:
            if len(params) != 1:
                raise DeviceError(protocol.ERROR_CODE_BAD_CMD_LENGTH)
            channel = self.device_info.channels[params[0]]
            return channel.name
        elif cmd == protocol.CMD_GET_CHANNEL_INFO:
            if len(params) != 1:
                raise DeviceError(protocol.ERROR_CODE_BAD_CMD_LENGTH)
            channel = self.device_info.channels[params[0]]
            return struct.pack(
                ">BBHHBhfffB", channel.channel_type, channel.unit_type,
                channel.filler_bits, channel.data_bits, channel.samples,
                channel.bits_per_sample, channel.minimum, channel.maximum,
                channel.resolution, channel.chunk_count)
        elif cmd == protocol.CMD_GET_CHANNEL_COEFFICIENTS:
            if len(params) not in (1, 2):
                raise DeviceError(protocol.ERROR_CODE_BAD_CMD_LENGTH)
            channel = self.device_info.channels[params[0]]
            if len(params) == 2:
                start_index = params[1]
            else:
                start_index = 0
            if start_index > channel.coefficients_length:
                raise DeviceError(protocol.ERROR_CODE_BAD_INDEX)
            length = channel.coefficients_length - start_index
            max_send = self.device_info.max_outgoing_param_length // 4
            if length > max_send:
                length = max_send
            c = channel.coefficients[start_index:start_index + length]
            return struct.pack(">{}f".format(length), *c)
        elif cmd == protocol.CMD_GET_CHANNEL_CHUNK:
            if len(params) != 2:
                raise DeviceError(protocol.ERROR_CODE_BAD_CMD_LENGTH)
            channel = self.device_info.channels[params[0]]
            chunk_number = params[1]
            if chunk_number >= channel.chunk_count:
                raise DeviceError(protocol.ERROR_CODE_BAD_INDEX)
            chunk_length = channel.chunk_lengths[chunk_number]
            chunk = channel.chunks[chunk_number][:chunk_length]
            return bytes(chunk)
        elif cmd == protocol.CMD_CHANNEL_SPECIFIC:
            if len(params) < 2:
                raise DeviceError(protocol.ERROR_CODE_BAD_CMD_LENGTH)
            index = params[0]
            channel_cmd = params[1]
            if index >= len(self.device_info.channels):
                raise DeviceError(protocol.ERROR_CODE_BAD_INDEX)
            return self._channel_specific(index, channel_cmd, params[2:])
        elif cmd == protocol.CMD_GET_SUPPLY_COUNT:
            if len(params) != 0:
                raise DeviceError(protocol.ERROR_CODE_BAD_CMD_LENGTH)
            return bytes((len(self.device_info.supplies),))
        elif cmd == protocol.CMD_GET_SUPPLY_NAME:
            if len(params) != 1:
                raise DeviceError(protocol.ERROR_CODE_BAD_CMD_LENGTH)
            supply_name = self.device_info.supplies[params[0]][0]
            return supply_name.encode("UTF-8")
        elif cmd == protocol.CMD_GET_SUPPLY_INFO:
            if len(params) != 1:
                raise DeviceError(protocol.ERROR_CODE_BAD_CMD_LENGTH)
            supply_info = self.device_info.supplies[params[0]][1]
            return struct.pack(
                ">BBiff", supply_info.unit_type, supply_info.is_battery,
                supply_info.nominal, supply_info.scale, supply_info.offset)
        elif cmd == protocol.CMD_CHECK_SUPPLY:
            if len(params) != 1:
                raise DeviceError(protocol.ERROR_CODE_BAD_CMD_LENGTH)
            supply_result = self.device_info.supply_results[params[0]]
            if supply_result is None:
                # supply not checked in the device info, make it up
                supply_info = self.device_info.supplies[params[0]][1]
                supply_result = (supply_info.nominal, 0)
            return struct.pack(">iB", supply_result[0], supply_result[1])
        elif cmd == protocol.CMD_GET_CTRL_VAR_COUNT:
            if len(params) != 0:
                raise DeviceError(protocol.ERROR_CODE_BAD_CMD_LENGTH)
            return bytes((len(self.device_info.ctrl_vars),))
        elif cmd == protocol.CMD_GET_CTRL_VAR_NAME:
            if len(params) != 1:
                raise DeviceError(protocol.ERROR_CODE_BAD_CMD_LENGTH)
            ctrl_var_name = self.device_info.ctrl_vars[params[0]][0]
            return ctrl_var_name.encode("UTF-8")
        elif cmd == protocol.CMD_GET_CTRL_VAR_INFO:
            if len(params) != 1:
                raise DeviceError(protocol.ERROR_CODE_BAD_CMD_LENGTH)
            ctrl_var_info = self.device_info.ctrl_vars[params[0]][1]
            return struct.pack(
                ">Biiff", ctrl_var_info.unit_type, ctrl_var_info.minimum,
                ctrl_var_info.maximum, ctrl_var_info.scale,
                ctrl_var_info.offset)
        elif cmd == protocol.CMD_GET_CTRL_VAR:
            if len(params) != 1:
                raise DeviceError(protocol.ERROR_CODE_BAD_CMD_LENGTH)
            ctrl_var_value = self.device_info.ctrl_vars[params[0]][2]
            if ctrl_var_value is None:
                # ctrl var not set in the device info, make it up
                ctrl_var_info = self.device_info.ctrl_vars[params[0]][1]
                ctrl_var_value = ctrl_var_info.minimum
            return struct.pack(">i", ctrl_var_value)
        elif cmd == protocol.CMD_SET_CTRL_VAR:
            if len(params) != 5:
                raise DeviceError(protocol.ERROR_CODE_BAD_CMD_LENGTH)
            new_value = cast(int, struct.unpack(">i", params[1:])[0])
            ctrl_var_tuple = self.device_info.ctrl_vars[params[0]]
            new_ctrl_var_tuple = (ctrl_var_tuple[0], ctrl_var_tuple[1],
                                  new_value)
            self.device_info.ctrl_vars[params[0]] = new_ctrl_var_tuple
            self._update_ctrl_var(params[0], new_value)
        elif cmd == protocol.CMD_GET_SETTING_COUNT:
            if len(params) != 0:
                raise DeviceError(protocol.ERROR_CODE_BAD_CMD_LENGTH)
            return b'\x00'  # TODO: implement
        elif cmd == protocol.CMD_GET_SETTING_NAME:
            raise DeviceError(protocol.ERROR_CODE_BAD_INDEX)  # TODO: implement
        elif cmd == protocol.CMD_GET_SETTING_INFO:
            raise DeviceError(protocol.ERROR_CODE_BAD_INDEX)  # TODO: implement
        elif cmd == protocol.CMD_GET_SETTING_DEFAULT:
            raise DeviceError(protocol.ERROR_CODE_BAD_INDEX)  # TODO: implement
        elif cmd == protocol.CMD_GET_CUSTOM_ENUM_COUNTS:
            if len(params) != 0:
                raise DeviceError(protocol.ERROR_CODE_BAD_CMD_LENGTH)
            custom_enum_count = len(self.device_info.custom_enums)
            return bytes(len(self.device_info.custom_enums[i])
                         for i in range(custom_enum_count))
        elif cmd == protocol.CMD_GET_CUSTOM_ENUM_VALUE_NAME:
            if len(params) != 2:
                raise DeviceError(protocol.ERROR_CODE_BAD_CMD_LENGTH)
            enum_index = params[0]
            enum_value = params[1]
            enum_str = self.device_info.custom_enums[enum_index][enum_value]
            return enum_str.encode("UTF-8")
        elif cmd == protocol.CMD_GET_SETTING_CATEGORY_COUNT:
            if len(params) != 0:
                raise DeviceError(protocol.ERROR_CODE_BAD_CMD_LENGTH)
            return bytes((len(self.device_info.setting_categories),))
        elif cmd == protocol.CMD_GET_SETTING_CATEGORY_NAME:
            if len(params) != 1:
                raise DeviceError(protocol.ERROR_CODE_BAD_CMD_LENGTH)
            index = params[0]
            name = self.device_info.setting_categories[index][0]
            return name.encode("UTF-8")
        elif cmd == protocol.CMD_GET_SETTING_CATERORY_SETTINGS:
            if len(params) != 1:
                raise DeviceError(protocol.ERROR_CODE_BAD_CMD_LENGTH)
            index = params[0]
            return bytes(self.device_info.setting_categories[index][1])
        elif cmd == protocol.CMD_STOP_RADIO and self.radio_implemented:
            if len(params) != 0:
                raise DeviceError(protocol.ERROR_CODE_BAD_CMD_LENGTH)
            self._radio_stop()
        elif cmd == protocol.CMD_START_RADIO_SCAN and self.radio_implemented:
            if len(params) != 0:
                raise DeviceError(protocol.ERROR_CODE_BAD_CMD_LENGTH)
            self._radio_start_scan(False)
        elif (cmd == protocol.CMD_GET_RADIO_SCAN_RESULTS and
              self.radio_implemented):
            if len(params) != 0:
                raise DeviceError(protocol.ERROR_CODE_BAD_CMD_LENGTH)
            max_results = self.device_info.max_outgoing_param_length // 4
            scan_results = self._get_scan_results(max_results)
            return_bytes = bytearray()
            for scan_result in scan_results:
                return_bytes.extend(
                    struct.pack(">I", scan_result.serial_number))
            return bytes(return_bytes)
        elif cmd == protocol.CMD_CONNECT_RADIO and self.radio_implemented:
            if len(params) != 4:
                raise DeviceError(protocol.ERROR_CODE_BAD_CMD_LENGTH)
            serial_number = struct.unpack(">I", params)[0]
            self._radio_connect(serial_number, False)
        elif cmd == protocol.CMD_GET_RADIO_STATUS and self.radio_implemented:
            if len(params) != 0:
                raise DeviceError(protocol.ERROR_CODE_BAD_CMD_LENGTH)

            return struct.pack(">?IB?", *self._get_radio_status())
        elif (cmd == protocol.CMD_GET_RADIO_CTRL_VARS and
              self.radio_implemented):
            if len(params) != 0:
                raise DeviceError(protocol.ERROR_CODE_BAD_CMD_LENGTH)
            return bytes(self.device_info.radio_ctrl_vars or [])
        elif (cmd == protocol.CMD_GET_RADIO_DEFAULT_SERIAL and
              self.radio_implemented):
            if len(params) != 0:
                raise DeviceError(protocol.ERROR_CODE_BAD_CMD_LENGTH)
            default_serial = self.device_info.radio_default_serial or 0
            return struct.pack(">I", default_serial)
        elif (cmd == protocol.CMD_START_RADIO_SCAN_BOOT and
              self.radio_implemented):
            if len(params) != 0:
                raise DeviceError(protocol.ERROR_CODE_BAD_CMD_LENGTH)
            self._radio_start_scan(True)
        elif cmd == protocol.CMD_CONNECT_RADIO_BOOT and self.radio_implemented:
            if len(params) != 4:
                raise DeviceError(protocol.ERROR_CODE_BAD_CMD_LENGTH)
            serial_number = struct.unpack(">I", params)[0]
            self._radio_connect(serial_number, True)
        elif (cmd == protocol.CMD_GET_RADIO_EXTRA_SCAN_RESULTS and
              self.radio_implemented):
            if len(params) != 0:
                raise DeviceError(protocol.ERROR_CODE_BAD_CMD_LENGTH)
            max_results = self.device_info.max_outgoing_param_length // 6
            scan_results = self._get_scan_results(max_results)
            return_bytes = bytearray()
            for scan_result in scan_results:
                return_bytes.extend(
                    struct.pack(">IBB", scan_result.serial_number,
                                scan_result.protocol_type,
                                scan_result.device_mode))
            return bytes(return_bytes)
        elif (cmd == protocol.CMD_GET_RADIO_SCAN_POWER and
              self.radio_implemented):
            if len(params) % 4 != 0:
                raise DeviceError(protocol.ERROR_CODE_BAD_CMD_LENGTH)
            serial_numbers = struct.unpack(f">{len(params) // 4}I", params)
            return b"".join(self._get_radio_scan_power(serial_number)
                            for serial_number in serial_numbers)
        elif cmd == protocol.CMD_STOP_REMOTE and self.remote_implemented:
            if len(params) != 0:
                raise DeviceError(protocol.ERROR_CODE_BAD_CMD_LENGTH)
            # ignore
        elif cmd == protocol.CMD_RESTART_REMOTE and self.remote_implemented:
            if len(params) != 0:
                raise DeviceError(protocol.ERROR_CODE_BAD_CMD_LENGTH)
            self._restart_remote()
        elif cmd == protocol.CMD_GET_REMOTE_STATUS and self.remote_implemented:
            if len(params) != 0:
                raise DeviceError(protocol.ERROR_CODE_BAD_CMD_LENGTH)
            return struct.pack(">?IB",
                               True,  # connected
                               self.serial_number_int,
                               self.protocol_type)
        elif (cmd == protocol.CMD_RESTART_REMOTE_APP and
              self.remote_implemented):
            if len(params) != 0:
                raise DeviceError(protocol.ERROR_CODE_BAD_CMD_LENGTH)
            self._restart_remote()
        elif (cmd == protocol.CMD_RESTART_REMOTE_BOOT and
              self.remote_implemented):
            if len(params) != 0:
                raise DeviceError(protocol.ERROR_CODE_BAD_CMD_LENGTH)
            self._restart_remote()
        elif cmd == protocol.CMD_GET_GPIO_PORT_COUNT:
            if len(params) != 0:
                raise DeviceError(protocol.ERROR_CODE_BAD_CMD_LENGTH)
            return b'\x00'  # not supported
        elif cmd == protocol.CMD_GET_GPIO_PORT_NAME:
            raise DeviceError(protocol.ERROR_CODE_BAD_INDEX)  # not supported
        elif cmd == protocol.CMD_GET_GPIO_PORT_INFO:
            raise DeviceError(protocol.ERROR_CODE_BAD_INDEX)  # not supported
        elif cmd == protocol.CMD_GET_GPIO_PORT_VALUES:
            raise DeviceError(protocol.ERROR_CODE_BAD_INDEX)  # not supported
        elif cmd == protocol.CMD_SET_GPIO_PORT_MODES:
            raise DeviceError(protocol.ERROR_CODE_BAD_INDEX)  # not supported
        elif cmd == protocol.CMD_DISABLE_GPIO_PORT_OVERRIDES:
            pass  # not supported
        elif cmd == protocol.CMD_GET_BUS_COUNTS:
            return b'\x00\x00'  # not supported
        elif cmd == protocol.CMD_SET_SPI_CS_MODE:
            raise DeviceError(protocol.ERROR_CODE_BAD_INDEX)  # not supported
        elif cmd == protocol.CMD_DO_SPI_TRANSFER:
            raise DeviceError(protocol.ERROR_CODE_BAD_INDEX)  # not supported
        elif cmd == protocol.CMD_DO_I2C_WRITE:
            raise DeviceError(protocol.ERROR_CODE_BAD_INDEX)  # not supported
        elif cmd == protocol.CMD_DO_I2C_READ:
            raise DeviceError(protocol.ERROR_CODE_BAD_INDEX)  # not supported
        elif cmd == protocol.CMD_DO_I2C_WRITE_READ:
            raise DeviceError(protocol.ERROR_CODE_BAD_INDEX)  # not supported
        elif cmd == protocol.CMD_GET_INFO_REGION_COUNT:
            return b'\x00'  # not supported
        elif cmd == protocol.CMD_GET_INFO_REGION_NAME:
            raise DeviceError(protocol.ERROR_CODE_BAD_INDEX)  # not supported
        elif cmd == protocol.CMD_GET_INFO_REGION:
            raise DeviceError(protocol.ERROR_CODE_BAD_INDEX)  # not supported
        elif cmd == protocol.CMD_GET_STACK_INFO:
            return struct.pack(">2I", 0, 0)  # not supported
        else:
            raise DeviceError(protocol.ERROR_CODE_UNIMPLEMENTED_COMMAND)

        # everything is fine
        return b""

    def handle_command(self, rx_buf: bytes) -> bytes:
        if len(rx_buf) == 0:
            # nothing to do
            return b''

        if len(rx_buf) == 1:
            # malformed packet
            return bytes((rx_buf[0], protocol.CMD_REPLY_ERROR,
                          protocol.ERROR_CODE_MALFORMED_COMMAND,
                          protocol.CMD_REPLY_ERROR))

        cmd = rx_buf[1]
        params = rx_buf[2:]

        try:
            # check for the ECHO commands here, as they can't be handled in the
            # normal manner
            max_param_len = self.device_info.max_outgoing_param_length
            if cmd == protocol.CMD_ECHO_RAW:
                if len(params) > max_param_len + 2:
                    raise DeviceError(protocol.ERROR_CODE_BAD_CMD_LENGTH)
                return params
            elif cmd == protocol.CMD_ECHO_TRANSACTION:
                if len(params) > max_param_len + 1:
                    raise DeviceError(protocol.ERROR_CODE_BAD_CMD_LENGTH)
                return rx_buf[0:1] + params
            elif cmd == protocol.CMD_ECHO_PARAMS:
                if len(params) > max_param_len:
                    raise DeviceError(protocol.ERROR_CODE_BAD_CMD_LENGTH)
                return rx_buf[0:2] + params
            else:
                cmd_params = self._handle_command_internal(cmd, params)
                return rx_buf[0:2] + cmd_params
        except DeviceError as e:
            return bytes((rx_buf[0], protocol.CMD_REPLY_ERROR, e.error_code,
                          cmd))
        except (IndexError, KeyError):
            return bytes((rx_buf[0], protocol.CMD_REPLY_ERROR,
                          protocol.ERROR_CODE_BAD_INDEX, cmd))
