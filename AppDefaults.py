# App's default settings
from typing import Literal


class ColorDefaults:

    def __init__(self):
        self.theme: Literal["white", "light", "dark", "black"] = "white"
        self.ascent = "#FF7983"

        match self.theme:
            case "white":
                self.main_back = "white"
                self.head_back = "#D7D7D7"

                self.main_fore = "black"
                self.head_fore = "#1F1F1F"


class FontDefaults:

    def __init__(self):
        self.title = ()
        self.subtitle = ()
        self.heading = ('Roboto Condensed Bold', 18)
        self.menu = ('Roboto Condensed', 11)
        self.body = ()
