from typing import Protocol as _Protocol, runtime_checkable as _runtime_checkable


@_runtime_checkable
class Stringable(_Protocol):
    def __str__(self) -> str:
        ...


AttrDict = dict[str, Stringable | bool] | None
