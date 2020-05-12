import os

class LoadError(TypeError):
    pass


class Playlist:

    def __init__(self, songs=[]):
        self._songs = songs
        self._active_song = None
        self.last_song = False

    def __iadd__(self, song):
        self._songs.append(song)
        return self

    def __isub__(self, song):
        self._songs.remove(song)
        return self

    def __len__(self):
        return len(self._songs)

    def __getitem__(self, index):
        return self._songs[index]

    def __setitem__(self, index, song):
        self._songs[index] = song

    def __delitem__(self, index):
        del self._songs[index]

    @property
    def active_song(self):
        return self._active_song

    @active_song.setter
    def active_song(self, song):
        try:
            assert song in self._songs
            if song == self._songs[-1]: self.last_song = True
            else: self.last_song = False
            self._active_song = song
        except AssertionError:
            print('Cannot activate song')

    @property
    def active_song_index(self):
        return self._songs.index(self.active_song)

    def next_song(self):
        try:
            self.active_song = self._songs[self.active_song_index + 1]
        except IndexError:
            raise LoadError("End of playlist")

    def back_song(self):
        try:
            self.active_song = self._songs[self.active_song_index - 1]
        except:
            self.active_song = self.active_song

    @classmethod
    def test_playlist(cls):
        return cls([
            os.path.join(r'D:\My documents\Sénégal\Chorales\Fadiouth\Wav', r'0. Entrée.wav'),
            os.path.join(r'D:\My documents\Sénégal\Chorales\Fadiouth\Wav', r'1. Ta parole.wav'),
            os.path.join(r'D:\My documents\Sénégal\Chorales\Fadiouth\Wav', r'2..wav'),
            os.path.join(r'D:\My documents\Sénégal\Chorales\Fadiouth\Wav', r'6.1.wav'),
            os.path.join(r'D:\My documents\Sénégal\Chorales\Fadiouth\Wav', r'7..wav')
        ])