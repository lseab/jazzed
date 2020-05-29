import time
import os
from tkinter import *
from tkinter import messagebox, filedialog, ttk
from PIL import ImageTk, Image
from threading import Thread
from .playlistUI import PlaylistGUI, PlaylistTab, SongQueueTab
from ..backend import song_queue, audio_interface
from ..backend.errors import LoadError, FormatError


class MediaPlayer:

    def __init__(self, root, name, icon):
        self.name = name
        self.root = root
        self.icon_image = icon        
        self.ismuted = False
        self.generate_UI()
        self.init_protocols()
    
    def generate_UI(self):
        self.display()
        self.queuetab.load_queue()

    def init_protocols(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def start_audio(self):
        """
        Update active song information and start new audio stream.
        """
        try:
            audio_interface.start_audio(song_queue.active_song)  
            audio_interface.volume = self.volume.get()      
            songname = os.path.basename(song_queue.active_song.title)
            self.new_audio_UI(songname)      
            self.update_thread()
            self.play_btn.configure(image=self.pauseImage)
        except LoadError:
            self.statusbar['text'] = f'No audio loaded...'
        except FormatError:
            self.statusbar['text'] = f'Wrong audio format...'

    def toggle_play_pause(self):
        """
        Toggle play/pause
        """
        if audio_interface.active:
            audio_interface.play_pause()
            if audio_interface.stopped == True:
                self.statusbar['text'] = 'Music paused'
                self.play_btn.configure(image=self.playImage)
            else:
                songname = os.path.basename(song_queue.active_song.title)
                self.statusbar['text'] = f'Playing {songname}'
                self.play_btn.configure(image=self.pauseImage)
        else:
            self.statusbar['text'] = f'No audio loaded...'

    def stop_playback(self):
        """
        Closes audio stream.
        """
        audio_interface.close_stream()

    def next_song(self):
        """
        Play next song
        """
        try:
            song_queue.next_song()
            self.start_audio()
        except LoadError:
            self.statusbar['text'] = 'End of queue'
        except ValueError:
            self.statusbar['text'] = f'No audio loaded...'

    def play_again(self):
        """
        Play next song
        """
        self.start_audio()

    def rewind_audio(self):
        """
        Rewind audio by 10 seconds
        """
        if audio_interface.active:
            audio_interface.rewind_10()
        else:
            self.statusbar['text'] = f'No audio loaded...'

    def forward_audio(self):
        """
        Rewind audio by 10 seconds
        """
        if audio_interface.active:
            audio_interface.forward_10()
        else:
            self.statusbar['text'] = f'No audio loaded...'

    def mute_audio(self):
        """
        Mute audio (toggle between volume 0 and 70)
        """
        if self.ismuted:            
            self.set_volume(70.0)
        else:            
            self.set_volume(0.0)

    def set_volume(self, val):
        """
        Set volume to val
        """
        audio_interface.volume = val
        self.volume.set(val)

        if float(val) == 0.0:
            self.ismuted = True
            self.volume_btn.configure(image=self.muteImage)
        else:
            self.ismuted = False
            self.volume_btn.configure(image=self.volumeImage)

    def get_time(self):
        try:
            return audio_interface.time
        except LoadError:
            return 0

    def check_song_end(self):
        """
        Checks for flags for callback end in audio playback thread (keep_playing or loop).
        Adds appropriate event to tkinter event thread.
        """
        if audio_interface.playback_end:
            audio_interface.playback_end = False
            if self.repeatVar.get() == True:
                self.play_again()
            elif not song_queue.last_song:
                self.next_song()
            else:
                self.stop_playback()
                self.play_btn.configure(image=self.playImage)
                
    def update(self):
        """
        Target method for thread called at the start of each playback.
        Updates time while audio is playing and checks for flags after playback is stopped
        """
        while not audio_interface.playback_end:
            self.time_update()
        self.check_song_end()

    def update_thread(self):
        """
        Starts update thread
        """
        update_thread = Thread(target=self.update, daemon=True)
        update_thread.start()

    def select_file(self):
        """
        Returns user file selection
        """
        return filedialog.askopenfilename()

    def about(self):
        """
        Set app info in About info box
        """
        messagebox.showinfo(title=f'About {self.name}',message=f'{self.name} is an opensource audio player by @ElSeabso')

    def on_closing(self):
        """
        Closing message box
        """
        if messagebox.askokcancel("Quit", "Are you sure you want to quit?"):
            self.stop_playback()
            self.root.destroy()

    def new_audio_UI(self, song):
        """
        Update UI elements on song load.
        """
        self.progress_bar['value'] = 0
        self.progress_bar['maximum'] = len(audio_interface)
        self.statusbar['text'] = f'Loaded {song}'
        mins, secs = divmod(round(len(audio_interface) / 1000), 60)
        self.total_length['text'] = "{:02d}:{:02d}".format(mins, secs)

    def time_update(self):
        """
        Updates current time display within its own thread
        """
        mins, secs = divmod(round(self.get_time() / 1000), 60)
        self.current_time['text'] = "{:02d}:{:02d}".format(mins, secs)
        time.sleep(0.5)
        self.progress_bar['value'] = self.get_time()

    def display(self):
        """
        Generate Tkinter GUI
        """
        ## Meta
        self.root.title(self.name)
        self.root.wm_iconbitmap(self.icon_image)
        self.root.resizable(False, False)
        # Menu bar
        menubar = Menu(self.root)
        self.root.config(menu=menubar)        
        submenu = Menu(menubar)
        menubar.add_cascade(label='Help', menu=submenu)
        submenu.add_command(label='About', command=self.about)
        submenu.add_command(label='Exit', command=self.on_closing)
        # Status bar
        self.statusbar = ttk.Label(self.root, text='Welcome to Jazzed', relief=SUNKEN, font='Times 10 italic')
        self.statusbar.pack(side=BOTTOM, fill=X)

        ## TopFrame
        topframe = Frame(self.root)
        topframe.pack(padx=10, pady=15)
        ## List of playlists
        self.playListFrame = PlaylistGUI(topframe, self, width=300, height=500, borderwidth=3, relief=RAISED, background="PaleTurquoise1")
        self.playListFrame.grid(row=0, column=0)
        ## Playlist/Queue tabs
        self.tabs = ttk.Notebook(topframe)
        self.pltab = PlaylistTab(self.tabs, self)
        self.queuetab = SongQueueTab(self.tabs, self)
        ## Pack tabs
        self.tabs.add(self.pltab, text="Playlist")
        self.tabs.add(self.queuetab, text="Song Queue")
        self.tabs.select(self.queuetab)
        self.tabs.grid(row=0, column=1, padx=20)

        ## BottomFrame
        bottomframe = Frame(self.root)
        bottomframe.pack(padx=10, pady=15)
        ## Playbackframe
        playbackframe = Frame(bottomframe)
        playbackframe.pack()
        # Rewind button
        self.rewindImage = ImageTk.PhotoImage(Image.open(r'jazzed\frontend\static\rewind.png').convert('RGBA').resize((20,20)))
        self.rewind_btn = ttk.Button(playbackframe, image=self.rewindImage, command=self.rewind_audio)
        self.rewind_btn.image = self.rewindImage
        self.rewind_btn.grid(row=0, column=0, padx=20)
        # Back button
        self.backImage = ImageTk.PhotoImage(Image.open(r'jazzed\frontend\static\back.png').convert('RGBA').resize((30,30)))
        self.back_btn = ttk.Button(playbackframe, image=self.backImage, command=self.play_again)
        self.back_btn.image = self.backImage
        self.back_btn.grid(row=0, column=1, padx=10)
        # Play/Pause button
        self.playImage = ImageTk.PhotoImage(Image.open(r'jazzed\frontend\static\play.png').convert('RGBA').resize((30,30)))
        self.pauseImage = ImageTk.PhotoImage(Image.open(r'jazzed\frontend\static\pause.png').convert('RGBA').resize((30,30)))
        self.play_btn = ttk.Button(playbackframe, image=self.playImage, command=self.toggle_play_pause)
        self.play_btn.image = self.playImage
        self.play_btn.grid(row=0, column=2)
        # Next button
        self.nextImage = ImageTk.PhotoImage(Image.open(r'jazzed\frontend\static\next.png').convert('RGBA').resize((30,30)))
        self.next_btn = ttk.Button(playbackframe, image=self.nextImage, command=self.next_song)
        self.next_btn.image = self.nextImage
        self.next_btn.grid(row=0, column=3, padx=10)
        # Forward button
        self.forwardImage = ImageTk.PhotoImage(Image.open(r'jazzed\frontend\static\forward.png').convert('RGBA').resize((20,20)))
        self.forward_btn = ttk.Button(playbackframe, image=self.forwardImage, command=self.forward_audio)
        self.forward_btn.image = self.forwardImage
        self.forward_btn.grid(row=0, column=4, padx=20)

        ## Progressframe
        progressframe = Frame(bottomframe)
        progressframe.pack()
        # Time labels
        self.total_length = ttk.Label(progressframe, text=r"__:__")
        self.total_length.grid(row=0, column=2, padx=5, pady=10)
        self.current_time = ttk.Label(progressframe, text=r"00:00")
        self.current_time.grid(row=0, column=0, padx=5, pady=10)  
        # Progress Bar
        self.progress_bar = ttk.Progressbar(progressframe, variable=self.get_time(), length=500, mode='determinate')
        self.progress_bar.grid(row=0, column=1, pady=10)

        ## Volume frame
        volumeframe = Frame(bottomframe)
        volumeframe.pack(pady=20)
        # Volume button
        self.volumeImage = ImageTk.PhotoImage(Image.open(r'jazzed\frontend\static\volume.png').convert('RGBA').resize((20,20)))
        self.muteImage = ImageTk.PhotoImage(Image.open(r'jazzed\frontend\static\mute.png').convert('RGBA').resize((20,20)))
        self.volume_btn = ttk.Button(volumeframe, image=self.volumeImage, command=self.mute_audio)
        self.volume_btn.image = self.volumeImage
        self.volume_btn.grid(row=0, column=0, padx=5)
        # Volume control
        self.volume = Scale(volumeframe, from_=0, to=100, orient=HORIZONTAL, command=self.set_volume)
        self.volume.set(100)
        self.volume.grid(row=0, column=1)
        # Repeat button
        self.repeatImage = ImageTk.PhotoImage(Image.open(r'jazzed\frontend\static\repeat.png').convert('RGBA').resize((20,20)))
        self.repeatVar = BooleanVar()
        self.repeat_btn = ttk.Checkbutton(volumeframe, image=self.repeatImage, variable=self.repeatVar, onvalue=True, offvalue=False)
        self.repeat_btn.image = self.repeatImage
        self.repeat_btn.grid(row=0, column=2, padx=5)