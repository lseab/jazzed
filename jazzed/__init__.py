from ttkthemes import ThemedTk
from jazzed.frontend.playerUI import MediaPlayer
from jazzed.backend.base import Song
from jazzed.backend import song_queue

def create_app(name="", icon="", song_list=[]):
    root = ThemedTk(theme="plastik")
    songs = [Song(song) for song in song_list]
    song_queue.songs = songs
    MediaPlayer(root, name=name, icon=icon)
    root.mainloop()