# App's default settings
from typing import Literal


class ColorDefaults:

    def __init__(self):
        self.theme: Literal["white", "light", "dark", "black"] = "white"
        self.ascent = "#FF7983"

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


class FontDefaults:

    def __init__(self):
        self.title = ()
        self.subtitle = ()
        self.menu = ('Roboto Condensed', 11)
        self.body = ()
        self.heading = ('Roboto Condensed Light', 11)
        self.key = ('Roboto Condensed', 9)
        self.value = ('Roboto Condensed Light', 9)
