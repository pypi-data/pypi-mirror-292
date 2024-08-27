from __future__ import annotations
import typing
from . import access
from . import constants
from . import errors
from . import hostApi
from . import log
from . import managerApi
from . import pluginSystem
from . import trait
from . import utils
__all__ = ['Context', 'EntityReference', 'access', 'constants', 'errors', 'hostApi', 'log', 'majorVersion', 'managerApi', 'minorVersion', 'patchVersion', 'pluginSystem', 'trait', 'utils', 'versionString']
class Context:
    locale: trait.TraitsData
    managerState: managerApi.ManagerStateBase
    @typing.overload
    def __init__(self, locale: trait.TraitsData, managerState: managerApi.ManagerStateBase = None) -> None:
        ...
    @typing.overload
    def __init__(self) -> None:
        ...
    def __str__(self) -> str:
        ...
class EntityReference:
    __hash__: typing.ClassVar[None] = None
    def __eq__(self, arg0: EntityReference) -> bool:
        ...
    def __init__(self, entityReferenceString: str) -> None:
        ...
    def __repr__(self) -> str:
        ...
    def __str__(self) -> str:
        ...
    def toString(self) -> str:
        ...
def majorVersion() -> int:
    ...
def minorVersion() -> int:
    ...
def patchVersion() -> int:
    ...
def versionString() -> str:
    ...
