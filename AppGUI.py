# import tkinter
from tkinter import (
    Tk, Toplevel,
    Frame, Canvas, Label, Scale,
    PhotoImage, Scrollbar,
    StringVar, DoubleVar
)
from tkinter.ttk import Sizegrip
# from tkinter.font import Font
# from os import listdir, curdir, chdir
# from os.path import isfile, isdir
from PIL import Image, ImageTk
# from io import BytesIO
# from base64 import b64decode
# from mutagen.mp3 import MP3
# from mutagen.id3 import ID3
from time import sleep, strftime, gmtime
from typing import Literal
from functools import partial
from threading import Thread, Event

# Custom imports
from AppDefaults import ColorDefaults, FontDefaults
from AppBackend import Filesystem, AudioPlayer


class App:
    default_volume: float = 0.3

    def __init__(self):
        self.color = ColorDefaults()
        self.font = FontDefaults()
        self.backend = Filesystem()
        self.audio = AudioPlayer(initial_volume=self.default_volume)
        self.app_name = "InnerTUNE"
        self.last_X = 0
        self.last_Y = 0
        self.app_terminate: bool = False

        self.images = {}
        self.menu_dropdown: bool = False
        self.play_trigger: bool = False
        self.is_playing: bool = False
        self.is_paused: bool = False
        self.is_repeat: bool = False
        self.active_entry: [(Label, Label)] = []
        self.last_active_entry: [(Label, Label, str)] = []
        self.active_controls: list[Label] = []
        self.is_muted: bool = False
        self.is_full: bool = False
        self.total_songs: int = 0
        self.current_song_index: int | None = None
        self.all_entries: [(Label, Label)] = []  # Stores the list of thumbnails and headings of all the entries

        self.main_window = Tk()
        self.set_title(self.app_name)
        self.configuration()
        self.load_files()
        self.status = StringVar(value="UPLOAD FILE(S)/FOLDER")
        self.title = StringVar(value="Play your favorite tune ...")
        self.volume = DoubleVar(value=self.default_volume)
        self.position = DoubleVar(value=0)
        self.duration = StringVar(value="00:00:00")
        self.elapsed = StringVar(value="00:00:00")
        self.main_bg = self.make_main_background()
        self.header_bg, self.body_bg = self.make_panels()
        self.make_preload_bg()
        # self.make_window_draggable()
        self.make_main_menu()
        self.main_menu_window: Toplevel = ...
        self.menu_dropdown_window: Toplevel
        self.entry_box_bg: Frame = ...
        self.tgl_play: Label = ...
        self.tgl_mute: Label = ...
        self.tgl_full: Label = ...
        self.tgl_active_heading: Label = ...
        self.seek_bar: Scale = ...
        self.make_playing_controller()
        self.thread_event = Event()

        self.bindings()
        Thread(target=self.progress, daemon=True).start()

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
        self.images["entry_banner"] = ImageTk.PhotoImage(Image.open(image_dir + 'entry_banner.png'))
        self.images["thumb"] = ImageTk.PhotoImage(Image.open(image_dir + 'thumb.png'))
        self.images["thumb_hover"] = ImageTk.PhotoImage(Image.open(image_dir + 'thumb_hover.png'))
        self.images["thumb_active"] = ImageTk.PhotoImage(Image.open(image_dir + 'thumb_active.png'))

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
        img = self.images["menu_button_inactive"]
        img1 = self.images["menu_button_active"]
        self.main_window.update()
        btn = self.header_bg.create_image(self.header_bg.winfo_width() - img.width() / 2, img.height() / 2, image=img)
        self.header_bg.tag_bind(btn, '<Enter>', lambda e=None: self.header_bg.itemconfigure(btn, image=img1))
        self.header_bg.tag_bind(btn, '<Leave>', lambda e=None: self.header_bg.itemconfigure(btn, image=img))
        self.header_bg.tag_bind(btn, '<ButtonRelease-1>', lambda e=None: __menu_options())

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
        self.tgl_play = Label(info_frame, text="\ue102", font=self.font.iconL, fg=self.color.play_fore, bg=self.color.head_back)
        self.tgl_play.pack(side='left', fill='both')
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
            "timer": "\ue121",
            "playlist": "\ue142",
            "shuffle": "\ue148",
            "repeat": "\ue14a",
            "next": "\ue101",
            "stop": "\ue15b",
            "previous": "\ue100",
        }
        for button in buttons:
            btn = Label(top, text=buttons[button], font=self.font.iconM, fg=self.color.control_fore, bg=self.color.head_back)
            btn.pack(side='right')
            btn.bind('<Enter>', lambda e=None, b=btn: b.configure(fg=self.color.control_hover_fore) if not b in self.active_controls else None)
            btn.bind('<Leave>', lambda e=None, b=btn: b.configure(fg=self.color.control_fore) if not b in self.active_controls else None)
            btn.bind('<Button-1>', lambda e=None, b=btn, a=button: self._control_actions(button=b, action=a))
        # row-2
        bottom = Frame(control_frame, bg=self.color.head_back)
        bottom.pack(side='bottom', anchor='e')
        self.tgl_full = Label(bottom, text="\ue247", font=self.font.iconS, fg=self.color.control_fore, bg=self.color.head_back)
        self.tgl_full.pack(side='right')
        # TODO: Will have to improve the volume bar with custom ttk styling
        vol = Scale(bottom, from_=0.0, to=1.0, orient="horizontal", relief="flat", sliderrelief="solid", showvalue=False,
                    sliderlength=10, bd=0, width=5, highlightthickness=0, resolution=0.01,  cursor='size_we',
                    troughcolor=self.color.slider_back, variable=self.volume, command=self._volume)
        vol.pack(side='right')
        self.tgl_mute = Label(bottom, text="\ue246", font=self.font.iconS, fg=self.color.control_fore, bg=self.color.head_back)
        self.tgl_mute.pack(side='right')
        duration = Label(bottom, textvariable=self.duration, font=self.font.iconS, fg=self.color.control_fore, bg=self.color.head_back)
        duration.pack(side='right')
        # TODO: Will have to improve the seek bar with custom ttk styling
        self.seek_bar = Scale(bottom, from_=0, to=100, orient="horizontal", relief="flat", sliderrelief="solid", showvalue=False,
                              sliderlength=2, bd=0, width=5, highlightthickness=0, length=200,  cursor='size_we', command=self._seek,
                              troughcolor=self.color.slider_back, variable=self.position)
        self.seek_bar.pack(side='right')
        elapsed = Label(bottom, textvariable=self.elapsed, font=self.font.iconS, fg=self.color.control_fore, bg=self.color.head_back)
        elapsed.pack(side='right')

        # Bindings
        self.tgl_play.bind('<Button-1>', lambda e=None: self._play())
        self.tgl_full.bind('<Enter>', lambda e=None: self.tgl_full.configure(fg=self.color.control_hover_fore) if self.tgl_full not in self.active_controls else None)
        self.tgl_full.bind('<Leave>', lambda e=None: self.tgl_full.configure(fg=self.color.control_fore) if self.tgl_full not in self.active_controls else None)
        self.tgl_full.bind('<Button-1>', lambda e=None: self._full())
        self.tgl_mute.bind('<Enter>', lambda e=None: self.tgl_mute.configure(fg=self.color.control_hover_fore) if self.tgl_mute not in self.active_controls else None)
        self.tgl_mute.bind('<Leave>', lambda e=None: self.tgl_mute.configure(fg=self.color.control_fore) if self.tgl_mute not in self.active_controls else None)
        self.tgl_mute.bind('<Button-1>', lambda e=None: self._mute())

    def make_preload_bg(self):
        Label(self.body_bg, image=self.images['entry_banner'], bg=self.color.main_back).place(relx=0.5, rely=0.5, anchor='center')

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

        self.entry_box_bg = bg_frame
        return entry_box

    def make_song_list(self, songs: list[dict]):
        self.total_songs = len(songs)
        commands = (
            ["\ue107", partial(self._delete)],   # delete
            ["\ue193", partial(self._edit_meta)],  # edit metadata
            ["\ue110", partial(self._play_next)],  # play next
            ["\ue142", partial(self._add_playlist)],  # add to playlist
            ["\ue19f", partial(self._like)],  # like
            ["\ue1f8", partial(self._favorite)]  # favorite
        )
        entry_box = self.make_entry_box()
        for i, song in enumerate(songs):
            details = (("ARTIST(S):", song['artists']), ("ALBUM:", song['album']), ("RELEASED:", song['release']))

            frame = Frame(entry_box, padx=15, pady=10, bg=self.color.entry_back, width=1076-60, height=32+25)
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
            frame.bind('<Double-Button-1>', lambda e=None, s=song['id'], t=thumb, h=heading: self._play(song_id=s, force_play=True, th=t, hd=h))
            thumb.bind('<Button-1>', lambda e=None, s=song['id'], t=thumb, h=heading: self._play(song_id=s, force_play=True, th=t, hd=h))

            self.all_entries.append((thumb, heading))
            # First entry added to the last_active_entry for thumb and heading change on hitting controller play button
            if i == 0:
                self.last_active_entry = [(thumb, heading, song['title'])]

        self.status.set("START YOUR INNER TUNE WITH")
        self.title.set(self.last_active_entry[0][2])  # Set the title to the first song's title as set before

    def _set_control(self, widget: Label, will_set: bool = True):
        if will_set:
            self.active_controls.append(widget)
            widget.configure(fg=self.color.control_active_fore)
        else:
            self.active_controls.remove(widget)
            widget.configure(fg=self.color.control_fore)

    def _entry_hover(self, frame: Frame, hover: bool = True):
        # Changes all elements' background on mouse hover
        if hover:
            frame.configure(bg=self.color.entry_back_hover)
            # For all child elements within a frame
            for i, f1 in enumerate(frame.winfo_children()):
                # If the child elements is the entries heading
                if i == 1:
                    try:
                        # If the entry is in active entry list (i.e., currently playing) then,
                        if f1 in self.active_entry[0]:
                            # Retain the thumb same that is active,
                            self.active_entry[0][0]['image'] = self.images['thumb_active']
                        else:
                            # otherwise change on hover as usual
                            f1['image'] = self.images['thumb_hover']
                    except:
                        # Else, change on hover
                        f1['image'] = self.images['thumb_hover']
                    # Do always
                    finally:
                        # If the last played song is in the last_active_list and the song is currently playing
                        if f1 in self.last_active_entry[0] and self.is_playing:
                            # Retain the thumb same as current playing
                            self.last_active_entry[0][0]['image'] = self.images['thumb_active']

                # Otherwise, change all elements and their children's background
                f1['bg'] = self.color.entry_back_hover
                for f2 in f1.winfo_children():
                    f2['bg'] = self.color.entry_back_hover

        # Changes all elements' background on mouse leave
        else:
            frame.configure(bg=self.color.entry_back)
            # For all child elements within a frame
            for i, f1 in enumerate(frame.winfo_children()):
                # If the child elements is the entries heading
                if i == 1:
                    try:
                        # If the entry is in active entry list (i.e., currently playing)
                        if f1 in self.active_entry[0]:
                            # Retain the thumb same that is active,
                            self.active_entry[0][0]['image'] = self.images['thumb_active']
                        else:
                            # otherwise change on hover as usual
                            f1['image'] = self.images['thumb']
                    except:
                        # Else, change on hover
                        f1['image'] = self.images['thumb']
                    # Do always
                    finally:
                        # If the last played song is in the last_active_list and the song is currently playing
                        if f1 in self.last_active_entry[0] and self.is_playing:
                            # Retain the thumb same as current playing
                            self.last_active_entry[0][0]['image'] = self.images['thumb_active']

                # Otherwise, change all elements and their children's background
                f1['bg'] = self.color.entry_back
                for f2 in f1.winfo_children():
                    f2['bg'] = self.color.entry_back

    # BACKEND function calls for Control Buttons
    def _play(self, song_id=None, force_play: bool = False, **element):
        # **element: Additional elements for visual change (e.g., entry thumbnail, entry heading)
        # If not forced to play individual file from song entries

        if not force_play:
            if not self.is_playing:
                self.tgl_play.configure(text="\ue103")
                self.status.set("NOW PLAYING")
                # Access the last_active_entry and change the thumb and heading style either hitting the controller
                # play button first or hitting the play button after invoking the stop button
                self.last_active_entry[0][0]['image'] = self.images['thumb_active']
                self.last_active_entry[0][1]['fg'] = self.color.ascent
                self.play_trigger = True
                if self.current_song_index is None:
                    self.current_song_index = 0
            elif self.is_paused:
                self.tgl_play.configure(text="\ue103")
                self.audio.play_pause(play_state="RESUME")
                self.is_paused = False
            elif not self.is_paused:
                self.tgl_play.configure(text="\ue102")
                self.audio.play_pause(play_state="PAUSE")
                self.is_paused = True
        # If forced to play individual file from song entries
        else:
            self._stop()
            song = self.backend.get_song(song_id)
            # Getting the current song index from the backend
            self.current_song_index = self.backend.current_songs.index(song)
            self.audio.load(song['path'])
            self.play_trigger = True
            self.tgl_play.configure(text="\ue103")
            self.status.set("NOW PLAYING")
            self.title.set(song['title'])
            # Change the thumb and the heading of the currently playing song's entry
            element['th'].configure(image=self.images['thumb_active'])
            element['hd'].configure(fg=self.color.ascent)
            # Update both active_entry and last_active_entry with the currently playing song
            self.active_entry = [(element['th'], element['hd'])]
            self.last_active_entry = [(element['th'], element['hd'], song['title'])]

    def progress(self):
        # Until the app gets termination signal, it will loop in the background
        while not self.app_terminate:

            # If any play button triggers
            if self.play_trigger:
                # Sets the total duration of the currently loaded song and total range of the seek bar
                self.duration.set(self._get_hms(seconds=self.audio.length()))
                self.seek_bar.configure(to=self.audio.length())
                # Will play the previously loaded song from _play method
                self.audio.play_pause(play_state='PLAY')

                self.play_trigger = False
                self.is_playing = True
            else:
                # If a song is playing or pausing
                if self.is_playing:
                    # When a song is now playing or resuming
                    if self.audio.currently_playing():
                        self.elapsed.set(self._get_hms(seconds=self.audio.current_position() / 1000))
                        self.position.set(self.audio.current_position() / 1000)
                    else:
                        # On ending of the current song
                        if self.audio.current_position() == -1:
                            self.elapsed.set("00:00:00")
                            self.position.set(0.0)
                            self.tgl_play.configure(text="\ue102")

                            # Loads the next song for autoplay if repeat mode if off
                            if not self.is_repeat:
                                require = self._load_next_prev('NEXT')
                                self._play(force_play=True, song_id=require['id'], th=require['entry_thumb'],
                                           hd=require['entry_heading'])
                                self.current_song_index += 1
                        # On pausing a song do nothing
                        # else: pass
                # If stop button is fired
                else:
                    self.elapsed.set("00:00:00")
                    self.position.set(0.0)
                    self.tgl_play.configure(text="\ue102")

            sleep(0.5)

        # Exit the thread on getting termination signal
        return None

    def _control_actions(self, button: Label, action: str):
        match action:
            case "previous":
                self._previous()
            case "stop":
                self._stop()
            case "next":
                self._next()
            case "repeat":
                self._repeat(element=button)

    def _load_next_prev(self, parameter: Literal["NEXT", "PREV"]):
        if self.current_song_index == 0:  # If it's playing the first song...
            next_index = self.current_song_index + 1
            prev_index = self.total_songs - 1  # Previous song will be the last one.
        elif self.current_song_index == self.total_songs - 1:  # If it's playing the last song...
            next_index = 0  # Next song will be the first one.
            prev_index = self.current_song_index - 1
        else:
            next_index, prev_index = self.current_song_index + 1, self.current_song_index - 1

        # Returns - song_id, element['th'], element['hd']
        match parameter:
            case "NEXT":
                return {"id"           : self.backend.current_songs[next_index]["id"],
                        "entry_thumb"  : self.all_entries[next_index][0],
                        "entry_heading": self.all_entries[next_index][1]}
            case "PREV":
                return {"id"           : self.backend.current_songs[prev_index]["id"],
                        "entry_thumb"  : self.all_entries[prev_index][0],
                        "entry_heading": self.all_entries[prev_index][1]}

    def _previous(self):
        required = self._load_next_prev('PREV')
        self._play(song_id=required['id'], force_play=True, th=required['entry_thumb'],
                   hd=required['entry_heading'])

    def _stop(self):
        # If a song is currently playing
        if self.is_playing:
            self.audio.stop()
            self.is_playing = False
            # If there is an entry in the active_entry list
            try:
                if self.active_entry[0]:
                    # Change the thumb and heading back to normal again
                    self.active_entry[0][0]['image'] = self.images['thumb']
                    self.active_entry[0][1]['fg'] = self.color.entry_heading_fore
                    # Update the last_active list with the song just stopped
                    self.last_active_entry = [(self.active_entry[0][0], self.active_entry[0][1])]
                    # Clear the active_entry list as no song will be played on hitting the stop button
                    self.active_entry.clear()
            except: pass
            finally:
                # Reset the styling of last active song entry
                self.last_active_entry[0][0]['image'] = self.images['thumb']
                self.last_active_entry[0][1]['fg'] = self.color.entry_heading_fore
                self.tgl_play.configure(text="\ue102")

    def _next(self):
        required = self._load_next_prev('NEXT')
        self._play(song_id=required['id'], force_play=True, th=required['entry_thumb'],
                   hd=required['entry_heading'])

    def _repeat(self, element: Label):
        if self.is_repeat:
            self.audio.loop(repeat=False)
            self._set_control(element, will_set=False)
            self.is_repeat = False
        else:
            self.audio.loop(repeat=True)
            self._set_control(element, will_set=True)
            self.is_repeat = True

    def _shuffle(self):
        pass

    def _que(self):
        pass

    def _timer(self):
        pass

    def _seek(self, e=None):
        position = self.position.get()
        self.audio.play_from(position=position)
        self.position.set(position)

    def _mute(self):
        if self.is_muted:
            self.audio.volume(kind="VOL", level=self.default_volume)
            self.volume.set(self.default_volume)
            self._set_control(self.tgl_mute, will_set=False)
            self.is_muted = False
        else:
            self.audio.volume(kind="MUTE")
            self.volume.set(0.0)
            self._set_control(self.tgl_mute, will_set=True)
            # If full enabled already, disable it by clicking on mute button
            if self.is_full:
                self._set_control(self.tgl_full, will_set=False)
                self.is_full = False
            self.is_muted = True

    def _volume(self, e=None):
        lvl = self.volume.get()
        self.audio.volume(kind="VOL", level=lvl)
        if lvl == 0.0 and not self.is_muted:
            self._set_control(self.tgl_mute, will_set=True)
            self.is_muted = True
        elif lvl == 1.0 and not self.is_full:
            self._set_control(self.tgl_full, will_set=True)
            self.is_full = True
        else:
            if self.is_muted:
                self._set_control(self.tgl_mute, will_set=False)
                self.is_muted = False
            if self.is_full:
                self._set_control(self.tgl_full, will_set=False)
                self.is_full = False

    def _full(self):
        if self.is_full:
            self.audio.volume(kind="VOL", level=self.default_volume)
            self.volume.set(self.default_volume)
            self._set_control(self.tgl_full, will_set=False)
            self.is_full = False
        else:
            self.audio.volume(kind="FULL")
            self.volume.set(1.0)
            self._set_control(self.tgl_full)
            # If mute enabled already, disable it by clicking on full button
            if self.is_muted:
                self._set_control(self.tgl_mute, will_set=False)
                self.is_muted = False
            self.is_full = True

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
                self.entry_box_bg.pack_forget()  # First clear the existing entry
            except: pass
            finally:
                self.make_song_list(self.backend.get_current_songs())  # Then, make new entries
                self.audio.load(file=self.backend.get_current_songs()[0]['path'])
                print(self.backend.current_songs)

    def _open_folder(self):
        self._exit_main_menu()
        self.status.set("OPENING FOLDER...")
        done = self.backend.open_folder(title=f"{self.app_name} - Choose a folder contains music to open with")
        if done:
            try:
                self.entry_box_bg.pack_forget()  # First clear the existing entry
            except: pass
            finally:
                self.make_song_list(self.backend.get_current_songs())  # Then, make new entries
                self.audio.load(file=self.backend.get_current_songs()[0]['path'])
                print(self.backend.current_songs)

    def _scan_filesystem(self):
        self._exit_main_menu()

    def _settings(self):
        self._exit_main_menu()

    def _about(self):
        self._exit_main_menu()

    def _close(self):
        self._exit_main_menu()
        self._stop()
        self.app_terminate = True
        self.audio.unload()
        self.main_window.destroy()

    # Custom functions
    @staticmethod
    def _get_hms(seconds: float):
        return strftime("%H:%M:%S", gmtime(seconds))

