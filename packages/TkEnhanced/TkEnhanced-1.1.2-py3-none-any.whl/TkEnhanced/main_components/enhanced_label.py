# local imports:
from ..components import TransparentMisc, ForegroundMisc
from ..utils import FontDescription

# standard libraries:
from tkinter import Event, Label, Misc
from typing import Optional, Any
from tkinter.font import Font


class EnhLabel(ForegroundMisc, TransparentMisc, Label):
    _text: str = ""

    def __init__(
            self,
            master: Optional[Misc] = None,
            *,
            background: Optional[str] = "transparent",
            foreground: Optional[str] = "auto",
            padx: Optional[int] = 3,
            text: Optional[str] = "Enhanced Label",
            **standard_options: Any) -> None:
        super().__init__(master, background=background, foreground=foreground, **standard_options)
        self.configure(padx=padx, text=text)
        self.bind(sequence="<Configure>", func=self.on_configure, add=True)

    def on_configure(self, event: Optional[Event] = None) -> None:
        font: FontDescription = self.cget(key="font")
        font = Font(font=font)
        label_width: int = self.winfo_width()
        minimum_width: int = font.measure(text="...")
        if minimum_width > label_width:
            Misc.configure(self, text="...")
            return None
        text: str = self._text
        text_width: int = font.measure(text)
        if text_width > label_width:
            text_width += minimum_width
            while text_width > label_width:
                text = text[:-1]
                text_width = font.measure(text=text + "...")
            text += "..."
        Misc.configure(self, text=text)

    def configure(self, **standard_options: Any) -> Any:
        padx: Optional[int] = standard_options.pop("padx", None)
        if isinstance(padx, int):
            standard_options["padx"] = max(3, padx)
        text: Optional[str] = standard_options.get("text", None)
        if text is not None:
            self._text = str(text)
        return super().configure(**standard_options)
    config = configure

    def cget(self, key: str) -> Any:
        return self._text if key == "text" else super().cget(key)
