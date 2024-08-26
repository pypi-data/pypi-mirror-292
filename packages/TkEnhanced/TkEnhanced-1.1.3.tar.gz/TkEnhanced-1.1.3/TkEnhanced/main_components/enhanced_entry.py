# local imports:
from ..components import TransparentMisc

# standard libraries:
from typing import Optional, Literal, Any
from tkinter import Entry, Event, Misc


class EnhEntry(TransparentMisc, Entry):
    _default_color: Optional[str] = None
    _default_show: Optional[str] = None

    placeholder_color: Optional[str] = None
    placeholder_text: Optional[str] = None

    def __init__(
            self,
            master: Optional[Misc] = None,
            *,
            borderwidth: Optional[int] = 6,
            highlightthickness: Optional[int] = 1,
            placeholdercolor: Optional[str] = "#aaaaaa",
            placeholdertext: Optional[str] = "",
            relief: Literal["raised", "sunken", "flat", "ridge", "solid", "groove"] = "flat",
            **standard_options: Any) -> None:
        super().__init__(master, borderwidth=borderwidth, highlightthickness=highlightthickness, relief=relief, **standard_options)
        self.configure(placeholdercolor=placeholdercolor, placeholdertext=placeholdertext)
        self.bind(sequence="<FocusIn>", func=self.on_focus_in, add=True)
        self.bind(sequence="<FocusOut>", func=self.on_focus_out, add=True)

    def on_focus_in(self, event: Optional[Event] = None) -> None:
        if self["foreground"] != self.placeholder_color:
            return None
        self.delete(first="0", last="end")
        Misc.configure(self, foreground=self._default_color, show=self._default_show)

    def on_focus_out(self, event: Optional[Event] = None) -> None:
        if self.get():
            return None
        Misc.configure(self, foreground=self.placeholder_color, show="")
        self.insert(index="0", string=self.placeholder_text)

    def configure(self, **standard_options: Any) -> Any:
        self.on_focus_in(event=None)
        placeholder_color: Optional[str] = standard_options.pop("placeholdercolor", None)
        if isinstance(placeholder_color, str):
            self.placeholder_color = placeholder_color
        placeholder_text: Optional[str] = standard_options.pop("placeholdertext", None)
        if placeholder_text is not None:
            self.placeholder_text = str(placeholder_text)
        result: Any = super().configure(**standard_options)
        self._default_color = self["foreground"]
        self._default_show = self["show"]
        if not self.focus_get():
            self.after(ms=0, func=self.on_focus_out)
        return result
    config = configure

    def set_text(self, text: str) -> None:
        self.on_focus_in(event=None)
        self.delete(first="0", last="end")
        self.insert(index="0", string=text)
        if self.focus_get():
            return None
        self.on_focus_out(event=None)

    def cget(self, key: str) -> Any:
        if key == "placeholdercolor":
            return self.placeholder_color
        if key == "placeholdertext":
            return self.placeholder_text
        return super().cget(key)
