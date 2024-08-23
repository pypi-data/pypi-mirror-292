import enum
import modal.functions
import modal_proto.api_pb2
import typing
import typing_extensions

class _PartialFunctionFlags(enum.IntFlag):
    FUNCTION: int = 1
    BUILD: int = 2
    ENTER_PRE_SNAPSHOT: int = 4
    ENTER_POST_SNAPSHOT: int = 8
    EXIT: int = 16
    BATCHED: int = 32

    @staticmethod
    def all() -> int:
        return ~_PartialFunctionFlags(0)

P = typing_extensions.ParamSpec("P")

R = typing.TypeVar("R", covariant=True)

class _PartialFunction(typing.Generic[P, R]):
    raw_f: typing.Callable[P, R]
    flags: _PartialFunctionFlags
    webhook_config: typing.Optional[modal_proto.api_pb2.WebhookConfig]
    is_generator: typing.Optional[bool]
    keep_warm: typing.Optional[int]
    batch_max_size: typing.Optional[int]
    batch_wait_ms: typing.Optional[int]

    def __init__(
        self,
        raw_f: typing.Callable[P, R],
        flags: _PartialFunctionFlags,
        webhook_config: typing.Optional[modal_proto.api_pb2.WebhookConfig] = None,
        is_generator: typing.Optional[bool] = None,
        keep_warm: typing.Optional[int] = None,
        batch_max_size: typing.Optional[int] = None,
        batch_wait_ms: typing.Optional[int] = None,
    ): ...
    def __get__(self, obj, objtype=None) -> modal.functions._Function[P, R]: ...
    def __del__(self): ...
    def add_flags(self, flags) -> _PartialFunction: ...

class PartialFunction(typing.Generic[P, R]):
    raw_f: typing.Callable[P, R]
    flags: _PartialFunctionFlags
    webhook_config: typing.Optional[modal_proto.api_pb2.WebhookConfig]
    is_generator: typing.Optional[bool]
    keep_warm: typing.Optional[int]
    batch_max_size: typing.Optional[int]
    batch_wait_ms: typing.Optional[int]

    def __init__(
        self,
        raw_f: typing.Callable[P, R],
        flags: _PartialFunctionFlags,
        webhook_config: typing.Optional[modal_proto.api_pb2.WebhookConfig] = None,
        is_generator: typing.Optional[bool] = None,
        keep_warm: typing.Optional[int] = None,
        batch_max_size: typing.Optional[int] = None,
        batch_wait_ms: typing.Optional[int] = None,
    ): ...
    def __get__(self, obj, objtype=None) -> modal.functions.Function[P, R]: ...
    def __del__(self): ...
    def add_flags(self, flags) -> PartialFunction: ...

def _find_partial_methods_for_user_cls(
    user_cls: typing.Type[typing.Any], flags: int
) -> typing.Dict[str, _PartialFunction]: ...
def _find_callables_for_cls(
    user_cls: typing.Type[typing.Any], flags: int
) -> typing.Dict[str, typing.Callable[..., typing.Any]]: ...
def _find_callables_for_obj(user_obj: typing.Any, flags: int) -> typing.Dict[str, typing.Callable[..., typing.Any]]: ...
def _method(
    _warn_parentheses_missing=None,
    *,
    is_generator: typing.Optional[bool] = None,
    keep_warm: typing.Optional[int] = None,
) -> typing.Callable[[typing.Callable[typing_extensions.Concatenate[typing.Any, P], R]], _PartialFunction[P, R]]: ...
def _parse_custom_domains(
    custom_domains: typing.Optional[typing.Iterable[str]] = None,
) -> typing.List[modal_proto.api_pb2.CustomDomainConfig]: ...
def _web_endpoint(
    _warn_parentheses_missing=None,
    *,
    method: str = "GET",
    label: typing.Optional[str] = None,
    docs: bool = False,
    wait_for_response: bool = True,
    custom_domains: typing.Optional[typing.Iterable[str]] = None,
) -> typing.Callable[[typing.Callable[P, R]], _PartialFunction[P, R]]: ...
def _asgi_app(
    _warn_parentheses_missing=None,
    *,
    label: typing.Optional[str] = None,
    wait_for_response: bool = True,
    custom_domains: typing.Optional[typing.Iterable[str]] = None,
) -> typing.Callable[[typing.Callable[..., typing.Any]], _PartialFunction]: ...
def _wsgi_app(
    _warn_parentheses_missing=None,
    *,
    label: typing.Optional[str] = None,
    wait_for_response: bool = True,
    custom_domains: typing.Optional[typing.Iterable[str]] = None,
) -> typing.Callable[[typing.Callable[..., typing.Any]], _PartialFunction]: ...
def _web_server(
    port: int,
    *,
    startup_timeout: float = 5.0,
    label: typing.Optional[str] = None,
    custom_domains: typing.Optional[typing.Iterable[str]] = None,
) -> typing.Callable[[typing.Callable[..., typing.Any]], _PartialFunction]: ...
def _disallow_wrapping_method(f: _PartialFunction, wrapper: str) -> None: ...
def _build(
    _warn_parentheses_missing=None,
) -> typing.Callable[[typing.Union[typing.Callable[[typing.Any], typing.Any], _PartialFunction]], _PartialFunction]: ...
def _enter(
    _warn_parentheses_missing=None, *, snap: bool = False
) -> typing.Callable[[typing.Union[typing.Callable[[typing.Any], typing.Any], _PartialFunction]], _PartialFunction]: ...
def _exit(
    _warn_parentheses_missing=None,
) -> typing.Callable[
    [
        typing.Union[
            typing.Callable[
                [typing.Any, typing.Optional[typing.Type[BaseException]], typing.Optional[BaseException], typing.Any],
                None,
            ],
            typing.Callable[[typing.Any], None],
        ]
    ],
    _PartialFunction,
]: ...
def _batched(
    _warn_parentheses_missing=None, *, max_batch_size: int, wait_ms: int
) -> typing.Callable[[typing.Callable[..., typing.Any]], _PartialFunction]: ...
def method(
    _warn_parentheses_missing=None,
    *,
    is_generator: typing.Optional[bool] = None,
    keep_warm: typing.Optional[int] = None,
) -> typing.Callable[[typing.Callable[typing_extensions.Concatenate[typing.Any, P], R]], PartialFunction[P, R]]: ...
def web_endpoint(
    _warn_parentheses_missing=None,
    *,
    method: str = "GET",
    label: typing.Optional[str] = None,
    docs: bool = False,
    wait_for_response: bool = True,
    custom_domains: typing.Optional[typing.Iterable[str]] = None,
) -> typing.Callable[[typing.Callable[P, R]], PartialFunction[P, R]]: ...
def asgi_app(
    _warn_parentheses_missing=None,
    *,
    label: typing.Optional[str] = None,
    wait_for_response: bool = True,
    custom_domains: typing.Optional[typing.Iterable[str]] = None,
) -> typing.Callable[[typing.Callable[..., typing.Any]], PartialFunction]: ...
def wsgi_app(
    _warn_parentheses_missing=None,
    *,
    label: typing.Optional[str] = None,
    wait_for_response: bool = True,
    custom_domains: typing.Optional[typing.Iterable[str]] = None,
) -> typing.Callable[[typing.Callable[..., typing.Any]], PartialFunction]: ...
def web_server(
    port: int,
    *,
    startup_timeout: float = 5.0,
    label: typing.Optional[str] = None,
    custom_domains: typing.Optional[typing.Iterable[str]] = None,
) -> typing.Callable[[typing.Callable[..., typing.Any]], PartialFunction]: ...
def build(
    _warn_parentheses_missing=None,
) -> typing.Callable[[typing.Union[typing.Callable[[typing.Any], typing.Any], PartialFunction]], PartialFunction]: ...
def enter(
    _warn_parentheses_missing=None, *, snap: bool = False
) -> typing.Callable[[typing.Union[typing.Callable[[typing.Any], typing.Any], PartialFunction]], PartialFunction]: ...
def exit(
    _warn_parentheses_missing=None,
) -> typing.Callable[
    [
        typing.Union[
            typing.Callable[
                [typing.Any, typing.Optional[typing.Type[BaseException]], typing.Optional[BaseException], typing.Any],
                None,
            ],
            typing.Callable[[typing.Any], None],
        ]
    ],
    PartialFunction,
]: ...
def batched(
    _warn_parentheses_missing=None, *, max_batch_size: int, wait_ms: int
) -> typing.Callable[[typing.Callable[..., typing.Any]], PartialFunction]: ...
