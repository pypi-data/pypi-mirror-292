# Local imports:
from . import EnhCanvas, EnhFrame
from ..utils import Orientation

# Standard libraries:
from typing import Optional, Tuple, List, Any
from tkinter import Event, Misc


class EnhScrollableFrame(EnhFrame):
    in_frame_id: Optional[int] = None
    in_frame: Optional[EnhFrame] = None
    orientation: Orientation = None

    def __init__(
            self,
            master: Optional[Misc] = None,
            *,
            background: Optional[str] = "transparent",
            orient: Orientation = "vertical",
            **standard_options: Any) -> None:
        super().__init__(master, background=background, **standard_options)
        self.create_widgets()
        self.configure(orient=orient)

    def create_widgets(self) -> None:
        self.canvas: EnhCanvas = EnhCanvas(self, height=0, width=0)
        self.canvas.bind(sequence="<MouseWheel>", func=self.on_mouse_wheel, add=True)
        self.canvas.bind(sequence="<Configure>", func=self.on_configure, add=True)
        self.canvas.bind(sequence="<Map>", func=self.on_map, add=True)
        self.in_frame: EnhFrame = EnhFrame(self.canvas)
        self.in_frame.bind(sequence="<MouseWheel>", func=self.on_mouse_wheel, add=True)
        self.in_frame.bind(sequence="<Configure>", func=self.on_configure, add=True)
        coords: Tuple[int, int] = 0, 0
        self.in_frame_id = self.canvas.create_window(coords, anchor="nw", window=self.in_frame)

    def on_mouse_wheel(self, event: Event) -> None:
        scroll_amount: int = event.delta // 120
        self.canvas.yview_scroll(number=-scroll_amount, what="units") if self.orientation == "vertical" \
            else self.canvas.xview_scroll(number=-scroll_amount, what="units")

    def on_configure(self, event: Event) -> None:
        scroll_coordinates: Tuple[int, int, int, int] = self.canvas.bbox("all")
        scroll_coordinates: List[int] = list(scroll_coordinates)
        canvas_end_x, canvas_end_y = scroll_coordinates[2:]
        canvas_width, canvas_height = event.width, event.height
        scroll_coordinates[2] = max(canvas_end_x, canvas_width)
        scroll_coordinates[3] = max(canvas_end_y, canvas_height)
        self.canvas.configure(scrollregion=scroll_coordinates)
        is_vertical: bool = self.orientation == "vertical"
        self.canvas.itemconfigure(
            tagOrId=self.in_frame_id,
            height=0 if is_vertical else canvas_height,
            width=canvas_width if is_vertical else 0)

    def on_map(self, event: Optional[Event] = None) -> None:
        for child_widget in self.winfo_children():
            if child_widget == self.canvas:
                continue
            self.bind_mouse_wheel(widget=child_widget)

    def bind_mouse_wheel(self, widget: Misc) -> None:
        widget.bind(sequence="<MouseWheel>", func=self.on_mouse_wheel, add=True)
        for child_widget in widget.winfo_children():
            self.bind_mouse_wheel(widget=child_widget)

    def configure(self, **standard_options: Any) -> Any:
        orientation: Orientation = standard_options.pop("orient", None)
        if orientation is not None:
            self.orientation = orientation or "vertical"
            is_vertical: bool = self.orientation == "vertical"
            self.canvas.pack_configure(expand=True, fill="both", side="left" if is_vertical else "top")
        return super().configure(**standard_options)
    config = configure
