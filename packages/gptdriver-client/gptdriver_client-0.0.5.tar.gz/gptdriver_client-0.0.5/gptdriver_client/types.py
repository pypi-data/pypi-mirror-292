from pydantic import BaseModel
from typing import Optional, List, Any, Literal, Callable, Awaitable


class Command(BaseModel):
    method: Literal['GET', 'DELETE', 'POST']
    url: str
    data: Any


class ExecuteResponse(BaseModel):
    commands: List[Command]
    status: Literal['inProgress', 'success', 'failed']


class DeviceSize(BaseModel):
    width: int
    height: int


AppiumHandler = Callable[[Any], Awaitable[Any]]


class AppiumServerConfig(BaseModel):
    port: int
    host: str


class AppiumSessionConfig(BaseModel):
    id: Optional[str] = None
    platform: Literal['iOS', 'Android']
    device_name: Optional[str] = None
    platform_version: Optional[str] = None
    size: Optional[DeviceSize] = None
    appium_server_config: Optional[AppiumServerConfig] = None


class AppiumSessionInitConfig(BaseModel):
    platform: Literal['iOS', 'Android']
    device_name: Optional[str] = None
    platform_version: Optional[str] = None
