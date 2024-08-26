# local imports:
from ..components import TransparentMisc

# standard libraries:
from tkinter import Listbox, Canvas, Frame, Text


class EnhListbox(TransparentMisc, Listbox):
    pass


class EnhCanvas(TransparentMisc, Canvas):
    pass


class EnhFrame(TransparentMisc, Frame):
    pass


class EnhText(TransparentMisc, Text):
    pass
