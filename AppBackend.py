# Gets a directory or path and find music files (e.g., *.mp3, *.wav, *.aac) for processing

# from tkinter import Frame
from io import BytesIO
from builtins import callable
from threading import Thread
from time import sleep
from tkinter.filedialog import askopenfilenames, askdirectory
from random import randint, shuffle, choice

from PIL import ImageTk, Image
# <<<<<<< HEAD
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TDRC
from os import curdir, listdir, getenv, PathLike, chdir, environ, remove
# =======
from mutagen.id3 import ID3
from os import curdir, listdir, getenv, PathLike, chdir, environ, mkdir
# >>>>>>> central
from os.path import isdir, isfile, exists, join
from shutil import copy

environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'
from pygame import mixer


class Filesystem:

    def __init__(self):

        # Initialization defaults
        self.default_folder = getenv('USERPROFILE') + '/Music'
        self.current_folder: PathLike | str = ""
        self.current_files: list | tuple = []
        self.current_songs: list = [
            # {"id": "", "path": "", "title": "", "artists": "", "album": "", "release": "", "cover": ""},
        ]
        self.original_order: list = []  # Same list as above for backup/reset after toggling off the shuffle mode
        self.played_songs_history: list = []
# <<<<<<< HEAD
        self.song_playlist: dict = {
            "Favorite Songs": [],
            "Liked Songs": [],
        }
# =======
        self.default_coverart_folder = getenv('LOCALAPPDATA') + '/InnerTUNE/Cover Art'
        self.random_covers_path = "./Assets/images/Random cover/"
        self.random_covers = listdir(self.random_covers_path)
# >>>>>>> central

    def get_default(self):
        return self.default_folder

    def get_current_folder(self):
        return self.current_folder

    def get_current_files(self):
        return self.current_files

    def get_current_songs(self):
        return self.current_songs

    def get_song(self, song_id):
        for song in self.current_songs:
            if song['id'] == song_id:
                return song

    def set_played_song_history(self, song_title: str):
        """
        Put the currently played song's title to the played song history list.

        :param song_title: Currently played song title
        :type song_title: str
        :return: None
        :rtype: None
        """
        self.played_songs_history.append(song_title)

    def set_favorite_songs(self, song: dict):
        fav: list = self.song_playlist['Favorite Songs']
        if song not in fav:
            fav.append(song)
            return True
        else:
            return False

    def remove_favorite_song(self, song: dict):
        fav: list = self.song_playlist['Favorite Songs']
        # Should be called when set_favorite_songs method returns False
        fav.remove(song)

    def set_liked_songs(self, song: dict):
        liked: list = self.song_playlist['Liked Songs']
        if song not in liked:
            liked.append(song)
            return True
        else:
            return False

    def remove_liked_song(self, song: dict):
        liked: list = self.song_playlist['Liked Songs']
        # Should be called when set_liked_songs method returns False
        liked.remove(song)

    def add_to_playlist(self, playlist_name: str, song: dict):
        if playlist_name not in self.song_playlist:
            self.song_playlist[playlist_name] = []

        if song not in self.song_playlist[playlist_name]:
            self.song_playlist[playlist_name].append(song)
            return True
        else:
            return False

    def make_shuffle(self, mode: bool = True):
        if mode:
            shuffle(self.current_songs)
        else:
            self.current_songs = self.original_order.copy()

    def make_play_next(self, set_index: int, song: dict):
        # Insert the specified song at the given index by popping it from its original position
        self.current_songs.insert(set_index, self.current_songs.pop(self.current_songs.index(song)))

    def open_files(self, title: str = "Open files"):
        files = askopenfilenames(defaultextension="*.mp3", initialdir=self.default_folder, title=title,
                                 filetypes=[("Mp3 Sounds", "*.mp3"), ("Wave Sounds", "*.wav"),
                                            ("All Music Files", "*.mp3"), ("All Music Files", "*.wav"), ])
        if files:
            self.current_folder = ""
            self.current_files.clear()
            self.current_songs.clear()
            for file in files:
                self.current_files.append(file)
            # self.current_folder = files[0].rsplit("/", 1)[0]
            self._extract_music_info()
            return True

    def open_folder(self, title: str = "Choose a music folder"):
        folder = askdirectory(initialdir=self.default_folder, title=title, mustexist=True)
        if folder:
            found_any_file = False
            for file in listdir(folder):
                if isfile(f"{folder}/{file}") and (file.endswith(".mp3") or file.endswith(".wav")):
                    if not found_any_file:
                        self.current_files.clear()
                        self.current_songs.clear()
                        found_any_file = True
                    self.current_files.append(f"{folder}/{file}")

            if found_any_file:
                self.current_folder = folder
                self._extract_music_info()
                return True

    def _extract_music_info(self):
        # chdir(self.current_folder)
        for file in self.current_files:
            song_id = randint(10000, 99999)

            title = file.rsplit("/", 1)[1].rstrip(".mp3").rstrip(".wav")
            # title = ttl[:125] + " ..." if len(file) > 125 else ttl
            duration = artists = album = year = "Unknown"
            cover = f"{self.default_coverart_folder}/{song_id}.jpg"
            try:
                tag = ID3(file)
                try:
                    if not exists(self.default_coverart_folder):
                        mkdir(self.default_coverart_folder)
                    cover_data = tag.get("APIC:").data
                    with open(cover, 'wb') as fl:
                        fl.write(cover_data)
                except:
                    cover = None
                ti, ar, al, ye = tag.get('TIT2').text[0], tag.get('TPE1').text[0], tag.get('TALB').text[0], tag.get('TDRC').text[0]
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
                # {"id": "", "path": "", "title": "", "artists": "", "album": "", "release": "", "cover": ""},
                self.current_songs.append(
                    {"id": song_id, "path": file, "title": title, "artists": artists, "album": album, "release": year,
                     "cover": cover}
                )
                self.original_order = self.current_songs.copy()

    def save_music_info(self, song_path: str, **new_info):
        tag = ID3(song_path)
        # TODO: Have to Fix
        tag.add(TIT2(text=new_info['title']))
        tag.add(TPE1(text=new_info['artists']))
        tag.add(TALB(text=new_info['album']))
        tag.add(TDRC(text=new_info['year']))
        tag.save()

    def delete_song(self, song: dict):
        remove(song['path'])
        self.current_songs.remove(song)


class AudioPlayer:
    from typing import Literal

    def __init__(self, initial_volume: float = 0.2):
        mixer.init(channels=2)
        mixer.music.set_volume(initial_volume)
        self.loaded_file = ""

    def load(self, file):
        mixer.music.load(file)
        self.loaded_file = file

    def length(self) -> float:
        return mixer.Sound(self.loaded_file).get_length()

    @staticmethod
    def play_pause(play_state: Literal["PLAY", "PAUSE", "RESUME"]):
        match play_state:
            case "PLAY":
                mixer.music.play()
            case "PAUSE":
                mixer.music.pause()
            case "RESUME":
                mixer.music.unpause()

    @staticmethod
    def play_from(position: float):
        mixer.music.play(start=position)

    @staticmethod
    def current_position() -> int:
        return mixer.music.get_pos()

    @staticmethod
    def currently_playing() -> bool:
        return mixer.music.get_busy()

    @staticmethod
    def stop():
        mixer.music.stop()

    @staticmethod
    def unload():
        mixer.music.unload()
        mixer.quit()

    @staticmethod
    def queue(file):
        mixer.music.queue(file)

    # @staticmethod
    def loop(self, repeat: bool = True):
        if repeat:
            mixer.music.queue(self.loaded_file, loops=-1)
        else:
            # TODO: To be fixed
            mixer.music.queue(self.loaded_file, loops=0)

    @staticmethod
    def volume(kind: Literal["MUTE", "FULL", "VOL"], level: float = ...):
        match kind:
            case "MUTE":
                mixer.music.set_volume(0.0)
            case "FULL":
                mixer.music.set_volume(1.0)
            case "VOL":
                mixer.music.set_volume(level)


class SleepTimer:
    from datetime import time, datetime
    from typing import Literal

    def __init__(self):
        self.current_time: int = 0
        self.timer_switch: bool = False

    def add_new_timer(self, minutes: int):
        # Actually get seconds from the minutes parameter, thus multiplied with 60 to get the minutes
        self.current_time = minutes * 60

    def turn_switch_timer(self, switch: Literal["ON", "OFF"], termination_func=...):
        match switch:
            case "ON":
                if not callable(termination_func):
                    raise TypeError("Termination function not defined/callable!\n"
                                    "A name of a callable termination function or a lambda function "
                                    "must have to specify upon turning the timer switch ON.")
                self.timer_switch = True
                Thread(target=self.start_timer, args=(termination_func,), daemon=True).start()
            case "OFF":
                self.current_time = 0
                self.timer_switch = False

    def start_timer(self, func):
        countdown_time = self.current_time

        while self.timer_switch:
            # TODO: Timer function have to add
            if countdown_time > 0:
                countdown_time -= 1
            else:
                self.current_time = 0
                self.timer_switch = False
                # Runs the termination function on TIME UP
                func()
            sleep(1)

        self.current_time = 0
        # Return None for the interrupting the current timer and terminate the thread
        return None


if __name__ == '__main__':
    # For testing purposes
    pass
