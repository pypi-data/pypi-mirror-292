from __future__ import annotations

import asyncio
import contextlib
import json
import random
import signal
import socket
import statistics
import string
import timeit
import traceback

from collections.abc import Callable, Generator, Iterator, Mapping, Sequence
from colorsys import rgb_to_hls, hls_to_rgb
from dataclasses import dataclass
from datetime import datetime, timedelta
from functools import cached_property, wraps
from http.client import HTTPResponse
from importlib import import_module
from importlib.resources import files as pkgfiles
from inspect import currentframe
from pathlib import Path
from types import FrameType, FunctionType
from typing import TYPE_CHECKING, Any, Generic, IO, Literal, TypeVar, overload
from urllib.request import Request, urlopen

from . import __version__
from .date import Date
from .enums import FileSizeUnit, HttpMethod, PridePalette

if TYPE_CHECKING:
	try:
		from typing import Self

	except ImportError:
		from typing_extensions import Self


T = TypeVar("T")
C = TypeVar("C", bound = type)
DictValueType = TypeVar("DictValueType")

TRUE_STR = ['on', 'y', 'yes', 'true', 'enable', 'enabled', '1']
FALSE_STR = ['off', 'n', 'no', 'false', 'disable', 'disable', '0']

TLD_CACHE_URL = "https://publicsuffix.org/list/public_suffix_list.dat"
TLD_CACHE_PATH = Path("~/.cache").expanduser().joinpath('public_suffix_list.txt')
TLD_CACHE_DATA: list[str] = []

_SIGNAL_STRS = ("SIGHUP", "SIGILL", "SIGTERM", "SIGINT")
DEFAULT_SIGNALS = tuple(getattr(signal, sig) for sig in _SIGNAL_STRS if hasattr(signal, sig))


@contextlib.contextmanager
def catch_errors(suppress: bool = False) -> Generator[None, None, None]:
	"""
		Context manager for running a block of code and catching any errors that get raised

		:param suppress: If ``True``, don't print a raised exception
	"""
	try:
		yield

	except Exception:
		if not suppress:
			traceback.print_exc()


def convert_to_boolean(value: Any) -> bool:
	"""
		Convert an object to :class:`bool`. If it can't be directly converted, ``True``
		is returned.

		:param value: Object to be converted
	"""
	if value is None:
		return False

	if isinstance(value, bool):
		return value

	if isinstance(value, str):
		if value.lower() in TRUE_STR:
			return True

		if value.lower() in FALSE_STR:
			return False

	if isinstance(value, int):
		if value == 1:
			return True

		if value == 0:
			return False

	return bool(value)


def convert_to_bytes(value: Any, encoding: str = "utf-8") -> bytes:
	"""
		Convert an object to :class:`bytes`

		:param value: Object to be converted
		:param encoding: Character encoding to use if the object is a string or gets converted to
			one in the process
		:raises TypeError: If the object cannot be converted
	"""
	if isinstance(value, bytes):
		return value

	try:
		return convert_to_string(value).encode(encoding)

	except TypeError:
		raise TypeError(f"Cannot convert '{get_object_name(value)}' into bytes") from None


def convert_to_string(value: Any, encoding: str = 'utf-8') -> str:
	"""
		Convert an object to :class:`str`

		:param value: Object to be converted
		:param encoding: Character encoding to use if the object is a :class:`bytes` object
	"""
	if isinstance(value, bytes):
		return value.decode(encoding)

	if isinstance(value, bool):
		return str(value)

	if isinstance(value, str):
		return value

	if isinstance(value, Date):
		return value.to_string()

	if isinstance(value, JsonBase):
		return value.to_json()

	if isinstance(value, (dict, list, tuple, set)):
		return json.dumps(value)

	if isinstance(value, (int, float)):
		return str(value)

	if value is None:
		return ''

	raise TypeError(f'Cannot convert "{get_object_name(value)}" into a string') from None


def deprecated(
			new_method: str | None,
			version: str,
			remove: str | None = None) -> Callable[..., Any]:
	"""
		Decorator to mark a function as deprecated and display a warning on first use.

		:param new_method: Name of the function to replace the wrapped function
		:param version: Version of the module in which the wrapped function was considered
			deprecated
		:param remove: Version the wrapped function will get removed
	"""

	called = False

	def wrapper(func: Callable[..., Any]) -> Callable[..., Any]:
		@wraps(func)
		def inner(*args: Any, **kwargs: Any) -> Any:
			if not called:
				name = func.__qualname__ if hasattr(func, "__qualname__") else func.__name__

				if not remove:
					msg = f"WARN: {name} was deprecated in {version}."

				else:
					msg = f"WARN: {name} was deprecated in {version} and will be removed in {remove}."

				print(msg + (f" Use {new_method} instead." if new_method is not None else ""))

			return func(*args, **kwargs)
		return inner
	return wrapper


def get_object_name(obj: Any) -> str:
	"""
		Get the name of an object

		:param obj: Object to get the name of
	"""

	try:
		return obj.__name__ # type: ignore[no-any-return]

	except AttributeError:
		return type(obj).__name__


def get_object_properties(
						obj: Any,
						ignore_descriptors: bool = False,
						ignore_underscore: bool = True) -> Iterator[tuple[str, Any]]:
	"""
		Get an objet's properties and their values

		:param obj: Object to get the properties of
		:param ignore_descriptors: Don't get the value of descriptor objects (ex. ``@property``)
		:param ignore_underscore: Skip properties that start with an underscore (``_``)
	"""

	for key in dir(obj):
		value = getattr(obj, key)

		if ignore_underscore and key.startswith("_"):
			continue

		if isinstance(value, FunctionType):
			continue

		if ignore_descriptors and hasattr(value, "__get__"):
			continue

		yield key, value


def get_resource_path(module: str, path: str | None = None) -> Path:
	"""
		Get a path to a module resource

		:param module: Name of the module to get the resource from
		:param path: Path of the resource starting from the path of the module
	"""

	new_path = Path(str(pkgfiles(module)))
	return new_path.joinpath(path.lstrip("/")) if path is not None else new_path


def get_top_domain(domain: str) -> str:
	'''
		Get the main domain from a string. The top-level domain list is cached as
		``~/.cache/public_suffix_list.txt`` for 7 days

		:param str domain: The domain to extract the top-level domain from
		:raises ValueError: When the top domain cannot be found
	'''

	global TLD_CACHE_DATA

	if len(TLD_CACHE_DATA) == 0:
		exists = TLD_CACHE_PATH.exists()

		try:
			modified = datetime.fromtimestamp(TLD_CACHE_PATH.stat().st_mtime)

		except FileNotFoundError:
			modified = None

		if not exists or not modified or modified + timedelta(days=7) < datetime.now():
			TLD_CACHE_PATH.parent.mkdir(exist_ok = True, parents = True)

			with TLD_CACHE_PATH.open("wt", encoding = "utf-8") as fd:
				with http_request(TLD_CACHE_URL) as resp:
					for line in resp.read().decode('utf-8').splitlines():
						if 'end icann domains' in line.lower():
							break

						if not line or line.startswith('//'):
							continue

						if line.startswith('*'):
							line = line[2:]

						fd.write(line + "\n")

		with TLD_CACHE_PATH.open("r", encoding = "utf-8") as fd:
			TLD_CACHE_DATA = list(fd.read().splitlines())

	domain_split = domain.split('.')

	try:
		if '.'.join(domain_split[-2:]) in TLD_CACHE_DATA:
			return '.'.join(domain_split[-3:])

	except IndexError:
		pass

	if '.'.join(domain_split[-1:]) in TLD_CACHE_DATA:
		return '.'.join(domain_split[-2:])

	raise ValueError('Cannot find TLD')


def http_request(
				url: str,
				data: Any = None,
				headers: dict[str, str] | None = None,
				method: HttpMethod | str = HttpMethod.GET,
				timeout: int = 60) -> HTTPResponse:
	"""
		Make an http request. The default User-Agent is "blib/:attr:`BLib.__version__`"

		:param url: Url to send the request to
		:param data: Data to send with the request. Must be parsable by :class:`convert_to_bytes`.
		:param method: HTTP method to use when making the request
		:param headers: HTTP header key/value pairs to send with the request
		:param timeout: How long to wait when connecting before giving up

		:raises TimeoutError: When the connection was not established before the timeout limit
		:raises urllib.error.HTTPError: When the server returns an error
	"""

	method = HttpMethod.parse(method)

	if not headers:
		headers = {}

	else:
		headers = {key.title(): value for key, value in headers.items()}

	if headers.get("User-Agent") is None:
		headers["User-Agent"] = f"BLib/{__version__}"

	request = Request(
		url = url,
		method = method.upper(),
		data = convert_to_bytes(data) if data else None,
		headers = headers
	)

	return urlopen(request, timeout = timeout) # type: ignore[no-any-return]


def is_loop_running() -> bool:
	"Check if an event loop is running in the current thread"

	try:
		return asyncio.get_running_loop().is_running()

	except RuntimeError:
		return False


def port_check(port: int, address: str = "127.0.0.1", tcp: bool = True) -> bool:
	"""
		Check if a TCP or UDP port is in use. Returns ``True`` if the port is in use.

		:param port: Port number to check
		:param address: IP address or hostname to use as the source address
		:param tcp: Whether to use TCP (``True``) or UDP (``False``)
	"""

	with socket.socket(socket.AF_INET, socket.SOCK_STREAM if tcp else socket.SOCK_DGRAM) as s:
		try:
			return s.connect_ex((address, port)) == 0

		except socket.error:
			return False


def random_port(
			lower: int = 49152,
			upper: int = 65535,
			address: str = "127.0.0.1",
			tcp: bool = True,
			tries: int = 10) -> int:
	"""
		Find a random open tcp or udp port between ``upper`` and ``lower``.

		:param lower: Lowest port number to use
		:param upper: Highest port number to use
		:param address: IP address or hostname to use as the source address
		:param tcp: Whether to use TCP (``True``) or UDP (``False``)
		:param tries: Number of times to find an open port before giving up
	"""

	cycles = 0

	while cycles < tries:
		port = random.choice(range(lower, upper + 1))

		if not port_check(port, address, tcp):
			return port

		cycles += 1

	raise ConnectionError("Failed to find an open port")


def random_str(
			length: int = 20,
			letters: bool = True,
			numbers: bool = True,
			capital: bool = False,
			extra: str = "") -> str:
	"""
		Return a randomly generated string. Uses alphanumeric characters by default, but more can
		be specified as a string.

		:param length: Length of the resulting string in characters
		:param letters: Include all ascii letters
		:param numbers: Include numbers
		:param capital: Include uppercase ascii letters if ``letters`` is ``True``
		:param extra: Characters to also include in the resulting string
	"""

	characters = extra

	if letters:
		characters += string.ascii_letters

		if capital:
			characters += string.ascii_letters.upper()

	if numbers:
		characters += string.digits

	return "".join(random.choices(characters, k = length))


def set_signal_handler(
					handler: Callable[[int, FrameType | None], None] | None,
					signals: Sequence[int] = DEFAULT_SIGNALS) -> None:
	"""
		Set a callback for for a group of OS signals. Set ``handler`` to ``None`` to reset the
		callback to default.

		If no signals are specified the following signals (if available) will be set by default:

		* :data:`signal.SIGHUP`
		* :data:`signal.SIGILL`
		* :data:`signal.SIGTERM`
		* :data:`signal.SIGINT`

		:param handler: Function that gets called when a listed signal is received
		:param signals: A list of signals to handle
	"""

	for sig in signals:
		signal.signal(sig, handler or signal.SIG_DFL)


def time_function(
				func: Callable[..., Any],
				*args: Any,
				passes: int = 1,
				use_gc: bool = True,
				**kwargs: Any) -> RunData:
	"""
		Call a function n times and return each run time, the average time, and the total time in
		miliseconds

		:param func: Function to call
		:param args: Positional arguments to pass to the function
		:param passes: Number of times to call the function
		:param use_gc: Enable garbage collection during the runs
		:param kwargs: Keyword arguments to pass to the function
	"""

	if use_gc:
		timer = timeit.Timer(lambda: func(*args, **kwargs), "gc.enable()")

	else:
		timer = timeit.Timer(lambda: func(*args, **kwargs))

	if passes > 1:
		times = timer.repeat(passes, 1)

	else:
		times = [timer.timeit(1)]

	return RunData(tuple(times), statistics.fmean(times), sum(times))


def time_function_pprint(
					func: Callable[..., Any],
					*args: Any,
					passes: int = 5,
					use_gc: bool = True,
					floatout: bool = True,
					**kwargs: Any) -> RunData:
	"""
		Prints out readable results from ``time_function`` and returns the raw data. Convert the
		printed times to an ``int`` by setting ``floatout`` to ``False``

		:param func: Function to call
		:param args: Positional arguments to pass to the function
		:param passes: Number of times to call the function
		:param use_gc: Enable garbage collection during the runs
		:param floatout: Print values as ``float`` instead of ``int``
		:param kwargs: Keyword arguments to pass to the function
	"""

	data = time_function(func, *args, **kwargs, passes = passes, use_gc = use_gc)

	for idx, passtime in enumerate(data.runs):
		if not floatout:
			print(f"Pass {idx+1}: {passtime:.0f}")

		else:
			print(f"Pass {idx+1}: {passtime:.8f}")

	print("-----------------")

	if not floatout:
		print(f"Average: {data.average:.0f}")
		print(f"Total: {data.total:.0f}")

	else:
		print(f"Average: {data.average:.8f}")
		print(f"Total: {data.total:.8f}")

	return data


# mypy complains when `type[Self]` is used for decorated methods
class ClassProperty(Generic[T]):
	def __init__(self, func: Callable[[C], T]) -> None:
		self.func: Callable[[C], T] = func


	@overload
	def __get__(self, obj: Any, cls: C) -> T:
		...


	@overload
	def __get__(self, obj: Any, cls: None) -> Self:
		...


	def __get__(self, obj: Any, cls: C | None) -> T | Self:
		if cls is None:
			return self

		return self.func(cls)


class Color(str):
	"Represents an HTML color value"


	def __new__(cls, color: str) -> Self:
		"""
			Create a new ``Color`` object

			:param color: Hex color string of 3 or 6 characters (``#`` character optional)
		"""

		color = color.lstrip("#")

		if len(color) == 3:
			color = f"{color[1]*2}{color[2]*2}{color[3]*2}"

		elif len(color) != 6:
			raise TypeError("Color must be 3 or 6 character hex string")

		return str.__new__(cls, "#" + color)


	def __repr__(self) -> str:
		return f"Color('{self}')"


	@classmethod
	def from_rgb(cls: type[Self], red: int, green: int, blue: int) -> Self:
		"""
			Create a new ``Color`` object from red, green, and blue values. The values must be
			between ``0`` and ``255``.

			:param red: Red color value
			:param green: Green color value
			:param blue: Blue color value
		"""

		values = [red, green, blue]

		for value in values:
			if 0 < value > 255:
				raise ValueError("Color value must be anywhere from 0 to 255")

		return cls("#" + "".join(hex(value)[2:].rjust(2, "0") for value in values))


	@classmethod
	def from_hsl(cls: type[Self], hue: int, saturation: int, luminance: int) -> Self:
		"""
			Create a new ``Color`` object from hue, saturation, and luminance values. The values
			must be between ``0`` and ``255``.

			:param hue: Hue level
			:param saturation: Saturation level
			:param luminance: Luminance level
		"""

		hsl_values: list[int | float] = [hue, saturation, luminance]

		for idx, value in enumerate(hsl_values):
			if 0 < value > 255:
				raise ValueError("HSV values must be anywhere from 0 to 255")

			hsl_values[idx] = value / 255

		rgb_values = hls_to_rgb(hsl_values[0], hsl_values[2], hsl_values[1])
		values = [int(value * 255) for value in rgb_values]

		return cls("#" + "".join(hex(value)[2:].rjust(2, "0") for value in values))


	@classmethod
	def new_pride_palette(cls: type[Self], flag: PridePalette | str) -> tuple[Self, ...]:
		"""
			Returns multiple ``Color`` objects which represents a pride flag color palette

			:param flag: Name of the flag
		"""

		if not isinstance(flag, PridePalette):
			flag = PridePalette.parse(flag.replace("-", ""))

		return tuple(cls(color) for color in flag)


	@staticmethod
	def _parse_multi(multiplier: int) -> float:
		if multiplier >= 100:
			return 1

		elif multiplier <= 0:
			return 0

		return multiplier / 100


	@cached_property
	def rgb(self) -> tuple[int, int, int]:
		"Get the color as a tuple of red, green, and blue levels"

		return (self.red, self.green, self.blue)


	@cached_property
	def hsl(self) -> tuple[int, int, int]:
		"Get the color as a tuple of hue, saturation, and luminance levels"

		rgb = [value / 255 for value in self.rgb]
		values = [int(value * 255) for value in rgb_to_hls(*rgb)]
		return (values[0], values[2], values[1])


	@cached_property
	def red(self) -> int:
		"Get the red color level"

		return int(self[1:3], 16)


	@cached_property
	def green(self) -> int:
		"Get the green color level"

		return int(self[3:5], 16)


	@cached_property
	def blue(self) -> int:
		"Get the blue color level"

		return int(self[5:7], 16)


	@cached_property
	def hue(self) -> int:
		"Get the hue level"

		return self.hsl[0]


	@cached_property
	def saturation(self) -> int:
		"Get the saturation level"

		return self.hsl[1]


	@cached_property
	def luminance(self) -> int:
		"Get the luminance level"

		return self.hsl[2]


	def alter(self,
			action: Literal["lighten", "darken", "saturate", "desaturate"],
			multiplier: int) -> Self:
		"""
			Change the lightness or saturation of the color

			:param action: Modification action to take on the color
			:param multiplier: Amount to multiply by for the effect. Any value outside
				0 - 100 will be changed to the nearest valid value.
		"""

		hue, saturation, luminance = self.hsl

		if action == "lighten":
			luminance += int((255 - luminance) * Color._parse_multi(multiplier))

		elif action == "darken":
			luminance -= int(luminance * Color._parse_multi(multiplier))

		elif action == "saturate":
			saturation += int((255 - saturation) * Color._parse_multi(multiplier))

		elif action == "desaturate":
			saturation -= int(saturation * Color._parse_multi(multiplier))

		else:
			raise ValueError(f"Invalid action: {action}")

		return self.__class__.from_hsl(hue, saturation, luminance)


	def lighten(self, multiplier: int) -> Self:
		"""
			Alias of ``Color.alter('lighten', multiplier)``

			:param multiplier: Amount to multiply by for the effect. Any value outside
				0 - 100 will be changed to the nearest valid value.
		"""

		return self.alter("lighten", multiplier)


	def darken(self, multiplier: int) -> Self:
		"""
			Alias of ``Color.alter('darken', multiplier)``

			:param multiplier: Amount to multiply by for the effect. Any value outside
				0 - 100 will be changed to the nearest valid value.
		"""

		return self.alter("darken", multiplier)


	def saturate(self, multiplier: int) -> Self:
		"""
			Alias of ``Color.alter('saturate', multiplier)``

			:param multiplier: Amount to multiply by for the effect. Any value outside
				0 - 100 will be changed to the nearest valid value.
		"""

		return self.alter("saturate", multiplier)


	def desaturate(self, multiplier: int) -> Self:
		"""
			Alias of ``Color.alter('desaturate', multiplier)``

			:param multiplier: Amount to multiply by for the effect. Any value outside
				0 - 100 will be changed to the nearest valid value.
		"""

		return self.alter("desaturate", multiplier)


	def rgba(self, opacity: int) -> str:
		"""
			Return the color as a CSS ``rgba`` value

			:param opacity: Opacity level to apply to the color. Any value outside
				0 - 100 will be changed to the nearest valid value.
		"""

		if 0 < opacity > 100:
			raise ValueError("Opacity must anywhere from 0 to 100")

		values = ", ".join(str(value) for value in self.rgb)
		trans = opacity / 100
		return f"rgba({values}, {trans:.2})"



class DictProperty(Generic[DictValueType]):
	"Represents a key in a dict"


	def __init__(self,
				key: str,
				deserializer: Callable[[str, Any], DictValueType] | None = None,
				serializer: Callable[[str, DictValueType], Any] | None = None) -> None:
		"""
			Create a new dict property

			:param key: Name of the key to be handled by this ``Property``
			:param deserializer: Function that will convert a JSON value to a Python value
			:param serializer: Function that will convert a Python value to a JSON value
		"""

		self.key: str = key
		self.deserializer: Callable[[str, Any], Any] | None = deserializer
		self.serializer: Callable[[str, Any], Any] | None = serializer


	def __get__(self,
				obj: dict[str, DictValueType | Any] | None,
				objtype: Any = None) -> DictValueType:

		if obj is None:
			raise RuntimeError("No object for dict property")

		try:
			value = obj[self.key]

		except KeyError:
			objname = get_object_name(obj)
			raise AttributeError(f"'{objname}' has no attribute '{self.key}'") from None

		if self.deserializer is None:
			return value

		return self.deserializer(self.key, value) # type: ignore[no-any-return]


	def __set__(self, obj: dict[str, DictValueType | Any], value: DictValueType) -> None:
		if self.serializer is None:
			obj[self.key] = value
			return

		obj[self.key] = self.serializer(self.key, value)


	def __delete__(self, obj: dict[str, DictValueType | Any]) -> None:
		del obj[self.key]


class FileSize(int):
	"Converts a human-readable file size to bytes"


	def __new__(cls: type[Self],
				size: int | float,
				unit: FileSizeUnit | str = FileSizeUnit.B) -> Self:

		return int.__new__(cls, FileSizeUnit.parse(unit).multiply(size))


	def __repr__(self) -> str:
		value = int(self)
		return f"FileSize({value:,} bytes)"


	def __str__(self) -> str:
		return int.__str__(self)


	@classmethod
	def parse(cls: type[Self], text: str) -> Self:
		"""
			Parse a file size string

			:param text: String representation of a file size
			:raises AttributeError: If the text cannot be parsed
		"""

		size_str, unit = text.strip().split(" ", 1)
		size = float(size_str)
		unit = FileSizeUnit.parse(unit)

		return cls(size, unit)


	def to_optimal_string(self) -> str:
		"""
			Attempts to display the size as the highest whole unit
		"""
		index = 0
		size: int | float = int(self)

		while True:
			if size < 1024 or index == 8:
				unit = FileSizeUnit.from_index(index)
				return f'{size:.2f} {unit}'

			try:
				index += 1
				size = self / FileSizeUnit.from_index(index).multiplier

			except IndexError:
				raise ValueError('File size is too large to convert to a string') from None


	def to_string(self, unit: FileSizeUnit, decimals: int = 2) -> str:
		"""
			Convert to the specified file size unit

			:param unit: Unit to convert to
			:param decimals: Number of decimal points to round to
		"""
		unit = FileSizeUnit.parse(unit)

		if unit == FileSizeUnit.BYTE:
			return f'{self} B'

		size = round(self / unit.multiplier, decimals)
		return f'{size} {unit}'


class JsonBase(dict[str, T]):
	"A ``dict`` with methods to convert to JSON and back"


	@classmethod
	def load(cls: type[Self], path: IO[Any] | Path | str) -> Self:
		"""
			Parse a JSON file at the specified path or from a file descriptor
		"""

		if isinstance(path, IO):
			return cls.parse(path.read())

		with open(path, "rb") as fd:
			return cls.parse(fd.read())


	@classmethod
	def parse(cls: type[Self], data: str | bytes | Mapping[str, T]) -> Self:
		"""
			Parse a JSON object

			:param data: JSON object to parse
			:raises TypeError: When an invalid object type is provided
		"""

		if isinstance(data, (str, bytes)):
			data = json.loads(data)

		if isinstance(data, cls):
			return data

		if not isinstance(data, dict):
			raise TypeError(f"Cannot parse objects of type \"{type(data).__name__}\"")

		return cls(data)


	def dump(self,
			path: IO[Any] | Path | str,
			indent: int | str | None = None,
			**kwargs: Any) -> None:
		"""
			Dump all key/value pairs as JSON data to a path or file descriptor

			:param path: Path or file descriptor to dump to
			:param indent: Number of spaces or the string to use for indention
			:param kwargs: Keyword arguments to pass to :func:`json.dumps`
		"""

		if isinstance(path, IO):
			self.handle_dump_fd(path, indent, **kwargs)
			return

		with open(path, "wb") as fd:
			self.handle_dump_fd(fd, indent, **kwargs)


	def to_json(self, indent: int | str | None = None, **kwargs: Any) -> str:
		"""
			Return the message as a JSON string

			:param indent: Number of spaces or the string to use for indention
			:param kwargs: Keyword arguments to pass to :func:`json.dumps`
		"""

		return json.dumps(self, indent = indent, default = self.handle_value_dump, **kwargs)


	def handle_dump_fd(self, fd: IO[Any], indent: int | str | None = None, **kwargs: Any) -> None:
		data = self.to_json(indent, **kwargs)

		try:
			fd.write(data.encode("utf-8"))

		except TypeError:
			fd.write(data)


	def handle_value_dump(self, value: Any) -> Any:
		"""
			Gets called when a value is of the wrong type and needs to be converted for dumping to
			json. If the type is unknown, it will be forcibly converted to a ``str``.

			:param value: Value to be converted
		"""

		if not isinstance(value, (str, int, float, bool, dict, list, tuple, type(None))):
			# print(f"Warning: Cannot properly convert value of type '{type(value).__name__}'")
			return str(value)

		return value


class LazyImport:
	"""
		Sets up a lazy importer for a module. This adds (or overwrites) ``__getattr__``.

		.. note:: This must be initiated in the root of a module.
	"""

	def __init__(self, **imports: str) -> None:
		"""
			:param imports: The object and import path for each lazy import
			:raises TypeError: When ``global_dict`` doesn't have a ``__package__`` item
		"""

		try:
			frame_globals = currentframe().f_back.f_globals # type: ignore[union-attr]

		except AttributeError:
			raise RuntimeError("Cannot get previous frame")

		self.globals: dict[str, Any] = frame_globals
		self.imports: dict[str, str] = imports

		if "__package__" not in self.globals:
			raise TypeError('Provided globals do not include a __package__ item')

		self.globals["__getattr__"] = self


	def __call__(self, key: str) -> Any:
		try:
			return self.globals[key]

		except KeyError:
			pass

		try:
			return import_module(f"{self.package}.{self.imports[key]}")

		except KeyError:
			raise ImportError(f'Cannot import "{key}" from "{self.package}"') from None


	@property
	def package(self) -> str:
		"Name of the associated module"

		return self.globals["__package__"] # type: ignore[no-any-return]


@dataclass
class RunData:
	"Data returned from :meth:`time_function` and :meth:`time_function_pprint`"

	runs: tuple[float, ...]
	"Elapsed time of each run"

	average: float
	"Average time of all runs"

	total: float
	"Time it took for all runs"


class StaticProperty(Generic[T]):
	"Decorator for turning a static method into a static property"

	def __init__(self, func: Callable[..., T]) -> None:
		"""
			Create a new ``StaticProperty`` object

			:param func: The decorated function
		"""

		self._getter: Callable[[], T] = func
		self._setter: Callable[[Any], None] | None = None


	def __get__(self, obj: Any, cls: Any) -> T:
		return self._getter()


	def __set__(self, obj: Any, value: Any) -> None:
		if self._setter is None:
			raise AttributeError("No setter is set")

		self._setter(value)


	def setter(self, func: Callable[[Any], None]) -> Callable[[Any], None]:
		"""
			Add a function for setting the value

			:param func: Function to decorate
		"""

		self._setter = func
		return func
