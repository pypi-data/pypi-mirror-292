from dataclasses import dataclass
from typing import Any, Callable, Dict, Generic, Optional, TypeVar
from pluto_base.resource import (
    IResource,
    IResourceCapturedProps,
    IResourceInfraApi,
    IResourceClientApi,
)
from pluto_base.platform import PlatformType
from pluto_base import utils
from .utils import create_simulator_client


DEFAULT_FUNCTION_NAME = "default"

FnHandler = TypeVar("FnHandler", bound=Callable[..., Any])


@dataclass
class DirectCallResponse:
    code: int
    body: Any


@dataclass
class FunctionOptions:
    memory: int | None = 128  # The memory size in MB, default is 128.
    envs: Dict[str, Any] | None = None
    raw: bool = False  # This option only works for the AWS currently.


class IFunctionClientApi(Generic[FnHandler], IResourceClientApi):
    def invoke(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError


class IFunctionInfraApi(IResourceInfraApi):
    pass


class IFunctionCapturedProps(IResourceCapturedProps):
    def url(self) -> str:
        raise NotImplementedError


class IFunctionClient(IFunctionClientApi[FnHandler], IFunctionCapturedProps):
    pass


class IFunctionInfra(IFunctionInfraApi, IFunctionCapturedProps):
    pass


class Function(IResource, IFunctionClient[FnHandler], IFunctionInfra):
    fqn = "@plutolang/pluto.Function"

    def __init__(
        self,
        func: FnHandler,
        name: Optional[str] = None,
        opts: Optional[FunctionOptions] = None,
    ):
        name = name or DEFAULT_FUNCTION_NAME

        platform_type = utils.current_platform_type()
        if platform_type == PlatformType.AWS:
            from .clients import aws

            self._client = aws.LambdaFunction(func, name, opts)

        elif platform_type == PlatformType.Simulator:
            resource_id = utils.gen_resource_id(Function.fqn, name)
            self._client = create_simulator_client(resource_id)  # type: ignore

        else:
            raise ValueError(f"not support this runtime '{platform_type}'")
