# App's default settings
from typing import Literal


class ColorDefaults:

    def __init__(self):
        self.theme: Literal["white", "light", "dark", "black"] = "white"
        self.ascent = "#f26d7d"

        match self.theme:
            case "white":
                self.main_back = "white"
                self.main_fore = "black"
                self.head_back = "#e6e6e6"
                self.head_fore = "#1F1F1F"
                self.entry_back = "#dbdbdb"
                self.entry_back_hover = "#cacaca"
                self.entry_title_fore = "black"
                self.entry_key_fore = "#919191"
                self.entry_value_fore = "#474747"
                self.button_fore = "#adadad"
                self.button_hover_fore = "#5e5e5e"
                self.button_active_fore = self.ascent


class FontDefaults:

    def __init__(self):
        self.title = ()
        self.subtitle = ()
        self.menu = ('Roboto Condensed', 11)
        self.body = ()
        self.heading = ('Roboto Condensed Light', 11)
        self.key = ('Roboto Condensed', 9)
        self.value = ('Roboto Condensed Light', 9)
        self.iconS = ('Segoe UI Symbol', 10)
        self.iconM = ('Segoe UI Symbol', 12)
        self.iconL = ('Segoe UI Symbol', 18)
