from collections.abc import Sequence
from numpy import bool_ as bool_, bytes_ as bytes_, complex_ as complex_, dtype as dtype, float_ as float_, int_ as int_, integer as integer, intp as intp, matrix as _Matrix, ndarray as ndarray, str_ as str_
from numpy._typing import ArrayLike as ArrayLike, DTypeLike as DTypeLike, NDArray as NDArray, _FiniteNestedSequence, _NestedSequence, _SupportsDType
from typing import Any, Generic, Literal, SupportsIndex, overload

@overload
def ix_(*args: _FiniteNestedSequence[_SupportsDType[_DType]]) -> tuple[ndarray[Any, _DType], ...]: ...
@overload
def ix_(*args: str | _NestedSequence[str]) -> tuple[NDArray[str_], ...]: ...
@overload
def ix_(*args: bytes | _NestedSequence[bytes]) -> tuple[NDArray[bytes_], ...]: ...
@overload
def ix_(*args: bool | _NestedSequence[bool]) -> tuple[NDArray[bool_], ...]: ...
@overload
def ix_(*args: int | _NestedSequence[int]) -> tuple[NDArray[int_], ...]: ...
@overload
def ix_(*args: float | _NestedSequence[float]) -> tuple[NDArray[float_], ...]: ...
@overload
def ix_(*args: complex | _NestedSequence[complex]) -> tuple[NDArray[complex_], ...]: ...

class nd_grid(Generic[_BoolType]):
    sparse: _BoolType
    def __init__(self, sparse: _BoolType = ...) -> None: ...
    @overload
    def __getitem__(self, key: slice | Sequence[slice]) -> NDArray[Any]: ...
    @overload
    def __getitem__(self, key: slice | Sequence[slice]) -> list[NDArray[Any]]: ...

class MGridClass(nd_grid[Literal[False]]):
    def __init__(self) -> None: ...

mgrid: MGridClass

class OGridClass(nd_grid[Literal[True]]):
    def __init__(self) -> None: ...

ogrid: OGridClass

class AxisConcatenator:
    axis: int
    matrix: bool
    ndmin: int
    trans1d: int
    def __init__(self, axis: int = ..., matrix: bool = ..., ndmin: int = ..., trans1d: int = ...) -> None: ...
    @staticmethod
    @overload
    def concatenate(*a: ArrayLike, axis: SupportsIndex = ..., out: None = ...) -> NDArray[Any]: ...
    @staticmethod
    @overload
    def concatenate(*a: ArrayLike, axis: SupportsIndex = ..., out: _ArrayType = ...) -> _ArrayType: ...
    @staticmethod
    def makemat(data: ArrayLike, dtype: DTypeLike = ..., copy: bool = ...) -> _Matrix: ...
    def __getitem__(self, key: Any) -> Any: ...

class RClass(AxisConcatenator):
    axis: Literal[0]
    matrix: Literal[False]
    ndmin: Literal[1]
    trans1d: Literal[-1]
    def __init__(self) -> None: ...

r_: RClass

class CClass(AxisConcatenator):
    axis: Literal[-1]
    matrix: Literal[False]
    ndmin: Literal[2]
    trans1d: Literal[0]
    def __init__(self) -> None: ...

c_: CClass

class IndexExpression(Generic[_BoolType]):
    maketuple: _BoolType
    def __init__(self, maketuple: _BoolType) -> None: ...
    @overload
    def __getitem__(self, item: _TupType) -> _TupType: ...
    @overload
    def __getitem__(self, item: _T) -> tuple[_T]: ...
    @overload
    def __getitem__(self, item: _T) -> _T: ...

index_exp: IndexExpression[Literal[True]]
s_: IndexExpression[Literal[False]]

def fill_diagonal(a: ndarray[Any, Any], val: Any, wrap: bool = ...) -> None: ...
def diag_indices(n: int, ndim: int = ...) -> tuple[NDArray[int_], ...]: ...
def diag_indices_from(arr: ArrayLike) -> tuple[NDArray[int_], ...]: ...
