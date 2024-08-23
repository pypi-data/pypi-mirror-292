from __future__ import annotations

import os
import re

from collections.abc import Callable, Iterator, Sequence
from typing import TYPE_CHECKING, Any, Generic, TypeVar, get_args, get_origin, overload

from .date import Date
from .errors import GenericError
from .misc import JsonBase, convert_to_boolean, convert_to_string, get_object_name
from .path import File
from .transport import AsyncTransport
from .url import Url

if TYPE_CHECKING:
	try:
		from typing import Self

	except ImportError:
		from typing_extensions import Self


T = TypeVar("T")
BASH_VAR_PARSE = re.compile(
	r"^(?:export )?(?P<key>[a-zA-Z_][a-zA-Z0-9_]*)=(?P<value>.*)$",
	re.MULTILINE
)


ENV_PARSERS = {
	"bool": convert_to_boolean,
	"float": float,
	"int": int,
	"str": str,
	"Date": Date.parse,
	"File": File,
	"JsonBase": JsonBase.parse,
	"Url": Url.parse
}


async def aprint(
				*text: str,
				separator: str = " ",
				newline: bool = True,
				flush: bool = True) -> None:
	"""
		Print some text to stdout.

		:param text: Objects to print out. They will be converted to strings.
		:param separator: Character(s) to use when separating multiple items
		:param newline: Add a newline character to the end of the string
		:param flush: Dump any currently queued data to be sent to stdout
	"""

	stdio = await AsyncTransport.from_stdio()
	data = separator.join(str(item) for item in text).encode(stdio.encoding)

	if newline:
		data += b"\n"

	await stdio.write(data, flush)


async def aprompt(
				prompt: str,
				deserializer: Callable[[str], T] = str, # type: ignore[assignment]
				choices: Sequence[T] | None = None,
				default: T | None = None) -> T:
	"""
		Ask the user for a response to a question via stdout (async-friendly). Returns a
		:class:`str` by default.

		:param prompt: Text to display to the user
		:param deserializer: Function that converts the response to the correct type
		:param choices: Only valid replies if set
		:param default: Value to return if a user doesn't provide an answer
	"""

	if choices is not None and default is not None and default not in choices:
		raise ValueError("Default value not in available choices")

	trans = await AsyncTransport.from_stdio(timeout = 0)
	prompt_text = _prompt_line(prompt, choices, default)

	while True:
		await trans.write(prompt_text)

		try:
			return _prompt_parse(
				(await trans.readline()).decode("utf-8"), deserializer, choices, default
			)

		except GenericError as error:
			if error == GenericError.Prompt:
				await aprint(f"\nERROR: {error.message}")
				continue

			raise


def prompt(
		prompt: str,
		deserializer: Callable[[str], T] = str, # type: ignore[assignment]
		choices: Sequence[T] | None = None,
		default: T | None = None) -> T:
	"""
		Ask the user for a response to a question via stdout. Returns a :class:`str` by default.

		:param prompt: Text to display to the user
		:param deserializer: Function that converts the response to the correct type
		:param choices: Only valid replies if set
		:param default: Value to return if a user doesn't provide an answer
	"""

	if choices is not None and default is not None and default not in choices:
		raise ValueError("Default value not in available choices")

	prompt_text = _prompt_line(prompt, choices, default)

	while True:
		try:
			return _prompt_parse(
				input(prompt_text), deserializer, choices, default
			)

		except GenericError as error:
			if error == GenericError.Prompt:
				print(f"\nERROR: {error.message}")
				continue

			raise


def _prompt_line(
				prompt: str,
				choices: Sequence[T] | None = None,
				default: Any = None) -> str:

	line2 = f"[{default}]: " if default is not None else ": "

	if choices is not None:
		str_choices = ", ".join(str(c) for c in choices)
		return f"{prompt} [{str_choices}]\n{line2}"

	return f"{prompt}\n{line2}"


def _prompt_parse(
				raw_value: str,
				deserializer: Callable[[str], T] = str, # type: ignore[assignment]
				choices: Sequence[T] | None = None,
				default: T | None = None) -> T:

	if (raw_value := raw_value.strip()) == "":
		if default is None:
			raise GenericError.Prompt("No response")

		return default

	value = deserializer(raw_value)

	if choices is not None and value not in choices:
		raise GenericError.Prompt("Not a valid choice")

	return value


class Env:
	"Easy access to environmental variables"


	@staticmethod
	def get(key: str,
			default: T | None = None,
			converter: Callable[[str], T] = str) -> T: # type: ignore[assignment]
		"""
			Get an environmental variable

			:param key: Name of the variable
			:param default: The default value to return if the key is not found
			:param converter: Function to convert the value to a different type
		"""

		try:
			return converter(os.environ[key])

		except KeyError:
			if default is None:
				raise

			return default


	@staticmethod
	def set(key: str, value: Any, converter: Callable[[Any], str] = convert_to_string) -> None:
		os.environ[key] = converter(value)


	@staticmethod
	def delete(key: str) -> None:
		"""
			Remove an environmental variable

			:param key: Name of the variable to delete
		"""

		del os.environ[key]


	@classmethod
	def get_array(cls: type[Self],
				key: str,
				separator: str = ",",
				converter: Callable[[str], Any] = str) -> Iterator[Any]:
		"""
			Get an environmental variable as an iterator of items

			:param key: Name of the variable
			:param separator: String to use to split items
			:param converter: Function to convert each value to a different type
		"""

		for value in cls.get(key, "").split(separator):
			yield (converter(value.strip()))


	@classmethod
	def get_int(cls: type[Self], key: str, default: int = 0) -> int:
		"""
			Get an environmental variable as an ``int``

			:param key: Name of the variable
			:param default: The default value to return if the key is not found
		"""

		return cls.get(key, default, int)


	@classmethod
	def get_float(cls: type[Self], key: str, default: float = 0.0) -> float:
		"""
			Get an environmental variable as a ``float``

			:param key: Name of the variable
			:param default: The default value to return if the key is not found
		"""

		return cls.get(key, default, float)


	@classmethod
	def get_bool(cls: type[Self], key: str, default: bool = False) -> bool:
		"""
			Get an environmental variable as a ``bool``

			:param key: Name of the variable
			:param default: The default value to return if the key is not found
		"""

		return cls.get(key, default, convert_to_boolean)


	@classmethod
	def get_json(cls: type[Self], key: str, default: JsonBase[T] | None = None) -> JsonBase[T]:
		"""
			Get an environmental variable as a JSON-parsed ``dict``

			:param key: Name of the variable
			:param default: The default value to return if the key is not found
		"""

		return cls.get(key, default, JsonBase.parse)


	@classmethod
	def get_list(cls: type[Self],
				key: str,
				separator: str = ",",
				converter: Callable[[str], T] = str) -> list[T]: # type: ignore[assignment]
		"""
			Get an environmental variable as a ``list``

			:param key: Name of the variable
			:param separator: String to use to split items
			:param converter: Function to convert each value to a different type
		"""

		return list(cls.get_array(key, separator, converter))


	@classmethod
	def keys(cls: type[Self]) -> Iterator[str]:
		"Fetch all environmental variable names"

		for key in os.environ:
			yield key


	@classmethod
	def items(cls: type[Self]) -> Iterator[tuple[str, str]]:
		"Fetch all environmental variable names and values"

		for key in os.environ:
			yield key, os.environ[key]


	@classmethod
	def values(cls: type[Self]) -> Iterator[str]:
		"Fetch all environmental variable values"

		for value in os.environ.values():
			yield value


	@classmethod
	def load_env(cls: type[Self], path: File | str) -> None:
		"""
			Load a bash-like file with key/value pairs into the environment

			.. note:: The env file is not parsed by bash at all. It should be treated as a simple
				key/value pair store.

			:param path: Path to the file to load
		"""

		path = File(path)

		for key, value in BASH_VAR_PARSE.findall(path.read_text()):
			cls.set(key, value.lstrip('"').rstrip('"'))


class EnvConfigProperty(Generic[T]):
	"Represents an environmental variable on an :class:`EnvConfig` object."

	key: str


	def __init__(self, key: str | None = None, converter: Callable[[str], T] | None = None) -> None:
		"""
			Create a new ``EnvConfigProperty`` object

			.. note:: If :data:`__future__.annotations` is not imported in the same file as the parent
				class, then :class:`list` annotations will not be parsed correctly.

			:param key: Name of the environmental variable to query. If not specified, the property
				name in uppercase form will be used instead.
			:param converter: Function to convert the value from a :class:`str`. If not specified,
				the converter will be determined from the annotation.
		"""
		if key is not None:
			self.key = key

		self.converter: Callable[[str], T] | None = converter
		self.is_list: bool = False


	def __set_name__(self, obj: EnvConfig, key: str) -> None:
		if not hasattr(self, "key"):
			self.key = key.upper()

		if self.converter is None:
			raw_vtype = obj.__annotations__[key]
			vtype = ""

			if not isinstance(raw_vtype, str):
				if get_origin(raw_vtype) is list:
					self.is_list = True

					try:
						vtype = get_object_name(get_args(raw_vtype)[0])

					except (IndexError, AttributeError):
						vtype = "str"

				else:
					vtype = get_object_name(get_origin(raw_vtype))

			else:
				# if __future__.annotations was not imported, list generics get excluded
				vtype = raw_vtype.replace("EnvConfigProperty", "", 1).strip("[]")

				if vtype.startswith("list"):
					self.is_list = True
					vtype = vtype.replace("list", "", 1).strip("[]") or "str"

			self.converter = ENV_PARSERS[vtype] # type: ignore[assignment]


	@overload
	def __get__(self, obj: EnvConfig, cls: Any) -> T:
		...


	@overload
	def __get__(self, obj: None, cls: Any) -> Self:
		...


	def __get__(self, obj: EnvConfig | None, cls: Any) -> T | Self:
		if obj is None:
			return self

		if self.key in obj._cache:
			return obj._cache[self.key] # type: ignore[no-any-return]

		if self.is_list:
			return Env.get_list(self.key, converter = self.converter or str) # type: ignore[return-value]

		return Env.get(self.key, converter = self.converter or str) # type: ignore[return-value]


	def __set__(self, obj: EnvConfig, value: T) -> None:
		Env.set(self.key, value)


	def __delete__(self, obj: EnvConfig) -> None:
		Env.delete(self.key)


class EnvConfigMeta(type):
	def __new__(cls: type,
				name: str,
				bases: Sequence[type[Any]],
				properties: dict[str, Any]) -> type:

		new_annotations = {}
		properties["_props"] = []

		for key, vtype in properties.get("__annotations__", {}).items():
			if key.startswith("_"):
				continue

			if key in properties:
				properties["_props"].append(key)
				continue

			if not isinstance(vtype, str):
				vtype = get_object_name(vtype)

			properties[key] = EnvConfigProperty()
			properties["_props"].append(key)
			new_annotations[key] = f"EnvConfigProperty[{vtype}]"

		properties["__annotations__"] = new_annotations
		return type.__new__(cls, name, tuple(bases), properties)


class EnvConfig(metaclass = EnvConfigMeta):
	"""
		Class to use for easy processing of specific environmental variables. Sub-class this class
		and add annotations just like a :meth:`dataclasses.dataclass`.
	"""

	slots: tuple[str, ...] = ("_cache", "_props")
	_props: list[str]


	def __init__(self, path: File | str | None) -> None:
		"""
			Create a new ``EnvConfig`` object

			:param path: Optional env file to load
		"""

		self._cache: dict[str, Any] = {}

		if path is not None:
			Env.load_env(path)


	def __repr__(self) -> str:
		prop_str = ", ".join(f"{key}={repr(getattr(self, key))}" for key in self._props)
		return f"{get_object_name(self)}({prop_str})"


	def clear_cache(self) -> None:
		"Clear the internal value cache"

		self._cache.clear()
