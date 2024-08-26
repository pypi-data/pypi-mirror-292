# standard libraries:
from typing import Optional, Callable, Final, Dict, List
from tkinter import Event, Misc, Wm, TclError
from abc import ABC, abstractmethod
from ctypes import WinDLL, windll
from enum import Enum

# window resize cursor names:
WINDOW_CURSOR_NAMES: Final[Dict[int, str]] = {
    0: "size_nw_se",
    1: "size_ne_sw",
    2: "sb_v_double_arrow",
    3: "size_ne_sw",
    4: "size_nw_se",
    5: "sb_v_double_arrow",
    6: "sb_h_double_arrow",
    7: "sb_h_double_arrow"}


class WindowInterface(ABC):
    @abstractmethod
    def retrieve_window_handle(self) -> int: ...

    @abstractmethod
    def hide_titlebar(self) -> None: ...

    @abstractmethod
    def show_titlebar(self) -> None: ...

    @abstractmethod
    def center_window(self, *, width: Optional[int] = None, height: Optional[int] = None) -> None: ...

    @abstractmethod
    def minimize_window(self) -> None: ...
    minimize = minimize_window


class WindowIndexes:
    WINDOW_STYLE: Final[int] = -16
    EXTENDED_WINDOW_STYLE: Final[int] = -20


class WindowStyles:
    MINIMIZE_BOX: Final[int] = 0x00020000
    FORCE_ONTO_TASKBAR: Final[int] = 0x00040000


class WindowStates(Enum):
    ZOOMED = 3
    SHOWN = 5
    MINIMIZED = 6


class WindowResizeUtils:
    _events: List[Dict[str, str]] = []
    _window: Optional["WindowUtils"] = None

    last_cursor_index: Optional[int] = None
    started_x: Optional[int] = None
    started_y: Optional[int] = None

    @staticmethod
    def get_cursor_index(event: Event, window: "WindowUtils") -> int:
        is_window: bool = event.widget == window
        if not is_window:
            return -1
        is_maximized: bool = window.wm_state() == WindowStates.ZOOMED.name
        if is_maximized:
            return -1
        is_top: bool = event.y <= 5
        is_left: bool = event.x <= 5
        is_right: bool = event.x >= window.winfo_width() - 5
        is_bottom: bool = event.y >= window.winfo_height() - 5
        is_width_resizable, is_height_resizable = window.wm_resizable()
        if is_height_resizable and is_top:
            return 0 if is_left else 1 if is_right else 2
        if is_height_resizable and is_bottom:
            return 3 if is_left else 4 if is_right else 5
        return -1 if not is_width_resizable else 6 if is_left else 7 if is_right else -1

    def __init__(self, master: Optional["WindowUtils"] = None) -> None:
        assert isinstance(master, WindowUtils), "The parent master must be a WindowUtils instance."
        self._window = master
        self.attach_events()

    def attach_events(self) -> None:
        self.attach_event(sequence="<Motion>", function=self.on_motion)
        self.attach_event(sequence="<Button-1>", function=self.start_resize)
        self.attach_event(sequence="<B1-Motion>", function=self.on_resize)
        self.attach_event(sequence="<ButtonRelease-1>", function=self.stop_resize)

    def attach_event(self, sequence: str, function: Callable[[Event], object]) -> None:
        function_id: str = self._window.bind(sequence, func=function, add=True)
        new_event: Dict[str, str] = {"sequence": sequence, "function_id": function_id}
        self._events.append(new_event)

    def on_motion(self, event: Event) -> None:
        cursor_index: int = self.get_cursor_index(event, window=self._window)
        if self.last_cursor_index == cursor_index:
            return None
        self.last_cursor_index = cursor_index
        cursor_name: str = WINDOW_CURSOR_NAMES.get(cursor_index, "")
        self._window.configure(cursor=cursor_name)

    def start_resize(self, event: Event) -> None:
        is_default_cursor: bool = self.last_cursor_index == -1
        if is_default_cursor:
            return None
        self.started_x, self.started_y = event.x, event.y

    def on_resize(self, event: Event) -> None:
        if self.started_x is None or self.started_y is None:
            return None
        new_x: int = self._window.winfo_x()
        new_y: int = self._window.winfo_y()
        new_width: int = self._window.winfo_width()
        new_height: int = self._window.winfo_height()
        minimum_width, minimum_height = self._window.wm_minsize()
        is_width_resizable, is_height_resizable = self._window.wm_resizable()
        if is_height_resizable:
            mouse_y: int = event.y
            # top movement.
            if self.last_cursor_index in (0, 1, 2):
                minimum_y: int = new_y + new_height - minimum_height
                new_y += mouse_y - self.started_y
                new_y = min(minimum_y, new_y)
                new_height -= mouse_y - self.started_y
            # bottom movement.
            if self.last_cursor_index in (3, 4, 5):
                if mouse_y >= minimum_height:
                    variable_name: int = mouse_y - self.started_y
                    self.started_y = mouse_y
                    new_height += variable_name
                else:
                    new_height = minimum_height
        if is_width_resizable:
            mouse_x: int = event.x
            # left movement.
            if self.last_cursor_index in (0, 3, 6):
                minimum_x: int = new_x + new_width - minimum_width
                new_x += mouse_x - self.started_x
                new_x = min(minimum_x, new_x)
                new_width -= mouse_x - self.started_x
            # right movement.
            if self.last_cursor_index in (1, 4, 7):
                if mouse_x >= minimum_width:
                    variable_name: int = mouse_x - self.started_x
                    self.started_x = mouse_x
                    new_width += variable_name
                else:
                    new_width = minimum_width
        new_width = max(minimum_width, new_width)
        new_height = max(minimum_height, new_height)
        new_geometry: str = "{}x{}+{}+{}".format(new_width, new_height, new_x, new_y)
        self._window.wm_geometry(newGeometry=new_geometry)

    def stop_resize(self, event: Event) -> None:
        self.started_x = self.started_y = None
        self.on_motion(event)

    def __del__(self) -> None:
        try:
            if not self._window.winfo_exists():
                return None
            for event in self._events:
                sequence, function_id = event.values()
                self._window.unbind(sequence, funcid=function_id)
            self._window.configure(cursor="")
        except TclError:
            return None


class WindowUtils(WindowInterface, Misc, Wm):
    _resize_utils: Optional[WindowResizeUtils] = None
    _user32_api: WinDLL = windll.user32

    def retrieve_window_handle(self) -> int:
        self.update_idletasks()
        window_id: int = self.winfo_id()
        window_handle: int = self._user32_api.GetParent(window_id)
        return window_handle

    def hide_titlebar(self, *, resize_utils: bool = True) -> None:
        self.wm_overrideredirect(boolean=True)
        if resize_utils:
            self._resize_utils = WindowResizeUtils(self)
        window_handle: int = self.retrieve_window_handle()
        self._user32_api.SetWindowLongPtrW(
            window_handle,
            WindowIndexes.WINDOW_STYLE,
            WindowStyles.MINIMIZE_BOX)
        self._user32_api.SetWindowLongPtrW(
            window_handle,
            WindowIndexes.EXTENDED_WINDOW_STYLE,
            WindowStyles.FORCE_ONTO_TASKBAR)
        is_window_hidden: bool = self.wm_state() == "withdrawn"
        if is_window_hidden:
            return None
        self._user32_api.ShowWindow(window_handle, WindowStates.SHOWN.value)

    def show_titlebar(self) -> None:
        if self._resize_utils is not None:
            self._resize_utils.__del__()
            self._resize_utils = None
        self.wm_overrideredirect(boolean=False)

    def center_window(self, *, width: Optional[int] = None, height: Optional[int] = None) -> None:
        if not width or not height:
            self.update_idletasks()
        screen_width: int = self.winfo_screenwidth()
        screen_height: int = self.winfo_screenheight()
        window_width: int = width or self.winfo_width()
        window_height: int = height or self.winfo_height()
        center_x: int = (screen_width - window_width) // 2
        center_y: int = (screen_height - window_height) // 2
        new_geometry: str = "{}x{}+{}+{}".format(window_width, window_height, center_x, center_y)
        self.wm_geometry(newGeometry=new_geometry)

    def minimize_window(self) -> None:
        is_titlebar_hidden: bool = self.wm_overrideredirect()
        if not is_titlebar_hidden:
            return self.wm_iconify()
        window_handle: int = self.retrieve_window_handle()
        self._user32_api.ShowWindow(window_handle, WindowStates.MINIMIZED.value)
    minimize = minimize_window
