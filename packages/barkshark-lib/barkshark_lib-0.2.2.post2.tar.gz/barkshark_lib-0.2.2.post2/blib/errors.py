from __future__ import annotations

import inspect

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, ParamSpec

from .enums import HttpStatus

if TYPE_CHECKING:
	try:
		from typing import Self

	except ImportError:
		from typing_extensions import Self


P = ParamSpec("P")


class ErrorCode(int):
	"Represents an error code for an error domain"

	name: str
	"Name of the error code"


	def __init__(self, code: int, name: str | None = None, cls: type[Error] | None = None):
		self._cls: type[Error] | None = cls

		if name is not None:
			self.name = name


	def __new__(cls: type[Self], code: int) -> Self:
		return int.__new__(cls, code)


	def __set_name__(self, cls: Any, name: str) -> None:
		self.name = name
		self._cls = cls


	def __repr__(self) -> str:
		return f"ErrorCode(code={int.__repr__(self)}, name={repr(self.name)})"


	def __call__(self, message: str, *args: P.args, **kwargs: P.kwargs) -> Error:
		"""
			Create a new error for the specified error code

			:param message: Text to pass with the error
			:param args: Positional arguments to pass to the error class
			:param kwargs: Keyword arguments to pass to the error class
		"""

		if self._cls is None:
			raise ValueError("Class is null")

		return self._cls(self, message, *args, **kwargs)


class ErrorMeta(type):
	"Meta class that sets all integer properties to :class:`ErrorCode` objects"

	def __new__(meta_cls: type,
				name: str,
				bases: Sequence[type[Any]],
				properties: dict[str, Any]) -> type:

		if "__annotations__" not in properties:
			properties["__annotations__"] = {}

		for key in properties:
			if key.startswith("_"):
				continue

			if isinstance(value := properties[key], int):
				properties[key] = ErrorCode(value)
				properties["__annotations__"][key] = "ErrorCode"

		return type.__new__(type, name, tuple(bases), properties)


class Error(Exception, metaclass = ErrorMeta):
	"Base error class"


	def __init__(self, code: ErrorCode | int, message: str):
		"""
			Create a new error object

			:param code: Number of the error
			:param message: Text to pass with the error
		"""

		if not isinstance(code, ErrorCode):
			code = ErrorCode(code, "Unknown", type(self))

		Exception.__init__(self, f"[{code.name}] {message}")

		self.code: ErrorCode = code
		"Code of the error"

		self.message: str = message
		"User-readable description of the error"


	def __eq__(self, other: type[Error] | Error | ErrorCode | int) -> bool: # type: ignore[override]
		if inspect.isclass(other):
			return type(self) == other # noqa: E721

		if isinstance(other, Error):
			return self.__class__ == other.__class__

		if isinstance(other, (ErrorCode | int)):
			for key in dir(type(self)):
				value = getattr(self, key)

				if other == value:
					return True

		return False


	@property
	def domain(self) -> str:
		"Name of the error group"

		return self.__class__.__name__


class FileError(Error):
	"Raised on errors involving files"

	NotFound: ErrorCode = ErrorCode(0)
	"Raised when a file or directory could not be found"

	Found: ErrorCode = ErrorCode(1)
	"Raised when a file or directory exists when it should not"

	IsDirectory: ErrorCode = ErrorCode(2)
	"Raised when the path is a directory when it should not be"

	IsFile: ErrorCode = ErrorCode(3)
	"Raised when the path is a file when it should not be"

	InvalidType: ErrorCode = ErrorCode(4)
	"Raised when the path is not the correct inode type"

	NotRelated: ErrorCode = ErrorCode(5)
	"Raised when a path does not share a base with another path"


class GenericError(Error):
	"Various uncategorized errors"

	Prompt: ErrorCode = ErrorCode(0)
	"Raised when there was an error with the return value from a prompt"

	Parse: ErrorCode = ErrorCode(1)
	"Raised when data cannot be parsed"


class HttpError(Error):
	"Error raised from a client or server response"


	Continue: ErrorCode = ErrorCode(100)
	SwitchingProtocols: ErrorCode = ErrorCode(101)
	Processing: ErrorCode = ErrorCode(102)
	EarlyHints: ErrorCode = ErrorCode(103)

	Ok: ErrorCode = ErrorCode(200)
	Created: ErrorCode = ErrorCode(201)
	Accepted: ErrorCode = ErrorCode(202)
	NonAuthoritativeInformation: ErrorCode = ErrorCode(203)
	NoContent: ErrorCode = ErrorCode(204)
	ResetContent: ErrorCode = ErrorCode(205)
	PartialContent: ErrorCode = ErrorCode(206)
	MultiStatus: ErrorCode = ErrorCode(207)
	AlreadyReported: ErrorCode = ErrorCode(208)
	ImUsed: ErrorCode = ErrorCode(226)

	MultipleChoices: ErrorCode = ErrorCode(300)
	MovedPermanently: ErrorCode = ErrorCode(301)
	Found: ErrorCode = ErrorCode(302)
	SeeOther: ErrorCode = ErrorCode(303)
	NotModified: ErrorCode = ErrorCode(304)
	UseProxy: ErrorCode = ErrorCode(305)
	TemporaryRedirect: ErrorCode = ErrorCode(307)
	PermanentRedirect: ErrorCode = ErrorCode(308)

	BadRequest: ErrorCode = ErrorCode(400)
	Unauthorized: ErrorCode = ErrorCode(401)
	PaymentRequired: ErrorCode = ErrorCode(402)
	Forbidden: ErrorCode = ErrorCode(403)
	NotFound: ErrorCode = ErrorCode(404)
	MethodNotAllowed: ErrorCode = ErrorCode(405)
	NotAcceptable: ErrorCode = ErrorCode(406)
	ProxyAuthenticationRequired: ErrorCode = ErrorCode(407)
	RequestTimeout: ErrorCode = ErrorCode(408)
	Conflict: ErrorCode = ErrorCode(409)
	Gone: ErrorCode = ErrorCode(410)
	LengthRequired: ErrorCode = ErrorCode(411)
	PreconditionFailed: ErrorCode = ErrorCode(412)
	RequestEntityTooLarge: ErrorCode = ErrorCode(413)
	RequestUriTooLong: ErrorCode = ErrorCode(414)
	UnsupportedMediaType: ErrorCode = ErrorCode(415)
	RequestRangeNotSatisfiable: ErrorCode = ErrorCode(416)
	ExpectationFailed: ErrorCode = ErrorCode(417)
	Teapot: ErrorCode = ErrorCode(418)
	EnhanceYourCalm: ErrorCode = ErrorCode(420)
	MisdirectedRequest: ErrorCode = ErrorCode(421)
	UnprocessableEntity: ErrorCode = ErrorCode(422)
	Locked: ErrorCode = ErrorCode(423)
	FailedDependency: ErrorCode = ErrorCode(424)
	TooEarly: ErrorCode = ErrorCode(425)
	UpgradeRequired: ErrorCode = ErrorCode(426)
	PreconditionRequired: ErrorCode = ErrorCode(428)
	TooManyRequests: ErrorCode = ErrorCode(429)
	RequestHeaderFieldsTooLarge: ErrorCode = ErrorCode(431)
	UnavailableForLegalReasons: ErrorCode = ErrorCode(451)

	InternalServerError: ErrorCode = ErrorCode(500)
	NotImplemented: ErrorCode = ErrorCode(501)
	BadGateway: ErrorCode = ErrorCode(502)
	ServiceUnavailable: ErrorCode = ErrorCode(503)
	GatewayTimeout: ErrorCode = ErrorCode(504)
	HttpVersionNotSupported: ErrorCode = ErrorCode(505)
	VariantAlsoNegotiates: ErrorCode = ErrorCode(506)
	InsufficientStorage: ErrorCode = ErrorCode(507)
	LoopDetected: ErrorCode = ErrorCode(508)
	NotExtended: ErrorCode = ErrorCode(510)
	NetworkAuthenticationRequired: ErrorCode = ErrorCode(511)


	def __init__(self,
				status: HttpStatus | ErrorCode | int,
				message: str | None = None,
				location: str | None = None,
				headers: dict[str, str] | None = None) -> None:
		"""
			Create a new http error

			:param status: Status code of the error
			:param message: Body of the error
			:param headers: Headers of the error
		"""

		self._status = HttpStatus.parse(status)

		if not isinstance(status, ErrorCode):
			status = ErrorCode(self._status.value, self._status.reason.replace(" ", ""), type(self))

		Error.__init__(self, status, "")

		self.headers: dict[str, str] = {}
		"Headers associated with the error"

		self.message = message or self.status.reason

		if headers:
			self.headers = {key: value.title() for key, value in headers.items()}

		if location is not None:
			self.location = location

		if not self.location and self._status in {301, 302, 303, 307, 308}:
			raise ValueError("Location header is not set")


	def __str__(self) -> str:
		return f"HTTP Error {self.status}: {self.message}"


	def __repr__(self) -> str:
		return f"HttpError(status={self.status}, message='{self.message}')"


	@property
	def location(self) -> str:
		return self.headers.get("Location", "")


	@location.setter
	def location(self, value: str) -> None:
		self.headers["Location"] = value


	@property
	def reason(self) -> str:
		return self._status.reason


	@property
	def status(self) -> HttpStatus:
		"HTTP status code"

		return self._status
