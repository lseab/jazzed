from . import Base, db_engine
from sqlalchemy import Column, Integer, String, Table, ForeignKey 
from sqlalchemy.orm import relationship


playlists_songs = Table('association', Base.metadata,
    Column('playlist_id', Integer, ForeignKey('playlists.id')),
    Column('song_id', Integer, ForeignKey('songs.id'))
)

class dbSong(Base):
    __tablename__ = 'songs'

    id = Column(Integer, primary_key=True)
    title = Column(String)

    playlists = relationship("dbPlaylist", 
                            secondary=playlists_songs)

    def __repr__(self):
        return f"<dbSong(name={self.title})>"


class dbPlaylist(Base):
    __tablename__ = 'playlists'
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)

    songs = relationship("dbSong", 
                            secondary=playlists_songs)

    def __repr__(self):
        return f"<dbPlaylist(name={self.name}, description={self.description})>"

Base.metadata.create_all(db_engine)