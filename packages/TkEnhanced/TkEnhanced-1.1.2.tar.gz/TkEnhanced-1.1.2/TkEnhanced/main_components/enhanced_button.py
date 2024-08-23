# local imports:
from ..components import ForegroundMisc, HoverMisc
from ..utils import ColorUtils

# standard libraries:
from typing import Optional, Tuple, Any
from tkinter import Button, Misc


class EnhButton(ForegroundMisc, HoverMisc, Button):
    def __init__(
            self,
            master: Optional[Misc] = None,
            *,
            background: Optional[str] = "transparent",
            borderwidth: Optional[int] = 0,
            foreground: Optional[str] = "auto",
            hoverbackground: Optional[str] = None,
            text: Optional[str] = "Enhanced Button",
            **standard_options: Any) -> None:
        super().__init__(
            master,
            background=background,
            borderwidth=borderwidth,
            foreground=foreground,
            hoverbackground=hoverbackground,
            text=text,
            **standard_options)
        if hoverbackground is not None:
            return None
        active_background_color: str = self.cget(key="activebackground")
        if not ColorUtils.is_hex_code_valid(hex_code=active_background_color):
            rgb: Tuple[int, int, int] = self.winfo_rgb(color=active_background_color)
            red, green, blue = rgb
            active_background_color = ColorUtils.convert_rgb_to_hex(red, green, blue)
        hover_background_color: str = ColorUtils.adjust_hex_code(
            hex_code=active_background_color,
            brightness_factor=.6)
        self.configure(hoverbackground=hover_background_color)
