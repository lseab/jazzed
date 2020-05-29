import os
from .database import session
from .database.schema import dbPlaylist, dbSong
from .errors import LoadError

class BaseList:

    def __init__(self, songs=[]):
        self.songs = songs

    def __len__(self):
        return len(self._songs)

    def __getitem__(self, index):
        return self._songs[index]

    def __setitem__(self, index, song):
        self._songs[index] = song

    def __delitem__(self, index):
        del self._songs[index]

    def append(self, song):
        self._songs.append(song)

    @property
    def songs(self):
        return self._songs

    @songs.setter
    def songs(self, songs):
        self._songs = songs


class LoadedPlaylist(BaseList):

    def __init__(self, id=None, name=None, songs=[]):
        super().__init__(songs)
        self.id = id
        self.name = name


class SongQueue(BaseList):

    def __init__(self, songs=[]):
        super().__init__(songs)
        self._active_song = None
        self.last_song = False

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
            raise LoadError("End of queue")

    def back_song(self):
        try:
            self.active_song = self._songs[self.active_song_index - 1]
        except:
            self.active_song = self.active_song

    def to_playlist(self, name, description):
        playlist = dbPlaylist(name=name, description=description)

        for song in self._songs:
            song_obj = session.query(dbSong).filter_by(title=song.title).first()
            if not song_obj:
                song_obj = dbSong(title=song.title)
            playlist.songs.append(song_obj)

        session.add(playlist)
        session.commit()

        return playlist


class Song:

    def __init__(self, title, artist=None):
        self.title = title
        self.artist = artist
        self.format = self.title.split('.')[-1]