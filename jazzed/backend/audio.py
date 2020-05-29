import os
import sounddevice as sd
import soundfile as sf
import numpy as np
from .errors import LoadError, FormatError


class AudioInterface():

    def __init__(self):
        self._audio_file_length = 0
        self._stopped = True
        self._volume = 100.0
        self._frame = 0
        self.stream = None
        self._audio = None
        self.raw_data = None
        self.blocksize = 2048
        self._next = False
        self._back = False
        self._playback_end = False

    def __len__(self):
        """
        Returns the length of the audio clip in milliseconds
        """
        return self._audio_file_length 

    @property
    def audio(self):
        if self._audio is None:
            raise LoadError('Audio is not loaded')
        else:
            return self._audio

    @audio.setter
    def audio(self, audio):
        self._audio = audio

    @property
    def active(self):
        try:
            return self.stream.active
        except:
            return False

    @property
    def volume(self) -> float:
        return self._volume

    @volume.setter
    def volume(self, value):
        self._volume = min(float(value), 100.0)

    @property
    def frame(self) -> int:
        return self._frame

    @frame.setter
    def frame(self, value):
        """
        This is set in rewind/forward functions
        Value clamped above 0 and below total frame count
        """
        try:
            self._frame = min(max(value, 0), self.audio.frames)
        except AttributeError:
            self._frame = self._frame

    @property
    def stopped(self) -> bool:
        return self._stopped

    @property
    def playback_end(self):
        return self._playback_end
        
    @playback_end.setter
    def playback_end(self, value):
        self._playback_end = value

    @property
    def time(self):
        """
        Returns current position in audio clip in milliseconds
        """
        return self.get_time(self.frame, self.audio.samplerate)

    def get_time(self, frames, rate):
        """
        Convert from frames to time
        """
        return round(1000 * (frames / rate))

    def load_audio_file(self, song):
        """
        Load audio segment from file.
        Supported formats: .wav, .mp3
        """
        try: 
            self.audio.close()
        except:
            pass

        if song.format == 'mp3':
            raise FormatError
        
        self.audio = sf.SoundFile(song.title)
        self._audio_file_length = self.get_time(self.audio.frames, self.audio.samplerate)

    def new_audio_stream(self):
        """
        Closes any existing audio stream and instantiate a new stream.
        """
        self.close_stream()
        
        self.stream = sd.OutputStream(
            samplerate=self.audio.samplerate,
            channels=self.audio.channels,
            blocksize=self.blocksize,
            callback=self.callback,
            finished_callback=self.finished_callback,
            dtype='float32')

        self.raw_data = self.audio.read(dtype='float32')
        self.channel_mapping = np.arange(self.audio.channels)

        self.stream.start()
        self._stopped = False

    def callback(self, outdata, frames, time, status):
        """
        PortAudio callback function for callback in OutputStream
        """
        self.blocksize = min(self.audio.frames - self.frame, len(outdata))

        if not self._stopped:
            if self.volume <= 0.0:
                outdata[:self.blocksize, self.channel_mapping] = 0.0 * self.raw_data[:self.blocksize]
            else:
                outdata[:self.blocksize, self.channel_mapping] =  (self.volume / 100.0) * self.raw_data[self.frame:self.frame + self.blocksize]           
            self.frame += self.blocksize
        else:
            outdata[:self.blocksize, self.channel_mapping] = 0.0 * self.raw_data[:self.blocksize]
        
        if not self.blocksize:
            """
            Reached end of file. If self._playback_end is set to True, the next song in queue is automatically played.
            """
            self._playback_end = True
            raise sd.CallbackAbort

    def finished_callback(self):
        """
        Invoked as finished_callback method in PortAudio callback
        """
        self.frame = 0
        self.blocksize = 2048

    def start_audio(self, song):
        """
        Start new audio stream.
        """
        self.load_audio_file(song)
        self.new_audio_stream()

    def play_pause(self):
        """
        Toggle play/pause.
        The stream is not closed on pause, simply fed empty arrays.
        """
        self._stopped = not self._stopped

    def close_stream(self):
        """
        Closes current stream
        Only called after new audio file is loaded
        """
        if self.stream:
            self.stream.stop()
            self.stream.close()

    def rewind_10(self):
        """
        Rewind audio by 10 seconds
        """
        self.frame -= 10 * self.audio.samplerate

    def forward_10(self):
        """
        Forwars audio by 10 seconds
        """
        self.frame += 10 * self.audio.samplerate