import tkinter
from tkinter import (
    Tk, Toplevel,
    Frame, Canvas, Label, Scale,
    PhotoImage, Scrollbar,
    StringVar, DoubleVar
)
from tkinter.ttk import Sizegrip
from tkinter.font import Font
from os import listdir, curdir, chdir
from os.path import isfile, isdir
from PIL import Image, ImageTk
from io import BytesIO
from base64 import b64decode
from mutagen.mp3 import MP3
from mutagen.id3 import ID3
from functools import partial

# Custom imports
from AppDefaults import ColorDefaults, FontDefaults
from AppBackend import Filesystem


class App:

    def __init__(self):
        self.backend = Filesystem()
        self.color = ColorDefaults()
        self.font = FontDefaults()
        self.app_name = "InnerTUNE"
        self.last_X = 0
        self.last_Y = 0
        self.images = {}
        self.menu_dropdown = False

        self.main_window = Tk()
        self.set_title(self.app_name)
        self.configuration()
        self.load_files()
        self.status = StringVar(value="NOW PLAYING")
        self.title = StringVar(value="Dhal Jaun Main Tujhme ...")
        self.volume = DoubleVar(value=20)
        self.position = DoubleVar(value=0)
        self.main_bg = self.make_main_background()
        self.header_bg, self.body_bg = self.make_panels()
        # self.make_window_draggable()
        self.make_main_menu()
        self.menu_dropdown_window: Toplevel
        self.make_playing_controller()
        self.entry_box = self.make_entry_box()
        self.make_song_list()

        self.bindings()

    def run(self):
        self.main_window.mainloop()

    def configuration(self):
        self.main_window.overrideredirect(True)
        self.main_window.resizable(True, True)
        w, h = 1076, 552
        x, y = self.main_window.winfo_screenwidth() / 2 - w / 2, self.main_window.winfo_screenheight() / 2 - h / 2
        self.main_window.geometry(f"{w}x{h}+{int(x)}+{int(y)}")

    def load_files(self):
        image_dir = "./Assets/images/"
        self.images["menu_button_inactive"] = PhotoImage(file=image_dir + 'menu_button_inactive.png')
        self.images["menu_button_active"] = PhotoImage(file=image_dir + 'menu_button_active.png')
        # self.images["thumb"] = PhotoImage(file=image_dir + 'thumb.png')
        self.images["thumb"] = ImageTk.PhotoImage(Image.open(image_dir + 'thumb.png'))
        self.images["thumb_hover"] = ImageTk.PhotoImage(Image.open(image_dir + 'thumb_hover.png'))

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

    def set_title(self, text: str):
        self.main_window.title(text)

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
                    ("Open & play a file", partial(self._open_file)),
                    ("Open & play a folder", partial(self._open_folder)),
                    ("Scan whole filesystem", partial(self._scan_filesystem)),
                    ("App Settings", partial(self._settings)),
                    (f"About {self.app_name}", partial(self._about)),
                    (f"Close {self.app_name}", partial(self._close))
                ]
                for i, option in enumerate(options):
                    cmd = Label(self.menu_dropdown_window, text=option[0], font=self.font.menu, bg=self.color.head_back,
                                fg=self.color.main_fore, anchor='e', padx=10, pady=3)
                    cmd.pack(fill='x', anchor='e')
                    cmd.bind('<Enter>',
                             lambda e=None, c=cmd: c.configure(bg=self.color.main_back, fg=self.color.ascent))
                    cmd.bind('<Leave>',
                             lambda e=None, c=cmd: c.configure(bg=self.color.head_back, fg=self.color.main_fore))
                    cmd.bind('<Button-1>', lambda e=None, f=option[1]: f())
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

    def make_playing_controller(self):
        info_frame = Frame(self.header_bg, bg=self.color.head_back, padx=10, pady=5)
        info_frame.pack(side='left')
        play = Label(info_frame, text="\ue102", font=self.font.iconL, fg=self.color.play_fore, bg=self.color.head_back)
        play.pack(side='left', fill='both')
        status = Label(info_frame, text=self.status.get(), font=self.font.subtitle, fg=self.color.head_subtitle,
                       bg=self.color.head_back)
        status.pack(side='top', anchor='sw')
        title = Label(info_frame, text=self.title.get(), font=self.font.title, fg=self.color.head_title,
                      bg=self.color.head_back)
        title.pack(side='top', anchor='w')

        control_frame = Frame(self.header_bg, bg=self.color.head_back, padx=10, pady=3)
        control_frame.pack(side='right', padx=(0, self.images['menu_button_active'].width()))
        # row-1
        top = Frame(control_frame, bg=self.color.head_back)
        top.pack(side='bottom', anchor='e')
        buttons = {
            "timer": ("\ue121", partial(self._timer)),
            "playlist": ("\ue142", partial(self._que)),
            "shuffle": ("\ue148", partial(self._shuffle)),
            "repeat": ("\ue14a", partial(self._repeat)),
            "next": ("\ue101", partial(self._next)),
            "stop": ("\ue15b", partial(self._stop)),
            "previous": ("\ue100", partial(self._previous)),
        }
        for button in buttons:
            btn = Label(top, text=buttons[button][0], font=self.font.iconM, fg=self.color.control_fore, bg=self.color.head_back)
            btn.pack(side='right')
            btn.bind('<Enter>', lambda e=None, b=btn: b.configure(fg=self.color.control_hover_fore))
            btn.bind('<Leave>', lambda e=None, b=btn: b.configure(fg=self.color.control_fore))
            btn.bind('<Button-1>', lambda e=None, b=buttons[button][1]: b())
        # row-2
        bottom = Frame(control_frame, bg=self.color.head_back)
        bottom.pack(side='bottom', anchor='e')
        full = Label(bottom, text="\ue247", font=self.font.iconS, fg=self.color.control_fore, bg=self.color.head_back)
        full.pack(side='right')
        # TODO: Will have to improve the volume bar with custom ttk styling
        vol = Scale(bottom, from_=0, to=100, orient="horizontal", relief="flat", sliderrelief="solid", showvalue=False,
                    sliderlength=10, bd=0, width=5, highlightthickness=0,
                    troughcolor=self.color.slider_back, variable=self.volume)
        vol.pack(side='right')
        mute = Label(bottom, text="\ue246", font=self.font.iconS, fg=self.color.control_fore, bg=self.color.head_back)
        mute.pack(side='right')
        time = Label(bottom, text="00:00:00", font=self.font.iconS, fg=self.color.control_fore, bg=self.color.head_back)
        time.pack(side='right')
        # TODO: Will have to improve the seek bar with custom ttk styling
        seek = Scale(bottom, from_=0, to=100, orient="horizontal", relief="flat", sliderrelief="solid", showvalue=False,
                     sliderlength=2, bd=0, width=5, highlightthickness=0, length=200,
                     troughcolor=self.color.slider_back, variable=self.position)
        seek.pack(side='right')
        elapse = Label(bottom, text="00:00:00", font=self.font.iconS, fg=self.color.control_fore, bg=self.color.head_back)
        elapse.pack(side='right')

        # Bindings
        full.bind('<Enter>', lambda e=None: full.configure(fg=self.color.control_hover_fore))
        full.bind('<Leave>', lambda e=None: full.configure(fg=self.color.control_fore))
        full.bind('<Button-1>', lambda e=None: self._full)
        mute.bind('<Enter>', lambda e=None: mute.configure(fg=self.color.control_hover_fore))
        mute.bind('<Leave>', lambda e=None: mute.configure(fg=self.color.control_fore))
        mute.bind('<Button-1>', lambda e=None: self._mute)

    def make_entry_box(self):
        bg_frame = Frame(self.body_bg)

        bg_canvas = Canvas(bg_frame)
        vsb = Scrollbar(bg_frame, orient='vertical', command=bg_canvas.yview, width=3)
        entry_box = Frame(bg_canvas)
        entry_box.bind('<Configure>', lambda e: bg_canvas.configure(scrollregion=bg_canvas.bbox('all')))
        bg_canvas.create_window((0, 0), window=entry_box, anchor='nw')
        bg_canvas.configure(yscrollcommand=vsb.set)
        bg_canvas.bind_all('<MouseWheel>', lambda e: bg_canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

        bg_frame.pack(side='top', fill='both', expand=True)
        bg_canvas.pack(side='left', fill='both', expand=True)
        vsb.pack(side='right', fill='y')

        return entry_box

    def make_song_list(self):
        commands = (
            ["\ue1f8", partial(self._favorite)],  # favorite
            ["\ue19f", partial(self._like)],  # like
            ["\ue142", partial(self._add_playlist)],  # add to playlist
            ["\ue110", partial(self._play_next)],  # play next
            ["\ue193", partial(self._edit_meta)],  # edit metadata
            ["\ue107", partial(self._delete)]   # delete
        )
        test_path = "C:/Users/SSW-10/Downloads/"
        chdir(test_path)
        for file in listdir(test_path):
            if isfile(file) and (file.endswith(".mp3") or file.endswith(".wav")):
                title = file.rstrip(".mp3").rstrip(".wav")[:125] + " ..." if len(file) > 125 else file.rstrip(".mp3").rstrip(".wav")
                duration = artists = album = year = "unknown"
                cover = self.images['thumb']
                # track = MP3(file)
                try:
                    tag = ID3(file)

                    co = ImageTk.PhotoImage(Image.open(BytesIO(tag.get("APIC:").data)).resize((32, 32), resample=0))
                    ti, ar, al, ye = tag.get('TIT2'), tag.get('TPE1'), tag.get('TALB'), tag.get('TDRC')
                    if ti:
                        title = ti
                    if ar:
                        artists = ar
                    if al:
                        album = al
                    if ye:
                        year = ye
                except:
                    pass
                finally:
                    frame = Frame(self.entry_box, bg=self.color.entry_back, pady=5, padx=10)
                    frame.pack(fill='x', padx=30, pady=5)
                    #  +------+-------------------------------------+------+---+---+---+---+
                    #         +-----+-----+-----+------+-----+------+
                    #  +------+-----+-----+-----+------+-----+------+------+---+---+---+---+
                    Label(frame, image=cover, text=" ", compound='center', font=self.font.iconM,
                          fg=self.color.ascent, bg=self.color.entry_back, anchor='center').grid(row=0, column=0, rowspan=2, padx=(0, 5))

                    title = Label(frame, text=title, bg=self.color.entry_back, anchor='w', font=self.font.heading, fg=self.color.entry_title_fore)
                    title.grid(row=0, column=1, columnspan=6, sticky='w')
                    title.bind('<Enter>', lambda e=None, t=title: t.configure(fg=self.color.ascent))
                    title.bind('<Leave>', lambda e=None, t=title: t.configure(fg=self.color.entry_title_fore))
                    if not artists == album == year == 'unknown':
                        Label(frame, text="ARTIST(S):", bg=self.color.entry_back, font=self.font.key, anchor='w').grid(row=1, column=1, sticky='w')
                        Label(frame, text=artists, bg=self.color.entry_back, font=self.font.value, anchor='w').grid(row=1, column=2, sticky='w')
                        Label(frame, text="ALBUM:", bg=self.color.entry_back, font=self.font.key, anchor='w').grid(row=1, column=3, sticky='w')
                        Label(frame, text=album, bg=self.color.entry_back, font=self.font.value, anchor='w').grid(row=1, column=4, sticky='w')
                        Label(frame, text="RELEASED IN:", bg=self.color.entry_back, font=self.font.key, anchor='w').grid(row=1, column=5, sticky='w')
                        Label(frame, text=year, bg=self.color.entry_back, font=self.font.value, anchor='w').grid(row=1, column=6, sticky='w')

                    frame.columnconfigure(7, weight=1)
                    button_frame = Frame(frame, bg="")
                    button_frame.grid(row=0, column=7, rowspan=2, sticky='e')
                    for cmd in commands:
                        btn = Label(button_frame, text=cmd[0], font=self.font.iconM, fg=self.color.button_fore, bg=self.color.entry_back)
                        btn.pack(side='left')
                        btn.bind('<Enter>', lambda e=None, b=btn: b.configure(fg=self.color.button_hover_fore))
                        btn.bind('<Leave>', lambda e=None, b=btn: b.configure(fg=self.color.button_fore))
                        btn.bind('<Button-1>', lambda e=None, c=cmd[1]: c())

                    # bindings
                    frame.bind('<Enter>', lambda e=None, f=frame: self._entry_hover(f, hover=True))
                    frame.bind('<Leave>', lambda e=None, f=frame: self._entry_hover(f, hover=False))

    def _entry_hover(self, frame: Frame, hover: bool = True):
        if hover:
            frame.configure(bg=self.color.entry_back_hover)
            for i, f1 in enumerate(frame.winfo_children()):
                if i == 0:
                    f1['image'] = self.images['thumb_hover']
                f1['bg'] = self.color.entry_back_hover
                for f2 in f1.winfo_children():
                    f2['bg'] = self.color.entry_back_hover
        else:
            frame.configure(bg=self.color.entry_back)
            for i, f1 in enumerate(frame.winfo_children()):
                if i == 0:
                    f1['image'] = self.images['thumb']
                f1['bg'] = self.color.entry_back
                for f2 in f1.winfo_children():
                    f2['bg'] = self.color.entry_back

    # BACKEND function calls for Control Buttons
    def _play(self):
        pass

    def _previous(self):
        pass

    def _stop(self):
        pass

    def _next(self):
        pass

    def _repeat(self):
        print("Repeat")

    def _shuffle(self):
        pass

    def _que(self):
        pass

    def _timer(self):
        pass

    def _seek(self):
        pass

    def _mute(self):
        pass

    def _volume(self):
        pass

    def _full(self):
        pass

    # BACKEND function calls for Individual Entry Buttons
    def _favorite(self):
        pass

    def _like(self):
        pass

    def _add_playlist(self):
        pass

    def _play_next(self):
        pass

    def _edit_meta(self):
        pass

    def _delete(self):
        pass

    # Main Menu functions
    def _open_file(self):
        self.backend.open_files(title=f"{self.app_name} - Select music files you want to play with")

    def _open_folder(self):
        self.backend.open_folder(title=f"{self.app_name} - Choose a folder contains music to open with")

    def _scan_filesystem(self):
        pass

    def _settings(self):
        pass

    def _about(self):
        pass

    def _close(self):
        self.main_window.destroy()
