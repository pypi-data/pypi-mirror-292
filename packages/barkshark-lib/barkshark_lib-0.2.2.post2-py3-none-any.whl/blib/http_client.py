from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Generator
from contextlib import contextmanager
from http.client import HTTPConnection, HTTPResponse
from http.client import _create_https_context # type: ignore[attr-defined]
from typing import Any, Self
from urllib.parse import quote

from . import __version__
from .enums import HttpMethod
from .misc import JsonBase, convert_to_bytes, random_str
from .path import File
from .url import Url


class HttpClient:
	def __init__(self,
				useragent: str | None = None,
				headers: dict[str, str] | None = None,
				timeout: int = 60) -> None:

		self.timeout: int = timeout

		self._headers: dict[str, str] = {
			"User-Agent": useragent or f"BarksharkLib/{__version__}"
		}

		for key, value in (headers or {}).items():
			self.add_header(key, value)


	@property
	def useragent(self) -> str:
		return self._headers["User-Agent"]


	@useragent.setter
	def useragent(self, value: str) -> None:
		self._headers["User-Agent"] = value


	def add_header(self, key: str, value: str) -> None:
		self._headers[key.title()] = value


	def get_header(self, key: str, default: str | None = None) -> str | None:
		return self._headers.get(key.title(), default)


	def del_header(self, key: str) -> None:
		del self._headers[key.title()]


	@contextmanager
	def request(self,
				method: HttpMethod | str,
				url: Url | str,
				data: Any = None,
				headers: dict[str, str] | None = None) -> Generator[HttpResponse, None, None]:

		method = HttpMethod.parse(method)

		if not isinstance(url, Url):
			url = Url.parse(url)

		if url.proto not in ("http", "https"):
			raise ValueError(f"Unsupported protocol: {url.proto}")

		with HttpConnection(self, url.domain, url.port, url.proto == "https") as conn:
			conn.request(method, url, data, headers)
			yield conn.get_response()


class HttpResponse(HTTPResponse):
	client: HttpClient


	@property
	def content_length(self) -> int:
		return int(self.headers.get("Content-Length", "0"))


	@property
	def content_type(self) -> str | None:
		return self.headers.get("Content-Type")


	def text(self) -> str:
		return self.read().decode("utf-8")


	def json(self, cls: type[JsonBase[Any]] = JsonBase) -> JsonBase[Any]:
		return JsonBase.parse(self.read())


class HttpConnection(HTTPConnection):
	auto_open = 0
	response_class = HttpResponse


	def __init__(self, client: HttpClient, domain: str, port: int, https: bool = True) -> None:
		HTTPConnection.__init__(self, domain, port, timeout = client.timeout)

		if https:
			self.default_port = 443

		self.client: HttpClient = client
		self._context = None

		if https:
			self._context = _create_https_context(self._http_vsn) # type: ignore[attr-defined]


	def __enter__(self) -> Self:
		self.connect()
		return self


	def __exit__(self, *_: Any) -> None:
		self.disconnect()


	def connect(self) -> None:
		if self.sock is not None:
			return

		HTTPConnection.connect(self)

		if self._context is not None:
			self.sock = self._context.wrap_socket(self.sock, server_hostname = self.host)


	def disconnect(self) -> None:
		self.close()


	def request(self, # type: ignore[override]
				method: str,
				url: Url,
				data: Any = None,
				headers: dict[str, str] | None = None) -> None:

		if url.proto not in ("http", "https"):
			raise ValueError(f"Unsupported protocol: {url.proto}")

		new_headers = self.client._headers.copy()
		new_headers.update({key.title(): value for key, value in (headers or {}).items()})

		if isinstance(data, HttpForm):
			body = data.to_bytes()

			if "Content-Type" not in new_headers:
				new_headers["Content-Type"] = f"multipart/form-data; boundry={data.boundry}"

		else:
			body = convert_to_bytes(data)

		new_headers["Content-Length"] = str(len(body))
		HTTPConnection.request(self, method, url, body, new_headers)


	def getresponse(self) -> None: # type: ignore[override]
		raise NotImplementedError("Use get_response instead")


	def get_response(self) -> HttpResponse:
		resp: HttpResponse = HTTPConnection.getresponse(self) # type: ignore[assignment]
		resp.client = self.client

		return resp


@dataclass(slots = True)
class HttpFormItem:
	key: str
	value: bytes | File
	content_type: str = "text/plain"
	charset: str = "utf-8"


	def to_bytes(self) -> bytes:
		if isinstance(self.value, File):
			data = self.value.read()

		else:
			data = self.value

		header: list[str] = []

		if isinstance(self.value, File):
			header.append(
				f"Content-Disposition: form-data; name=\"{quote(self.key)}\";"
				f" filename=\"{quote(self.value.name)}\""
			)

		else:
			header.append(f"Content-Disposition: form-data; name=\"{quote(self.key)}\";")

		header.append(f"Content-Type: {self.content_type}; charset={self.charset}")
		header_bytes = ("\r\n".join(header)).encode(self.charset)

		return header_bytes + b"\r\n\r\n" + data + b"\r\n--"


class HttpForm(list[tuple[str, HttpFormItem]]):
	def __init__(self,
				data: dict[str, str | bytes | File] | None = None,
				boundry: str | None = None,
				charset: str = "utf-8") -> None:

		list.__init__(self, [])

		self.boundry: str = boundry or random_str()
		self.default_charset: str = charset

		for key, value in (data or {}).items():
			self.add_value(key, value)


	def add_value(self,
				key: str,
				value: bytes | str | File,
				content_type: str = "text/plain",
				charset: str | None = None) -> HttpFormItem:

		if not isinstance(value, (bytes, File)):
			value = convert_to_bytes(value)

		item = HttpFormItem(key, value, content_type, charset or self.default_charset)
		self.append((key, item))

		return item


	def to_bytes(self) -> bytes:
		boundry = b"--" + self.boundry.encode(self.default_charset) + b"\r\n"
		form_data = b"".join(value.to_bytes() for key, value in self)
		return boundry + form_data + boundry
