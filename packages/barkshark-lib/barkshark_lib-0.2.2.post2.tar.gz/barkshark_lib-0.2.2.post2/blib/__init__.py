__software__ = "Barkshark Lib"
__version_info__ = (0, 2, 2)
__version__ = ".".join(str(v) for v in __version_info__) + ".post2"
__author__ = "Zoey Mae"
__homepage__ = "https://git.barkshark.xyz/barkshark/blib"


from .application import (
	Application
)

from .date import (
	Date,
	HttpDate
)

from .enums import (
	Enum,
	IntEnum,
	IntFlagEnum,
	StrEnum,
	FilePermField,
	FileSizeUnit,
	FileType,
	HttpMethod,
	HttpStatus,
	Platform,
	PridePalette,
	ProtocolPort,
	SeekPosition,
	XdgDir
)

from .errors import (
	Error,
	ErrorCode,
	ErrorMeta,
	FileError,
	GenericError,
	HttpError
)

# from .http_client import (
# 	HttpClient,
# 	HttpConnection,
# 	HttpForm,
# 	HttpFormItem,
# 	HttpResponse
# )

from .misc import (
	catch_errors,
	convert_to_boolean,
	convert_to_bytes,
	convert_to_string,
	deprecated,
	get_object_name,
	get_object_properties,
	get_resource_path,
	get_top_domain,
	http_request,
	is_loop_running,
	port_check,
	random_port,
	random_str,
	set_signal_handler,
	time_function,
	time_function_pprint,
	ClassProperty,
	Color,
	DictProperty,
	FileSize,
	JsonBase,
	LazyImport,
	RunData,
	StaticProperty
)

from .objects import (
	Object,
	Property,
	Signal,
	SignalObj
)

from .path import (
	AsyncFile,
	File,
	Path,
	UnixPerms
)

from .termutils import (
	Env,
	EnvConfig,
	EnvConfigProperty,
	aprint,
	aprompt,
	prompt
)

from .transport import (
	AsyncTransport
)

from .url import (
	Query,
	Url,
	open_url
)
