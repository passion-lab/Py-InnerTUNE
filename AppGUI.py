from tkinter import (
    Tk, Toplevel,
    Frame, Canvas, Label, Button,
    PhotoImage, Scrollbar
)
from tkinter.ttk import Sizegrip
# from PIL import Image, ImageTk

# Custom imports
from AppDefaults import ColorDefaults, FontDefaults


class App:

    def __init__(self):
        self.color = ColorDefaults()
        self.font = FontDefaults()
        self.app_name = "InnerTUNE"
        self.last_X = 0
        self.last_Y = 0
        self.images = {}
        self.menu_dropdown = False

        self.main_window = Tk()
        self.configuration()
        self.load_files()
        self.main_bg = self.make_main_background()
        self.header_bg, self.body_bg = self.make_panels()
        # self.make_window_draggable()
        self.make_main_menu()
        self.menu_dropdown_window: Toplevel
        self.make_entry_box()

        self.bindings()

    def run(self):
        self.main_window.mainloop()

    def configuration(self):
        self.main_window.overrideredirect(True)
        self.main_window.resizable(True, True)
        self.main_window.geometry("1076x552")

    def load_files(self):
        image_dir = "./Assets/images/"
        self.images["menu_button_inactive"] = PhotoImage(file=image_dir + 'menu_button_inactive.png')
        self.images["menu_button_active"] = PhotoImage(file=image_dir + 'menu_button_active.png')

    def bindings(self):
        self.header_bg.bind('<Button-1>', self._save_last_click)
        self.header_bg.bind('<B1-Motion>', self._drag_window)
        self.main_window.bind('<Escape>', lambda e=None: self.main_window.destroy())

    def _save_last_click(self, click):
        self.last_X, self.last_Y = click.x, click.y

    def _drag_window(self, drag):
        x, y = drag.x - self.last_X + self.main_window.winfo_x(), drag.y - self.last_Y + self.main_window.winfo_y()
        self.main_window.geometry(f"+{x}+{y}")

    def _resize_window(self, drag):
        x0, y0 = self.main_window.winfo_rootx(), self.main_window.winfo_rooty()
        x1, y1 = self.main_window.winfo_pointerx(), self.main_window.winfo_pointery(),
        self.main_window.geometry(f"{x1 - x0}x{y1 - y0}")

    # Created if needed later
    def _get_dimension(self, widget=None):
        self.main_window.update()
        if widget:
            widget.update()
            return widget.winfo_width(), widget.winfo_height(), widget.winfo_x(), widget.winfo_y()
        else:
            return self.main_window.winfo_width(), self.main_window.winfo_height(), \
                   self.main_window.winfo_x(), self.main_window.winfo_y()

    def make_main_background(self):
        main_bg = Canvas(self.main_window, bd=0, highlightthickness=0)
        main_bg.pack(fill='both', expand=True)

        return main_bg

    def make_panels(self):
        header = Canvas(self.main_bg, bg=self.color.head_back, bd=0, highlightthickness=0, height=60)
        header.pack(side='top', fill='x')
        body = Canvas(self.main_bg, bg=self.color.main_back, bd=0, highlightthickness=0)
        body.pack(side='top', fill='both', expand=True)

        return header, body

    def make_window_draggable(self):
        grip = Sizegrip(self.body_bg)
        grip.place(relx=1.0, rely=1.0, anchor='se')
        grip.bind('<B1-Motion>', self._drag_window)

    def make_main_menu(self):
        img = self.images['menu_button_inactive']
        img1 = self.images["menu_button_active"]
        self.main_window.update()
        btn = self.header_bg.create_image(self.header_bg.winfo_width() - img.width() / 2, img.height() / 2, image=img)
        self.header_bg.tag_bind(btn, '<Enter>', lambda e=None: self.header_bg.itemconfigure(btn, image=img1))
        self.header_bg.tag_bind(btn, '<Leave>', lambda e=None: self.header_bg.itemconfigure(btn, image=img))
        self.header_bg.tag_bind(btn, '<Button-1>', lambda e=None: __menu_options())

        def __menu_options():
            if not self.menu_dropdown:
                self.menu_dropdown = True
                self.menu_dropdown_window = Toplevel(self.main_window, bg=self.color.main_back, highlightthickness=1,
                                                     highlightcolor=self.color.ascent,
                                                     highlightbackground=self.color.ascent)
                options = [
                    ("Open & play a file", ),
                    ("Open & play a folder", ),
                    ("Scan whole filesystem", ),
                    ("App Settings", ),
                    (f"About {self.app_name}", ),
                    (f"Close {self.app_name}", )
                ]
                for i, option in enumerate(options):
                    cmd = Label(self.menu_dropdown_window, text=option[0], font=self.font.menu, bg=self.color.head_back,
                                fg=self.color.main_fore, anchor='e', padx=10, pady=3)
                    cmd.pack(fill='x', anchor='e')
                    cmd.bind('<Enter>', lambda e=None, c=cmd: c.configure(bg=self.color.main_back, fg=self.color.ascent))
                    cmd.bind('<Leave>', lambda e=None, c=cmd: c.configure(bg=self.color.head_back, fg=self.color.main_fore))
                    # cmd.bind('<Button-1>', lambda e=None, f=option[1]['func']: f())
                # Window options
                self.menu_dropdown_window.overrideredirect(True)
                self.menu_dropdown_window.attributes('-alpha', 0.7)
                self.menu_dropdown_window.attributes('-topmost', True)
                w1, h1, x1, y1 = self._get_dimension()
                w2, h2, _, _ = self._get_dimension(self.menu_dropdown_window)
                self.menu_dropdown_window.geometry(f"+{x1 + w1 - w2 - 10}+{y1 + 70}")
                self.menu_dropdown_window.bind('<Escape>', lambda e=None: self.menu_dropdown_window.destroy())
                self.menu_dropdown_window.mainloop()
            else:
                self.menu_dropdown_window.destroy()
                self.menu_dropdown = False

    def make_entry_box(self):
        bg_frame = Frame(self.body_bg)

        bg_canvas = Canvas(bg_frame)
        vsb = Scrollbar(bg_frame, orient='vertical', command=bg_canvas.yview, width=3)
        entry_box = Frame(bg_canvas)
        entry_box.bind('<Configure>', lambda e: bg_canvas.configure(scrollregion=bg_canvas.bbox('all')))
        bg_canvas.create_window((0, 0), window=entry_box, anchor='nw')
        bg_canvas.configure(yscrollcommand=vsb.set)
        bg_canvas.bind_all('<MouseWheel>', lambda e: bg_canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        for i in range(51):
            Label(entry_box, text=f"This is a line with number: {i}", font=("Arial", 22)).pack()

        bg_frame.pack(side='top', fill='both', expand=True)
        bg_canvas.pack(side='left', fill='both', expand=True)
        vsb.pack(side='right', fill='y')


