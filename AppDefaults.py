# App's default settings
from typing import Literal


class ColorDefaults:

    def __init__(self):
        self.theme: Literal["white", "light", "dark", "black"] = "white"
        self.ascent = "#f26d7d"

        match self.theme:
            case "white":
                self.disabled = "#c7c7c7"
                self.enabled = self.ascent
                self.select_back = self.ascent
                self.select_fore = "#c4c4c4"

                self.main_back = "white"
                self.main_fore = "black"

                self.head_back = "#e6e6e6"
                self.head_fore = "#1F1F1F"
                self.head_subtitle = "#a8a8a8"
                self.head_title = "#2b2b2b"
                self.body = "grey"
                self.play_fore = self.ascent
                self.control_fore = "#777777"
                self.control_disabled = "#a2a2a2"
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

                self.popup_back = self.head_back
                self.popup_title_fore = "#121212"
                self.popup_head_fore = "#3e3e3e"
                self.popup_option_fore = "#3e3e3e"
                self.popup_option_hover = "#c8c8c8"
                self.popup_option_select = self.main_back
                self.popup_body = "#636363"
                self.popup_line = "#b7b7b7"

                self.now_playing_back = self.ascent  # endangered
                self.now_playing_title = "#f8f8f8"
                self.now_playing_subtitle = "#d4d4d4"
                self.now_playing_btnP = "#ffffff"
                self.now_playing_btnS = "#C2C2C2"
                self.now_playing_status = "#f48a98"
                self.now_playing_info = "#000000"


class FontDefaults:

    def __init__(self):
        self.title = ('Roboto Condensed Light', 16)
        self.subtitle = ('Roboto Condensed Bold', 9)
        self.menu = ('Roboto Condensed', 11)
        self.body = ('Roboto Condensed', 12)
        self.heading = ('Roboto Condensed Light', 11)
        self.key = ('Roboto Condensed', 9)
        self.value = ('Roboto Condensed Light', 9)
        self.na = ('Roboto Condensed Light Italic', 8)
        self.iconS = ('Segoe UI Symbol', 10)
        self.iconM = ('Segoe UI Symbol', 12)
        self.iconL = ('Segoe UI Symbol', 22)
        self.popup_title = ('Roboto Condensed Bold', 11)
        self.popup_head = ('Roboto Condensed Light', 16)
        self.popup_option = ('Roboto Condensed', 12)
# <<<<<<< HEAD
        self.popup_body = ('Roboto Condensed', 10)
        self.popup_field = ('Roboto Condensed Light Italic', 10)
        self.popup_entry = ('Roboto Condensed Light', 12)
# =======
        self.now_playing_title = ('Roboto Condensed Light', 18)
        self.now_playing_subtitle = ('Roboto Condensed Light Italic', 10)
        self.now_playing_status = ('Roboto Condensed Bold', 11)
        self.now_playing_info = ('Roboto Condensed', 13)
# >>>>>>> central
