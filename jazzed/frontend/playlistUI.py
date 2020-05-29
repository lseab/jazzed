import os
from tkinter import *
from tkinter import ttk
from ..backend import loaded_playlist, song_queue
from ..backend.database import session
from ..backend.database.schema import dbPlaylist, dbSong
from ..backend.base import Song


class PlaylistGUI(Frame):

    def __init__(self, master, gui, **kwargs):
        super().__init__(master=master, **kwargs)
        self.pack()
        self.propagate(0)
        self.gui = gui
        self.playlist_label = Label(self, text=r"Playlists: ", font='Times 18 bold')
        self.playlist_label['bg'] = self.playlist_label.master['bg']
        self.playlist_label.pack(anchor=NW, pady=20)
        self.get_playlists()

    def add_button(self, playlist):
        self.playlist_btn = PlaylistButton(self, self.gui, playlist)
        self.playlist_btn.pack(anchor=W, pady=2)

    def get_playlists(self):
        playlists = session.query(dbPlaylist).all()
        for playlist in playlists:
            self.add_button(playlist)


class PlaylistButton(Frame):

    def __init__(self, master, gui, playlist):
        super().__init__(master=master)
        self.master = master
        self.gui = gui
        self.playlist = playlist
        self.to_option = Button(self, text=str(playlist.name), 
                                background=master['background'],
                                command=self.load_playlist)
        self.to_option.pack()

    def load_playlist(self, *args):
        songs = session.query(dbSong).filter(dbSong.playlists.any(id=self.playlist.id)).all()
        songs = [Song(song.title) for song in songs]
        loaded_playlist.id = self.playlist.id
        loaded_playlist.name = self.playlist.name
        loaded_playlist.songs = songs
        self.gui.pltab.load_playlist()
        self.gui.tabs.select(0)


class PlaylistPopup(Toplevel):

    def __init__(self, master, gui):
        super().__init__(master=master)
        self.gui = gui
        self.resizable(False, False)
        self.UI()
        self.geometry(self.center_geometry())
        self.grab_set()

    def UI(self):
        self.label = Label(self, text="New Playlist")
        self.label.pack(pady=30)
        nameFrame = Frame(self)
        nameFrame.pack(pady=10)
        self.name_label = Label(nameFrame, text="Name:  ")
        self.name_label.grid(row=0, column=0, padx=10)
        self.name = StringVar()
        self.input_name = Entry(nameFrame, width=30, textvariable=self.name)
        self.input_name.grid(row=0, column=1, padx=10)
        descFrame = Frame(self)
        descFrame.pack(pady=10)
        self.desc_label = Label(descFrame, text="Description:  ")
        self.desc_label.grid(row=0, column=0, padx=10)
        self.input_desc = Text(descFrame, width=30, height=10)
        self.input_desc.grid(row=0, column=1, padx=10)
        self.add_btn = ttk.Button(self, text="Add Playlist", command=self.new_playlist)
        self.add_btn.pack(pady=10)

    def center_geometry(self):
        self.update_idletasks()
        x = self.master.winfo_rootx() + (self.master.winfo_width() - self.winfo_width()) / 2
        y = self.master.winfo_rooty() + (self.master.winfo_height() - self.winfo_height()) / 2
        return "+%d+%d" % (x, y)

    def new_playlist(self):
        name = self.name.get()
        description = self.input_desc.get("1.0", END)
        playlist = song_queue.to_playlist(name, description)
        self.gui.add_button(playlist)
        self.destroy()


class PlaylistTab(Frame):

    def __init__(self, master, gui):
        super().__init__(master=master)
        self.pack()
        self.gui = gui
        # Song list
        self.plbox = Listbox(self, width=50, height=25)
        self.plbox.pack(padx=20)
        self.plbox.focus()
        self.plbox.bind('<Double-Button-1>', self.new_queue)
        # Buttons
        buttonframe = Frame(self)
        buttonframe.pack()
        self.add_btn = ttk.Button(buttonframe, text="Add", command=self.select_new_song)
        self.del_btn = ttk.Button(buttonframe, text="Del", command=self.remove_from_playlist)
        self.add_btn.grid(row=0, column=0, padx=10, pady=10)
        self.del_btn.grid(row=0, column=1, padx=10, pady=10)

    def new_queue(self, *args):
        user_selection_index = int(self.plbox.curselection()[0])
        songs = loaded_playlist.songs[user_selection_index:]
        song_queue.songs = songs
        song_queue.active_song = loaded_playlist.songs[user_selection_index]
        self.gui.queuetab.load_queue()
        self.gui.start_audio()

    def select_new_song(self, *args):
        user_selection = self.gui.select_file()
        if user_selection != "":
            self.add_to_playlist(user_selection)

    def add_to_playlist(self, selection):
        """
        Opens file box and adds user selection to queue object and songbox UI
        """  
        song = Song(title=selection)
        loaded_playlist.append(song)

        songQuery = session.query(dbSong).filter_by(title=song.title).first()
        dbQuery = session.query(dbPlaylist).filter_by(id=loaded_playlist.id).first()
        if not songQuery:
            songQuery = dbSong(title=song.title)
        dbQuery.songs.append(songQuery)
        session.commit()

        songname = os.path.basename(song.title)
        self.plbox.insert(END, songname)

    def remove_from_playlist(self, *args):
        """
        Removes cursor selection from queue object and songbox UI
        """
        try:
            user_selection_index = int(self.plbox.curselection()[0])
            song = loaded_playlist[user_selection_index]
            songQuery = session.query(dbSong).filter_by(title=song.title).first()
            dbQuery = session.query(dbPlaylist).filter_by(id=loaded_playlist.id).first()
            songQuery.playlists.remove(dbQuery)
            session.commit()
            del loaded_playlist[user_selection_index]
            self.gui.statusbar['text'] = f'Removed {self.plbox.get(user_selection_index)} from playlist'
            self.plbox.delete(user_selection_index)
            self.update_idletasks()
        except IndexError:
            self.gui.statusbar['text'] = f'No song selected'

    def load_playlist(self):
        self.plbox.delete('0','end')
        for song in loaded_playlist.songs:
            songname = os.path.basename(song.title)
            self.plbox.insert(END, songname)


class SongQueueTab(Frame):

    def __init__(self, master, gui):
        super().__init__(master=master)
        self.pack()
        self.gui = gui
        # Song list
        self.songbox = Listbox(self, width=50, height=25)
        self.songbox.pack(padx=20)
        self.songbox.focus()
        self.songbox.bind('<Double-Button-1>', self.start_song)
        # Buttons
        buttonframe = Frame(self)
        buttonframe.pack()
        self.add_btn = ttk.Button(buttonframe, text="Add", command=self.select_new_song)
        self.del_btn = ttk.Button(buttonframe, text="Del", command=self.remove_from_queue)
        self.save_btn = ttk.Button(buttonframe, text="Save to playlist", command=self.playlist_popup)
        self.add_btn.grid(row=0, column=0, padx=10, pady=10)
        self.del_btn.grid(row=0, column=1, padx=10, pady=10)
        self.save_btn.grid(row=0, column=2, padx=10, pady=10)

    def start_song(self, *args):
        """
        Get user file selection.
        This is only ever called on double-click of file in Songbox.
        """
        user_selection_index = int(self.songbox.curselection()[0])
        song_selection = song_queue[user_selection_index]
        if song_selection != song_queue.active_song:
            song_queue.active_song = song_selection
            self.gui.start_audio()

    def select_new_song(self, *args):
        user_selection = self.gui.select_file()
        if user_selection != "":
            self.add_to_queue(user_selection)

    def add_to_queue(self, selection):
        """
        Opens file box and adds user selection to queue object and songbox UI
        """    
        song = Song(title=selection)
        song_queue.append(song)
        songname = os.path.basename(song.title)
        self.songbox.insert(END, songname)

    def remove_from_queue(self, *args):
        """
        Removes cursor selection from queue object and songbox UI
        """
        try:
            user_selection_index = int(self.songbox.curselection()[0])
            del song_queue[user_selection_index]
            self.gui.statusbar['text'] = f'Removed {self.songbox.get(user_selection_index)} from queue'
            self.songbox.delete(user_selection_index)
        except IndexError:
            self.gui.statusbar['text'] = f'No song selected'

    def load_queue(self):
        self.songbox.delete('0','end')
        for song in song_queue:            
            songname = os.path.basename(song.title)
            self.songbox.insert(END, songname)

    def playlist_popup(self):
        self.window = PlaylistPopup(self.gui.root, self.gui.playListFrame)
        self.window.focus_set()