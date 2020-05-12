from ttkthemes import ThemedTk
from player import MediaPlayer
from playlist import Playlist


if __name__ == '__main__':
    root = ThemedTk(theme="plastik")
    MediaPlayer(root, 'Jazzed', r'static\jazzed.ico', Playlist.test_playlist())
    root.mainloop()