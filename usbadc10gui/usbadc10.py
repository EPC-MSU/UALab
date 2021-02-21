"""
Project generated by builder 0.10.7 protocol 0.1.7
"""
import logging
from sys import version_info
import struct
from ctypes import CDLL, Structure, Array, CFUNCTYPE, byref, create_string_buffer, cast
from ctypes import c_uint, c_ushort, c_ubyte
from ctypes import c_void_p, c_char_p, c_wchar_p, c_size_t, c_int
import atexit
try:
    from typing import overload, Union, Sequence, Optional
except ImportError:
    def overload(method):
        return method

    class _GenericTypeMeta(type):
        def __getitem__(self, _):
            return None

    class Union(metaclass=_GenericTypeMeta):
        pass

    class Sequence(metaclass=_GenericTypeMeta):
        pass

    class Optional(metaclass=_GenericTypeMeta):
        pass

urpc_builder_version_major = 0
urpc_builder_version_minor = 10
urpc_builder_version_bugfix = 7
urpc_builder_version_suffix = ""
urpc_builder_version = "0.10.7"
_Ok = 0
_Error = -1
_NotImplemented = -2
_ValueError = -3
_NoDevice = -4
_DeviceUndefined = -1


class UrpcError(Exception):
    pass


class UrpcValueError(UrpcError, ValueError):
    pass


class UrpcNotImplementedError(UrpcError, NotImplementedError):
    pass


class UrpcNoDeviceError(UrpcError, RuntimeError):
    pass


class UrpcDeviceUndefinedError(UrpcError, RuntimeError):
    pass


class UrpcUnknownError(UrpcError, RuntimeError):
    pass


class _IterableStructure(Structure):
    def __iter__(self):
        return (getattr(self, n) for n, t in self._fields_)


def _validate_call(result):
    if result == _ValueError:
        raise UrpcValueError()
    elif result == _NotImplemented:
        raise UrpcNotImplementedError()
    elif result == _NoDevice:
        raise UrpcNoDeviceError()
    elif result == _DeviceUndefined:
        raise UrpcDeviceUndefinedError()
    elif result != _Ok:
        raise UrpcUnknownError()


def _normalize_arg(value, desired_ctype):
    from collections import Sequence
    if isinstance(value, desired_ctype):
        return value
    elif issubclass(desired_ctype, Array) and isinstance(value, Sequence):
        member_type = desired_ctype._type_
        if desired_ctype._length_ < len(value):
            raise ValueError()
        if issubclass(member_type, c_ubyte) and isinstance(value, bytes):
            return desired_ctype.from_buffer_copy(value)
        elif issubclass(member_type, c_ubyte) and isinstance(value, bytearray):
            return desired_ctype.from_buffer(value)
        else:
            return desired_ctype(*value)
    else:
        return desired_ctype(value)


_logger = logging.getLogger(__name__)


def _load_specific_lib(path):
    # from os.path import isfile
    try:
        lib = CDLL(path)
        _logger.debug("Load library " + path + ": success")
        return lib
    except OSError as err:
        _logger.debug("Load library " + path + ": failed, " + str(err))
        raise err


def _near_script_path(libname):
    from os.path import dirname, abspath, join
    return join(abspath(dirname(__file__)), libname)


def _load_lib():
    from platform import system
    os_kind = system().lower()
    if os_kind == "windows":
        if 8 * struct.calcsize("P") == 32:
            paths = (_near_script_path("usbadc10-win32\\usbadc10.dll"),
                     _near_script_path("usbadc10.dll"),
                     "usbadc10.dll")
        else:
            paths = (_near_script_path("usbadc10-win64\\usbadc10.dll"),
                     _near_script_path("usbadc10.dll"),
                     "usbadc10.dll")
    elif os_kind == "darwin":
        paths = (_near_script_path("usbadc10-darwin/libusbadc10.dylib"),
                 _near_script_path("libusbadc10.dylib"),
                 "libusbadc10.dylib")
    elif os_kind == "freebsd" or "linux" in os_kind:
        paths = (_near_script_path("usbadc10-debian/libusbadc10.so"),
                 _near_script_path("libusbadc10.so"),
                 "libusbadc10.so")
    else:
        raise RuntimeError("unexpected OS")

    errors = []
    for path in paths:
        try:
            lib = _load_specific_lib(path)
        except Exception as e:
            errors.append(str(e))
        else:
            return lib

    error_msg = "Unable to load library. Paths tried:\n"
    for i, path in enumerate(paths):
        error_msg = error_msg + str(path) + " - got error: " + errors[i] + "\n"

    raise RuntimeError(error_msg)


_lib = _load_lib()


# Hack to prevent auto-conversion to native Python int
class _device_t(c_int):
    def from_param(self, *args):
        return self


_lib.usbadc10_open_device.restype = _device_t


@CFUNCTYPE(None, c_int, c_wchar_p, c_void_p)
def _logging_callback(loglevel, message, user_data):
    if loglevel == 0x01:
        _logger.error(message)
    elif loglevel == 0x02:
        _logger.warning(message)
    elif loglevel == 0x03:
        _logger.info(message)
    elif loglevel == 0x04:
        _logger.debug(message)


_lib.usbadc10_set_logging_callback(_logging_callback, 0)
atexit.register(lambda: _lib.usbadc10_set_logging_callback(None, 0))
_lib.usbadc10_set_logging_callback(_logging_callback, 0)
atexit.register(lambda: _lib.usbadc10_set_logging_callback(None, 0))


def reset_locks():
    _validate_call(_lib.usbadc10_reset_locks())


def fix_usbser_sys():
    _validate_call(_lib.usbadc10_fix_usbser_sys())


class Usbadc10DeviceHandle:
    def save_settings(self) -> None:
        _validate_call(_lib.usbadc10_save_settings(self._handle))

    def read_settings(self) -> None:
        _validate_call(_lib.usbadc10_read_settings(self._handle))

    class GetIdentityInformationResponse(_IterableStructure):
        _fields_ = (
            ("_manufacturer", c_ubyte*16),
            ("_product_name", c_ubyte*16),
            ("_controller_name", c_ubyte*16),
            ("_hardware_major", c_ubyte),
            ("_hardware_minor", c_ubyte),
            ("_hardware_bugfix", c_ushort),
            ("_bootloader_major", c_ubyte),
            ("_bootloader_minor", c_ubyte),
            ("_bootloader_bugfix", c_ushort),
            ("_firmware_major", c_ubyte),
            ("_firmware_minor", c_ubyte),
            ("_firmware_bugfix", c_ushort),
            ("_serial_number", c_uint),
            ("_reserved", c_ubyte*8),
        )

        @property
        def manufacturer(self) -> c_ubyte*16:
            return self._manufacturer

        @manufacturer.setter
        def manufacturer(self, value: Union[Sequence[int], c_ubyte*16]) -> None:
            self._manufacturer = _normalize_arg(value, c_ubyte*16)

        @property
        def product_name(self) -> c_ubyte*16:
            return self._product_name

        @product_name.setter
        def product_name(self, value: Union[Sequence[int], c_ubyte*16]) -> None:
            self._product_name = _normalize_arg(value, c_ubyte*16)

        @property
        def controller_name(self) -> c_ubyte*16:
            return self._controller_name

        @controller_name.setter
        def controller_name(self, value: Union[Sequence[int], c_ubyte*16]) -> None:
            self._controller_name = _normalize_arg(value, c_ubyte*16)

        @property
        def hardware_major(self) -> c_ubyte:
            return self._hardware_major

        @hardware_major.setter
        def hardware_major(self, value: Union[int, c_ubyte]) -> None:
            self._hardware_major = _normalize_arg(value, c_ubyte)

        @property
        def hardware_minor(self) -> c_ubyte:
            return self._hardware_minor

        @hardware_minor.setter
        def hardware_minor(self, value: Union[int, c_ubyte]) -> None:
            self._hardware_minor = _normalize_arg(value, c_ubyte)

        @property
        def hardware_bugfix(self) -> c_ushort:
            return self._hardware_bugfix

        @hardware_bugfix.setter
        def hardware_bugfix(self, value: Union[int, c_ushort]) -> None:
            self._hardware_bugfix = _normalize_arg(value, c_ushort)

        @property
        def bootloader_major(self) -> c_ubyte:
            return self._bootloader_major

        @bootloader_major.setter
        def bootloader_major(self, value: Union[int, c_ubyte]) -> None:
            self._bootloader_major = _normalize_arg(value, c_ubyte)

        @property
        def bootloader_minor(self) -> c_ubyte:
            return self._bootloader_minor

        @bootloader_minor.setter
        def bootloader_minor(self, value: Union[int, c_ubyte]) -> None:
            self._bootloader_minor = _normalize_arg(value, c_ubyte)

        @property
        def bootloader_bugfix(self) -> c_ushort:
            return self._bootloader_bugfix

        @bootloader_bugfix.setter
        def bootloader_bugfix(self, value: Union[int, c_ushort]) -> None:
            self._bootloader_bugfix = _normalize_arg(value, c_ushort)

        @property
        def firmware_major(self) -> c_ubyte:
            return self._firmware_major

        @firmware_major.setter
        def firmware_major(self, value: Union[int, c_ubyte]) -> None:
            self._firmware_major = _normalize_arg(value, c_ubyte)

        @property
        def firmware_minor(self) -> c_ubyte:
            return self._firmware_minor

        @firmware_minor.setter
        def firmware_minor(self, value: Union[int, c_ubyte]) -> None:
            self._firmware_minor = _normalize_arg(value, c_ubyte)

        @property
        def firmware_bugfix(self) -> c_ushort:
            return self._firmware_bugfix

        @firmware_bugfix.setter
        def firmware_bugfix(self, value: Union[int, c_ushort]) -> None:
            self._firmware_bugfix = _normalize_arg(value, c_ushort)

        @property
        def serial_number(self) -> c_uint:
            return self._serial_number

        @serial_number.setter
        def serial_number(self, value: Union[int, c_uint]) -> None:
            self._serial_number = _normalize_arg(value, c_uint)

        @property
        def reserved(self) -> c_ubyte*8:
            return self._reserved

        @reserved.setter
        def reserved(self, value: Union[Sequence[int], c_ubyte*8]) -> None:
            self._reserved = _normalize_arg(value, c_ubyte*8)

    def get_identity_information(self, **kwargs) -> "GetIdentityInformationResponse":
        dst_buffer = kwargs.get("dst_buffer", self.GetIdentityInformationResponse())
        _validate_call(_lib.usbadc10_get_identity_information(self._handle, byref(dst_buffer)))
        return dst_buffer

    def reboot_to_bootloader(self) -> None:
        _validate_call(_lib.usbadc10_reboot_to_bootloader(self._handle))

    class DebugReadResponse(_IterableStructure):
        _fields_ = (
            ("_debug_data", c_ubyte*128),
            ("_reserved", c_ubyte*8),
        )

        @property
        def debug_data(self) -> c_ubyte*128:
            return self._debug_data

        @debug_data.setter
        def debug_data(self, value: Union[Sequence[int], c_ubyte*128]) -> None:
            self._debug_data = _normalize_arg(value, c_ubyte*128)

        @property
        def reserved(self) -> c_ubyte*8:
            return self._reserved

        @reserved.setter
        def reserved(self, value: Union[Sequence[int], c_ubyte*8]) -> None:
            self._reserved = _normalize_arg(value, c_ubyte*8)

    def debug_read(self, **kwargs) -> "DebugReadResponse":
        dst_buffer = kwargs.get("dst_buffer", self.DebugReadResponse())
        _validate_call(_lib.usbadc10_debug_read(self._handle, byref(dst_buffer)))
        return dst_buffer

    class DebugWriteRequest(_IterableStructure):
        _fields_ = (
            ("_debug_data", c_ubyte*128),
            ("_reserved", c_ubyte*8),
        )

        @property
        def debug_data(self) -> c_ubyte*128:
            return self._debug_data

        @debug_data.setter
        def debug_data(self, value: Union[Sequence[int], c_ubyte*128]) -> None:
            self._debug_data = _normalize_arg(value, c_ubyte*128)

        @property
        def reserved(self) -> c_ubyte*8:
            return self._reserved

        @reserved.setter
        def reserved(self, value: Union[Sequence[int], c_ubyte*8]) -> None:
            self._reserved = _normalize_arg(value, c_ubyte*8)

    @overload  # noqa: F811
    def debug_write(
            self,
            debug_data: Union[Sequence[int], c_ubyte*128],
            reserved: Union[Sequence[int], c_ubyte*8]
    ) -> None: pass

    @overload  # noqa: F811
    def debug_write(
            self,
            src_buffer: DebugWriteRequest
    ) -> None: pass

    def debug_write(self, *args) -> None:  # noqa: F811
        src_buffer = None
        if len(args) != 1 or not isinstance(args[0], self.DebugWriteRequest):
            src_buffer = self.DebugWriteRequest(
                debug_data=_normalize_arg(args[0], c_ubyte*128),
                reserved=_normalize_arg(args[1], c_ubyte*8)
            )
        else:
            src_buffer = args[0]
        _validate_call(_lib.usbadc10_debug_write(self._handle, byref(src_buffer)))

    def reset(self) -> None:
        _validate_call(_lib.usbadc10_reset(self._handle))

    def update_firmware(self) -> None:
        _validate_call(_lib.usbadc10_update_firmware(self._handle))

    class GetConversionRawResponse(_IterableStructure):
        _fields_ = (
            ("_data", c_ushort*10),
            ("_reserved", c_ubyte*12),
        )

        @property
        def data(self) -> c_ushort*10:
            return self._data

        @data.setter
        def data(self, value: Union[Sequence[int], c_ushort*10]) -> None:
            self._data = _normalize_arg(value, c_ushort*10)

        @property
        def reserved(self) -> c_ubyte*12:
            return self._reserved

        @reserved.setter
        def reserved(self, value: Union[Sequence[int], c_ubyte*12]) -> None:
            self._reserved = _normalize_arg(value, c_ubyte*12)

    def get_conversion_raw(self, **kwargs) -> "GetConversionRawResponse":
        dst_buffer = kwargs.get("dst_buffer", self.GetConversionRawResponse())
        _validate_call(_lib.usbadc10_get_conversion_raw(self._handle, byref(dst_buffer)))
        return dst_buffer

    class GetConversionResponse(_IterableStructure):
        _fields_ = (
            ("_data", c_ushort*10),
            ("_reserved", c_ubyte*12),
        )

        @property
        def data(self) -> c_ushort*10:
            return self._data

        @data.setter
        def data(self, value: Union[Sequence[int], c_ushort*10]) -> None:
            self._data = _normalize_arg(value, c_ushort*10)

        @property
        def reserved(self) -> c_ubyte*12:
            return self._reserved

        @reserved.setter
        def reserved(self, value: Union[Sequence[int], c_ubyte*12]) -> None:
            self._reserved = _normalize_arg(value, c_ubyte*12)

    def get_conversion(self, **kwargs) -> "GetConversionResponse":
        dst_buffer = kwargs.get("dst_buffer", self.GetConversionResponse())
        _validate_call(_lib.usbadc10_get_conversion(self._handle, byref(dst_buffer)))
        return dst_buffer

    class CalibrationSettingsRequest(_IterableStructure):
        _fields_ = (
            ("_reserved", c_ubyte*4),
        )

        @property
        def reserved(self) -> c_ubyte*4:
            return self._reserved

        @reserved.setter
        def reserved(self, value: Union[Sequence[int], c_ubyte*4]) -> None:
            self._reserved = _normalize_arg(value, c_ubyte*4)

    CalibrationSettingsResponse = CalibrationSettingsRequest

    def get_calibration_settings(self, **kwargs) -> "CalibrationSettingsResponse":
        dst_buffer = kwargs.get("dst_buffer", self.CalibrationSettingsResponse())
        _validate_call(_lib.usbadc10_get_calibration_settings(self._handle, byref(dst_buffer)))
        return dst_buffer

    @overload  # noqa: F811
    def set_calibration_settings(
            self,
            reserved: Union[Sequence[int], c_ubyte*4]
    ) -> None: pass

    @overload  # noqa: F811
    def set_calibration_settings(
            self,
            src_buffer: CalibrationSettingsRequest
    ) -> None: pass

    def set_calibration_settings(self, *args) -> None:  # noqa: F811
        src_buffer = None
        if len(args) != 1 or not isinstance(args[0], self.CalibrationSettingsRequest):
            src_buffer = self.CalibrationSettingsRequest(
                reserved=_normalize_arg(args[0], c_ubyte*4)
            )
        else:
            src_buffer = args[0]
        _validate_call(_lib.usbadc10_set_calibration_settings(self._handle, byref(src_buffer)))

    def __init__(self, uri, defer_open=False):
        if isinstance(uri, str):
            uri = uri.encode("utf-8")
        if not isinstance(uri, (bytes, bytearray)):
            raise ValueError()
        self._uri = uri
        self._handle = None
        if not defer_open:
            self.open_device()
    if version_info >= (3, 4):
        def __del__(self):
            if self._handle:
                self.close_device()

    @property
    def uri(self):
        return self._uri

    def open_device(self):
        if self._handle is not None:
            return False

        handle = _lib.usbadc10_open_device(self._uri)
        if handle.value == _DeviceUndefined:
            raise UrpcDeviceUndefinedError()

        self._handle = handle
        return True

    def lib_version(self):
        ver_lib = create_string_buffer(str.encode("00.00.00"))
        result = _lib.usbadc10_libversion(ver_lib)
        _validate_call(result)
        version_lib = ver_lib.value.decode("utf-8")
        return version_lib

    def close_device(self):
        if self._handle is None:
            return False

        try:
            result = _lib.usbadc10_close_device(byref(self._handle))
            _validate_call(result)
        except Exception as e:
            raise e
        else:
            return True
        finally:
            self._handle = None

    def get_profile(self):
        buffer = c_char_p()

        @CFUNCTYPE(c_void_p, c_size_t)
        def allocate(size):
            # http://bugs.python.org/issue1574593
            return cast(create_string_buffer(size+1), c_void_p).value
        _validate_call(_lib.usbadc10_get_profile(self._handle, byref(buffer), allocate))
        return buffer.value.decode("utf-8")

    def set_profile(self, source):
        if isinstance(source, str):
            source = source.encode("utf-8")
        _validate_call(_lib.usbadc10_set_profile(self._handle, c_char_p(source), len(source)))
