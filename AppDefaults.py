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
                self.head_subtitle = "#a8a8a8"
                self.head_title = "#2b2b2b"
                self.play_fore = self.ascent
                self.control_fore = "#777777"
                self.control_hover_fore = "#373737"
                self.control_active_fore = self.ascent
                self.slider_back = "#a8a8a8"

                self.entry_back = "#dbdbdb"
                self.entry_back_hover = "#cacaca"
                self.entry_heading_fore = "black"
                self.entry_key_fore = "#919191"
                self.entry_value_fore = "#474747"
                self.entry_na_fore = "#919191"
                self.entry_btn_fore = "#adadad"
                self.entry_btn_hover_fore = "#5e5e5e"
                self.entry_btn_active_fore = self.ascent


class FontDefaults:

    def __init__(self):
        self.title = ('Roboto Condensed Light', 16)
        self.subtitle = ('Roboto Condensed Bold', 9)
        self.menu = ('Roboto Condensed', 11)
        self.body = ()
        self.heading = ('Roboto Condensed Light', 11)
        self.key = ('Roboto Condensed', 9)
        self.value = ('Roboto Condensed Light', 9)
        self.na = ('Roboto Condensed Light Italic', 8)
        self.iconS = ('Segoe UI Symbol', 10)
        self.iconM = ('Segoe UI Symbol', 12)
        self.iconL = ('Segoe UI Symbol', 22)
