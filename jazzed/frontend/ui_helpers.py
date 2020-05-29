from tkinter import *
from tkinter import ttk
import itertools as it

class ToggleImageButton(ttk.Button):

    def __init__(self, master, image_up, image_down, **kwargs):
        super().__init__(master=master, image=image_up, **kwargs)
        self.images = it.cycle([image_down, image_up])
        self.bind("<Button-1>", self.toggle)

    def toggle(self, *args):
        """
        Toggle between button images
        """
        self.configure(image=next(self.images))