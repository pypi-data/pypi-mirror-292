# local imports:
from ..utils import ColorUtils

# standard libraries:
from tkinter import Widget, Event, Misc
from typing import Optional, Any


class ForegroundMisc(Misc):
    is_auto_foreground: bool = False

    def __init__(self, master: Optional[Misc] = None, *, foreground: Optional[str] = "auto", **standard_options: Any) -> None:
        assert isinstance(self, Widget), "This instance must be a Widget."
        foreground_color: Optional[str] = standard_options.pop("fg", foreground)
        super().__init__(master, **standard_options)
        self.configure(foreground=foreground_color)
        self.bind(sequence="<<BackgroundConfigure>>", func=self.on_background_configure, add=True)

    def on_background_configure(self, event: Optional[Event] = None) -> None:
        if not self.is_auto_foreground:
            return None
        hex_code: str = self["background"]
        if not ColorUtils.is_hex_code_valid(hex_code):
            red, green, blue = self.winfo_rgb(color=hex_code)
            hex_code = ColorUtils.convert_rgb_to_hex(red, green, blue)
        foreground_color: str = "#ffffff" if ColorUtils.is_hex_code_darker(hex_code) else "#000000"
        Misc.configure(self, foreground=foreground_color)

    def configure(self, **standard_options: Any) -> Any:
        foreground_color: Optional[str] = standard_options.pop("foreground", None)
        foreground_color = standard_options.pop("fg", foreground_color)
        if foreground_color is not None:
            self.is_auto_foreground = isinstance(foreground_color, str) and foreground_color == "auto"
            if not self.is_auto_foreground:
                standard_options["foreground"] = foreground_color
        result: Any = super().configure(**standard_options)
        if self.is_auto_foreground:
            self.after(ms=0, func=self.on_background_configure)
        return result
    config = configure

    def cget(self, key: str) -> Any:
        return "auto" if key in ("fg", "foreground") and self.is_auto_foreground else super().cget(key)
