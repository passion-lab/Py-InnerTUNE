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
from AppBackend import Filesystem, AudioPlayer


class App:

    def __init__(self):
        self.color = ColorDefaults()
        self.font = FontDefaults()
        self.backend = Filesystem()
        self.audio = AudioPlayer()
        self.app_name = "InnerTUNE"
        self.last_X = 0
        self.last_Y = 0
        self.images = {}
        self.menu_dropdown: bool = False
        self.is_playing: bool = False
        self.is_paused: bool = False

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
        self.main_menu_window: Toplevel = ...
        self.menu_dropdown_window: Toplevel
        self.make_playing_controller()
        self.entry_box = self.make_entry_box()
        # self.make_song_list()

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

    def _exit_main_menu(self):
        self.main_menu_window.destroy()
        self.menu_dropdown = False

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
                self.main_menu_window = self.menu_dropdown_window
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
        status = Label(info_frame, textvariable=self.status, font=self.font.subtitle, fg=self.color.head_subtitle, bg=self.color.head_back)
        status.pack(side='top', anchor='sw')
        title = Label(info_frame, textvariable=self.title, font=self.font.title, fg=self.color.head_title, bg=self.color.head_back)
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
                    troughcolor=self.color.slider_back, variable=self.volume, command=self._volume)
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
        play.bind('<Button-1>', lambda e=None: self._play())
        full.bind('<Enter>', lambda e=None: full.configure(fg=self.color.control_hover_fore))
        full.bind('<Leave>', lambda e=None: full.configure(fg=self.color.control_fore))
        full.bind('<Button-1>', lambda e=None: self._full)
        mute.bind('<Enter>', lambda e=None: mute.configure(fg=self.color.control_hover_fore))
        mute.bind('<Leave>', lambda e=None: mute.configure(fg=self.color.control_fore))
        mute.bind('<Button-1>', lambda e=None: self._mute)

    def make_preload_bg(self):
        pass

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

    def make_song_list(self, songs: list[dict]):
        commands = (
            ["\ue107", partial(self._delete)],   # delete
            ["\ue193", partial(self._edit_meta)],  # edit metadata
            ["\ue110", partial(self._play_next)],  # play next
            ["\ue142", partial(self._add_playlist)],  # add to playlist
            ["\ue19f", partial(self._like)],  # like
            ["\ue1f8", partial(self._favorite)]  # favorite
        )
        for song in songs:
            details = (("ARTIST(S):", song['artists']), ("ALBUM:", song['album']), ("RELEASED:", song['release']))

            frame = Frame(self.entry_box, padx=15, pady=10, bg=self.color.entry_back, width=1076-60, height=32+25)
            frame.pack(padx=30, pady=7, fill='x')
            frame.pack_propagate(False)  # Fixes the width and the height for each entry frames
            c_frm = Frame(frame, bg=self.color.entry_back)
            c_frm.pack(side='right', anchor='e')

            thumb = Label(frame, image=self.images['thumb'], bg=self.color.entry_back, anchor='w')
            thumb.pack(side='left', fill='both', anchor='w', padx=(0, 5))
            heading = Label(frame, text=song['title'], font=self.font.heading, fg=self.color.entry_heading_fore, bg=self.color.entry_back, anchor='w')
            heading.pack(side='top', anchor='w')

            if not song['artists'] == song['album'] == song['release'] == 'Unknown':
                for detail in details:
                    Label(frame, text=detail[0], font=self.font.key, fg=self.color.entry_key_fore, bg=self.color.entry_back, anchor='w').pack(side='left', anchor='w')
                    Label(frame, text=detail[1], font=self.font.value, fg=self.color.entry_value_fore, bg=self.color.entry_back, anchor='w').pack(side='left', anchor='w')
            else:
                # TODO: Random quotations about music would be great!
                Label(frame, text="Details not available!", font=self.font.na, fg=self.color.entry_na_fore, bg=self.color.entry_back, anchor='w').pack(side='left', anchor='w')

            for command in commands:
                btn = Label(c_frm, text=command[0], font=self.font.iconM, fg=self.color.entry_btn_fore, bg=self.color.entry_back, anchor='e')
                btn.pack(side='right', fill='both', anchor='e')
                btn.bind('<Enter>', lambda e=None, b=btn: b.configure(fg=self.color.entry_btn_hover_fore))
                btn.bind('<Leave>', lambda e=None, b=btn: b.configure(fg=self.color.entry_btn_fore))

            # Bindings...
            frame.bind('<Enter>', lambda e=None, f=frame: self._entry_hover(f, hover=True))
            frame.bind('<Leave>', lambda e=None, f=frame: self._entry_hover(f, hover=False))
            frame.bind('<Double-Button-1>', lambda e=None: self._play())
            thumb.bind('<Button-1>', lambda e=None, s=song['id']: self._play(song_id=s, force_play=True))
            heading.bind('<Enter>', lambda e=None, h=heading: h.configure(fg=self.color.ascent))
            heading.bind('<Leave>', lambda e=None, h=heading: h.configure(fg=self.color.entry_heading_fore))

            self.status.set("PLAY YOUR InnerTUNE")

    def _entry_hover(self, frame: Frame, hover: bool = True):
        if hover:
            frame.configure(bg=self.color.entry_back_hover)
            for i, f1 in enumerate(frame.winfo_children()):
                if i == 1:
                    f1['image'] = self.images['thumb_hover']
                f1['bg'] = self.color.entry_back_hover
                for f2 in f1.winfo_children():
                    f2['bg'] = self.color.entry_back_hover
        else:
            frame.configure(bg=self.color.entry_back)
            for i, f1 in enumerate(frame.winfo_children()):
                if i == 1:
                    f1['image'] = self.images['thumb']
                f1['bg'] = self.color.entry_back
                for f2 in f1.winfo_children():
                    f2['bg'] = self.color.entry_back

    # BACKEND function calls for Control Buttons
    def _play(self, song_id=None, force_play: bool = False):
        # If not forced to play individual file from song entries
        if not force_play:
            if not self.is_playing:
                self.status.set("NOW PLAYING")
                self.audio.play_pause(play_state="PLAY")
                self.is_playing = True
            elif self.is_paused:
                self.audio.play_pause(play_state="RESUME")
                self.is_paused = False
            elif not self.is_paused:
                self.audio.play_pause(play_state="PAUSE")
                self.is_paused = True
        # If forced to play individual file from song entries
        else:
            self.audio.stop()
            song = self.backend.get_song(song_id)
            self.audio.load(song['path'])
            self.audio.play_pause("PLAY")
            self.status.set("NOW PLAYING")
            self.title.set(song['title'])
            self.is_playing = True


    def _previous(self):
        pass

    def _stop(self):
        if self.is_playing:
            self.audio.stop()
            self.is_playing = False

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
        print(self.volume.get)

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
        self._exit_main_menu()
        self.status.set("OPENING MUSIC FILES...")
        done = self.backend.open_files(title=f"{self.app_name} - Select music files you want to play with")
        if done:
            try:
                self.entry_box.winfo_children()[0].pack_forget()  # First clear the existing entry
            except:
                pass
            finally:
                self.make_song_list(self.backend.get_current_songs())  # Then, make new entries
                self.audio.load(file=self.backend.get_current_songs()[0]['path'])

    def _open_folder(self):
        self._exit_main_menu()
        self.status.set("OPENING FOLDER...")
        done = self.backend.open_folder(title=f"{self.app_name} - Choose a folder contains music to open with")
        if done:
            try:
                self.entry_box.winfo_children()[0].pack_forget()  # First clear the existing entry
            except:
                pass
            finally:
                self.make_song_list(self.backend.get_current_songs())  # Then, make new entries
                self.audio.load(file=self.backend.get_current_songs()[0]['path'])

    def _scan_filesystem(self):
        self._exit_main_menu()

    def _settings(self):
        self._exit_main_menu()

    def _about(self):
        self._exit_main_menu()

    def _close(self):
        self._exit_main_menu()
        self.main_window.destroy()
