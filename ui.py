import time
import os
from tkinter import *
from tkinter import messagebox, filedialog, ttk
from PIL import ImageTk, Image
from threading import Thread


class MediaFrame:

    def __init__(self, player, root):
        self.player = player
        self.root = root
        self.icon_image = None
        self.generate_UI()
        self.init_protocols()

    def init_protocols(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def about(self):
        """
        Set app info in About info box
        """
        messagebox.showinfo(title=f'About {self.player.name}',message=f'{self.player.name} is an opensource audio player by @ElSeabso')
        self.icon_image = self.icon

    def select_file(self):
        """
        Returns user file selection
        """
        return filedialog.askopenfilename()

    def load_playlist(self):
        for song in self.player.playlist:
            self.add_to_playlist(song)

    def add_to_playlist(self, song):
        """
        Insert new user selection into playlist
        """
        songname = os.path.basename(song)
        self.songbox.insert(END, songname)

    def remove_from_playlist(self, index):
        """
        Remove song selection from playlist
        """
        self.statusbar['text'] = f'Removed {self.songbox.get(index)} from playlist'
        self.songbox.delete(index)

    def on_closing(self):
        """
        Closing message box
        """
        if messagebox.askokcancel("Quit", "Are you sure you want to quit?"):
            self.player.stop_playback()
            self.root.destroy()

    def new_audio_UI(self, song):        
        self.progress_bar['value'] = 0
        self.progress_bar['maximum'] = len(self.player.audio)
        self.statusbar['text'] = f'Loaded {song}'
        mins, secs = divmod(round(len(self.player.audio) / 1000), 60)
        self.total_length['text'] = "Total length - {:02d}:{:02d}".format(mins, secs)

    def time_update(self):
        """
        Updates current time display within its own thread
        """
        mins, secs = divmod(round(self.player.get_time() / 1000), 60)
        self.current_time['text'] = "Current Time - {:02d}:{:02d}".format(mins, secs)
        time.sleep(0.5)
        self.progress_bar['value'] = self.player.get_time()

    def generate_UI(self):
        self.display()
        self.load_playlist()

    def display(self):
        """
        Generate Tkinter GUI
        """
        ## Meta
        self.root.title(self.player.name)
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

        # Frames
        leftframe = Frame(self.root)
        rightframe = Frame(self.root)
        leftframe.pack(side=LEFT)
        rightframe.pack()

        # In rightframe
        topframe = Frame(rightframe)
        topframe.pack(padx=10, pady=15)
        middleframe = Frame(rightframe)
        middleframe.pack(padx=10, pady=15)
        bottomframe = Frame(rightframe)
        bottomframe.pack(padx=10, pady=10)

        ## Topframe
        # Time labels
        self.total_length = ttk.Label(topframe, text=r"Total length - __:__")
        self.total_length.pack(pady=10)
        self.current_time = ttk.Label(topframe, text=r"Current Time - 00:00")
        self.current_time.pack(pady=10)        

        ## Middleframe
        ## Progressframe
        progressframe = Frame(middleframe)
        progressframe.pack(pady=20)
        # Progress button
        self.progress_bar = ttk.Progressbar(progressframe, variable=self.player.get_time(), length=300, mode='determinate')
        self.progress_bar.pack(pady=20)
        ## Playbackframe
        playbackframe = Frame(middleframe)
        playbackframe.pack()
        # Back button
        self.backImage = ImageTk.PhotoImage(Image.open(r'static\back.png').convert('RGBA').resize((50,50)))
        self.back_btn = ttk.Button(playbackframe, image=self.backImage, command=self.player.play_again)
        self.back_btn.image = self.backImage
        self.back_btn.grid(row=0, column=0, padx=10)
        # Play/Pause button
        self.playImage = ImageTk.PhotoImage(Image.open(r'static\play.png').convert('RGBA').resize((50,50)))
        self.pauseImage = ImageTk.PhotoImage(Image.open(r'static\pause.png').convert('RGBA').resize((50,50)))
        self.play_btn = ttk.Button(playbackframe, image=self.playImage, command=self.player.toggle_play_pause)
        self.play_btn.image = self.playImage
        self.play_btn.grid(row=0, column=1, padx=10)
        # Next button
        self.nextImage = ImageTk.PhotoImage(Image.open(r'static\next.png').convert('RGBA').resize((50,50)))
        self.next_btn = ttk.Button(playbackframe, image=self.nextImage, command=self.player.next_song)
        self.next_btn.image = self.nextImage
        self.next_btn.grid(row=0, column=2, padx=10)

        ## Bottom Frame
        ## Playback frame
        playbackframe = Frame(bottomframe)
        playbackframe.grid(row=0, column=0, padx=10)
        # Rewind button
        self.rewindImage = ImageTk.PhotoImage(Image.open(r'static\rewind.png').convert('RGBA').resize((30,30)))
        self.rewind_btn = ttk.Button(playbackframe, image=self.rewindImage, command=self.player.rewind_audio)
        self.rewind_btn.image = self.rewindImage
        self.rewind_btn.grid(row=0, column=0, padx=5)
        # Forward button
        self.forwardImage = ImageTk.PhotoImage(Image.open(r'static\forward.png').convert('RGBA').resize((30,30)))
        self.forward_btn = ttk.Button(playbackframe, image=self.forwardImage, command=self.player.forward_audio)
        self.forward_btn.image = self.forwardImage
        self.forward_btn.grid(row=0, column=1, padx=5)

        ## Volume frame
        volumeframe = Frame(bottomframe)
        volumeframe.grid(row=0, column=1,padx=10)
        # Volume button
        self.volumeImage = ImageTk.PhotoImage(Image.open(r'static\volume.png').convert('RGBA').resize((20,20)))
        self.muteImage = ImageTk.PhotoImage(Image.open(r'static\mute.png').convert('RGBA').resize((20,20)))
        self.volume_btn = ttk.Button(volumeframe, image=self.volumeImage, command=self.player.mute_audio)
        self.volume_btn.image = self.volumeImage
        self.volume_btn.grid(row=0, column=0, padx=5)
        # Volume control
        self.volume = Scale(volumeframe, from_=0, to=100, orient=HORIZONTAL, command=self.player.set_volume)
        self.volume.set(100)
        self.volume.grid(row=0, column=1)
        # Repeat button
        self.repeatImage = ImageTk.PhotoImage(Image.open(r'static\repeat.png').convert('RGBA').resize((20,20)))
        self.repeatVar = BooleanVar()
        self.repeat_btn = ttk.Checkbutton(volumeframe, image=self.repeatImage, variable=self.repeatVar, onvalue=True, offvalue=False)
        self.repeat_btn.image = self.repeatImage
        self.repeat_btn.grid(row=0, column=2, padx=5)

        ## Leftframe
        # Song list
        self.songbox = Listbox(leftframe)
        self.songbox.pack(padx=20)
        self.songbox.focus()
        self.songbox.bind('<Double-Button-1>', self.player.user_select_song)
        # Add button
        buttonframe = Frame(leftframe)
        buttonframe.pack()
        self.add_btn = ttk.Button(buttonframe, text="Add", command=self.player.add_to_playlist)
        self.del_btn = ttk.Button(buttonframe, text="Del", command=self.player.remove_from_playlist)
        self.add_btn.grid(row=0, column=0, padx=10, pady=10)
        self.del_btn.grid(row=0, column=1, padx=10, pady=10)
