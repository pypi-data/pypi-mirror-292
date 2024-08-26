# standard libraries:
from typing import TypeAlias, Optional, Literal, Union, Tuple, List, Any
from tkinter.font import Font
from _tkinter import Tcl_Obj
from pathlib import Path

# path aliases:
PathDescription: TypeAlias = Optional[Union[Path, str]]

# other type aliases:
FontDescription: TypeAlias = (
    str
    | Font
    | List[Any]
    | Tuple[str]
    | Tuple[str, int]
    | Tuple[str, int, str]
    | Tuple[str, int, List[str] | Tuple[str, ...]]
    | Tcl_Obj)
Orientation: TypeAlias = Optional[Literal["vertical", "horizontal"]]
Size: TypeAlias = Optional[Tuple[int, int]]
