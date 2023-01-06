# Gets a directory or path and find music files (e.g., *.mp3, *.wav, *.aac) for processing

# from tkinter import Frame
from tkinter.filedialog import askopenfilenames, askdirectory
from pygame import mixer
from os import curdir, listdir, getenv, PathLike
from os.path import isdir, isfile, exists


class Filesystem:

    def __init__(self, ):

        # Initialization defaults
        self.default_folder = getenv('USERPROFILE') + '/Music'
        self.current_folder: PathLike | str = ""
        self.current_files: list | tuple = []
        self.current_songs: list = [
            # {"id": "", "abs_path": "", "title": "", "artists": "", "album": "", "release": ""},
        ]

        # Audio initialization

    def open_files(self, title: str = "Open files"):
        files = askopenfilenames(defaultextension="*.mp3", initialdir=self.default_folder, title=title,
                                 filetypes=[("Mp3 Sounds", "*.mp3"), ("Wave Sounds", "*.wav"),
                                            ("All Music Files", "*.mp3"), ("All Music Files", "*.wav"), ])
        self.current_files = files

    def open_folder(self, title: str = "Choose a music folder"):
        folder = askdirectory(initialdir=self.default_folder, title=title, mustexist=True)
        print(folder)

    def _filter_music_file(self):
        pass


if __name__ == '__main__':
    ab = Filesystem()
    ab.open_folder()
