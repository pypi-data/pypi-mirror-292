# local imports:
from ..utils import ColorUtils
from . import TransparentMisc

# standard libraries:
from typing import Generator, Optional, Tuple, List, Any
from tkinter import Event, Misc


class HoverMisc(TransparentMisc):
    auto_hover_background: bool = False
    background_color_did_update: bool = False
    hover_background_color: Optional[str] = None

    palette_colors: Tuple[str, ...] = ()
    palette_color_amount: int = 12

    cursor_hovered: bool = False
    speed: int = 1
    acceleration_ms: int = 6
    scheduled_update: Optional[str] = None

    def __init__(
            self,
            master: Optional[Misc] = None,
            *,
            hoverbackground: Optional[str] = None,
            **standard_options: Any) -> None:
        super().__init__(master, **standard_options)
        self.auto_hover_background = hoverbackground is None
        self.configure(hoverbackground=hoverbackground)
        self.bind(sequence="<<ParentConfigure>>", func=self.update_palette_colors, add=True)
        self.bind(sequence="<Enter>", func=self.on_cursor_interact, add=True)
        self.bind(sequence="<Leave>", func=self.on_cursor_interact, add=True)

    def on_cursor_interact(self, event: Event = None) -> None:
        self.cursor_hovered = int(event.type) == 7
        if self.scheduled_update:
            self.after_cancel(id=self.scheduled_update)
            self.scheduled_update = None
        self.scheduled_update = self.after(ms=self.acceleration_ms, func=self.update_frame)

    def update_frame(self) -> None:
        new_speed: int = self.speed + (1 if self.cursor_hovered else -1)
        new_speed = min(new_speed, self.palette_color_amount)
        new_speed = max(new_speed, 1)
        if new_speed == self.speed:
            return None
        self.speed = new_speed
        try:
            background_color: str = self.palette_colors[new_speed - 1]
            Misc.configure(self, background=background_color)
            self.event_generate(sequence="<<BackgroundConfigure>>")
            self.update_children()
        except IndexError:
            pass
        self.scheduled_update = self.after(ms=self.acceleration_ms, func=self.update_frame)

    def update_palette_colors(self, event: Optional[Event] = None) -> None:
        background_color: str = Misc.cget(self, key="background") \
            if not self.palette_colors or event is not None \
            else self.palette_colors[0]
        if background_color == "transparent":
            background_color = Misc.cget(self.master, key="background") or Misc.cget(self, key="background")
        if not ColorUtils.is_hex_code_valid(hex_code=background_color):
            rgb: Tuple[int, int, int] = self.winfo_rgb(color=background_color)
            red, green, blue = rgb
            background_color = ColorUtils.convert_rgb_to_hex(red, green, blue)
        palette_colors: Generator[str, None, str] = ColorUtils.generate_palette_colors(
            start_hex_code=background_color,
            end_hex_code=self.hover_background_color,
            color_amount=self.palette_color_amount)
        self.palette_colors = tuple(palette_colors)
        try:
            background_color: str = self.palette_colors[self.speed - 1]
            Misc.configure(self, background=background_color)
            self.event_generate(sequence="<<BackgroundConfigure>>")
            self.update_children()
        except IndexError:
            pass

    def configure(self, **standard_options: Any) -> Any:
        background_color: Optional[str] = standard_options.get("background", None)
        background_color = standard_options.get("bg", background_color)
        hover_background_color: Optional[str] = standard_options.pop("hoverbackground", None)
        if background_color is not None and self.auto_hover_background:
            hex_code: str = background_color or Misc.cget(self, key="background")
            if hex_code == "transparent":
                hex_code = Misc.cget(self.master, key="background") or Misc.cget(self, key="background")
            if not ColorUtils.is_hex_code_valid(hex_code):
                rgb: Tuple[int, int, int] = self.winfo_rgb(color=hex_code)
                red, green, blue = rgb
                hex_code = ColorUtils.convert_rgb_to_hex(red, green, blue)
            hover_background_color = hover_background_color or ColorUtils.adjust_hex_code(
                hex_code, brightness_factor=3.)
        if hover_background_color is not None or self.hover_background_color is None:
            if hover_background_color is None:
                hex_code: str = background_color or Misc.cget(self, key="background")
                if hex_code == "transparent":
                    hex_code = Misc.cget(self.master, key="background") or Misc.cget(self, key="background")
                if not ColorUtils.is_hex_code_valid(hex_code):
                    rgb: Tuple[int, int, int] = self.winfo_rgb(color=hex_code)
                    red, green, blue = rgb
                    hex_code = ColorUtils.convert_rgb_to_hex(red, green, blue)
                hover_background_color = ColorUtils.adjust_hex_code(hex_code, brightness_factor=3.)
            self.hover_background_color = hover_background_color
        result: Any = super().configure(**standard_options)
        if background_color is not None or hover_background_color is not None:
            self.after(ms=0, func=self.update_palette_colors)
        return result
    config = configure

    def cget(self, key: str) -> Any:
        return self.hover_background_color if key == "hoverbackground" else super().cget(key)

    def keys(self) -> List[str]:
        new_keys: Tuple[str, str] = "imagepath", "imagesize"
        keys: List[str] = super().keys()
        keys.extend(new_keys)
        return keys
