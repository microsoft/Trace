import shutil
import os

custom_index = 'index.html'
built_book = '_build/html'

shutil.copy2(custom_index, os.path.join(built_book, 'index.html'))
