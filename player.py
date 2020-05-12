import os
import time
from threading import Thread
from audio import AudioInterface, LoadError
from ui import MediaFrame
from playlist import Playlist


class MediaPlayer:

    def __init__(self, root, name, icon, playlist=Playlist()):
        self.name = name
        self.icon = icon
        self.ismuted = False
        self.playlist = playlist
        self.audio = AudioInterface()
        self.UI = MediaFrame(self, root)

    def user_select_song(self, event):
        """
        Get user file selection.
        This is only ever called on double-click of file in Songbox.
        """
        user_selection_index = int(self.UI.songbox.curselection()[0])
        song_selection = self.playlist[user_selection_index]
        if song_selection != self.playlist.active_song:
            self.playlist.active_song = song_selection
            self.start_audio()

    def start_audio(self):
        """
        Update active song inforation and start new audio stream.
        """
        try:
            self.audio.start_audio(self.playlist.active_song)        
            songname = os.path.basename(self.playlist.active_song)
            self.UI.new_audio_UI(songname)      
            self.update_thread()
            self.audio.volume = self.UI.volume.get()
            self.UI.play_btn.configure(image=self.UI.pauseImage)
        except:
            self.UI.statusbar['text'] = f'No audio loaded...'

    def toggle_play_pause(self):
        """
        Toggle play/pause
        """
        if self.audio.active:
            self.audio.play_pause()
            if self.audio.stopped == True:
                self.UI.statusbar['text'] = 'Music paused'
                self.UI.play_btn.configure(image=self.UI.playImage)
            else:
                songname = os.path.basename(self.playlist.active_song)
                self.UI.statusbar['text'] = f'Playing {songname}'
                self.UI.play_btn.configure(image=self.UI.pauseImage)
        else:
            self.UI.statusbar['text'] = f'No audio loaded...'

    def rewind_audio(self):
        """
        Rewind audio by 10 seconds
        """
        if self.audio.active:
            self.audio.rewind_10()
        else:
            self.UI.statusbar['text'] = f'No audio loaded...'

    def forward_audio(self):
        """
        Rewind audio by 10 seconds
        """
        if self.audio.active:
            self.audio.forward_10()
        else:
            self.UI.statusbar['text'] = f'No audio loaded...'

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
        self.audio.volume = val
        self.UI.volume.set(val)

        if float(val) == 0.0:
            self.ismuted = True
            self.UI.volume_btn.configure(image=self.UI.muteImage)
        else:
            self.ismuted = False
            self.UI.volume_btn.configure(image=self.UI.volumeImage)

    def add_to_playlist(self):
        """
        Opens file box and adds user selection to playlist object and songbox UI
        """
        user_selection = self.UI.select_file()
        if user_selection != "":            
            self.playlist += user_selection
            self.UI.add_to_playlist(user_selection)

    def remove_from_playlist(self):
        """
        Removes cursor selection from playlist object and songbox UI
        """
        try:
            user_selection_index = int(self.UI.songbox.curselection()[0])
            del self.playlist[user_selection_index]
            self.UI.remove_from_playlist(user_selection_index)
        except IndexError:
            self.UI.statusbar['text'] = f'No song selected'

    def stop_playback(self):
        """
        Closes audio stream.
        """
        self.audio.close_stream()

    def next_song(self):
        """
        Play next song
        """
        try:
            self.playlist.next_song()
            self.start_audio()
        except LoadError:
            self.UI.statusbar['text'] = 'End of playlist'
        except ValueError:
            self.UI.statusbar['text'] = f'No audio loaded...'

    def play_again(self):
        """
        Play next song
        """
        self.start_audio()

    def get_time(self):
        try:
            return self.audio.time
        except LoadError:
            return 0

    def check_song_end(self):
        """
        Checks for flags for callback end in audio playback thread (keep_playing or loop).
        Adds appropriate event to tkinter event thread.
        """
        if self.audio.playback_end:
            self.audio.playback_end = False
            if self.UI.repeatVar.get() == True:
                self.play_again()
            elif not self.playlist.last_song:
                self.next_song()
            else:
                self.stop_playback()
                self.UI.play_btn.configure(image=self.UI.playImage)
                
    def update(self):
        """
        Target method for thread called at the start of each playback.
        Updates time while audio is playing and checks for flags after playback is stopped
        """
        while not self.audio.playback_end:
            self.UI.time_update()
        self.check_song_end()

    def update_thread(self):
        """
        Starts update thread
        """
        update_thread = Thread(target=self.update, daemon=True)
        update_thread.start()