import os
from jazzed import create_app

if __name__ == '__main__':

    name = 'Jazzed'
    icon = r'jazzed\frontend\static\jazzed.ico'    
    song_list = [
            # Add list of songs here to initialize app with pre-set song queue
            # Or leave empty
        ]

    create_app(name=name, icon=icon, song_list=song_list)