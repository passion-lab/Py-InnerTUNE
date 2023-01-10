# Gets a directory or path and find music files (e.g., *.mp3, *.wav, *.aac) for processing

# from tkinter import Frame
from io import BytesIO
from tkinter.filedialog import askopenfilenames, askdirectory
from random import randint, random
from PIL import ImageTk, Image
from mutagen.id3 import ID3
from os import curdir, listdir, getenv, PathLike, chdir, environ
from os.path import isdir, isfile, exists, join

environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'
from pygame import mixer


class Filesystem:

    def __init__(self, ):

        # Initialization defaults
        self.default_folder = getenv('USERPROFILE') + '/Music'
        self.current_folder: PathLike | str = ""
        self.current_files: list | tuple = []
        self.current_songs: list = [
            # {"id": "", "abs_path": "", "title": "", "artists": "", "album": "", "release": ""},
        ]

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
            ttl = file.rsplit("/", 1)[1].rstrip(".mp3").rstrip(".wav")
            title = ttl[:125] + " ..." if len(file) > 125 else ttl
            duration = artists = album = year = "Unknown"
            cover = ...
            try:
                tag = ID3(file)

                # TODO: Cover art will have to be added
                # co = ImageTk.PhotoImage(Image.open(BytesIO(tag.get("APIC:").data)).resize((32, 32), resample=0))
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
                # {"id": "", "path": "", "title": "", "artists": "", "album": "", "release": ""},
                self.current_songs.append(
                    {"id": randint(10000, 99999), "path": file, "title": title, "artists": artists, "album": album, "release": year}
                )


class AudioPlayer:
    from typing import Literal

    def __init__(self, initial_volume: float = 0.2):
        mixer.init(channels=2)
        mixer.music.set_volume(initial_volume)
        self.loaded_file = ""

    def load(self, file):
        mixer.music.load(file)
        self.loaded_file = file

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
    def stop():
        mixer.music.stop()

    @staticmethod
    def unload():
        mixer.music.unload()
        mixer.quit()

    @staticmethod
    def queue(files):
        mixer.music.queue(files)

    @staticmethod
    def volume(kind: Literal["MUTE", "FULL", "VOL"], level: float = ...):
        match kind:
            case "MUTE":
                mixer.music.set_volume(0.0)
            case "FULL":
                mixer.music.set_volume(1.0)
            case "VOL":
                mixer.music.set_volume(level)


if __name__ == '__main__':
    ab = Filesystem()
    ab.open_files()
    # ab.open_folder()
    print(ab.get_current_folder())
    print(ab.get_current_files())
    print(ab.get_current_songs())

    ad = AudioPlayer()
