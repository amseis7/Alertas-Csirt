import tkinter as tk
import tkinter.messagebox as messagebox
import base64
import os
import requests
import zipfile
import io
import shutil
import sys
import webbrowser

origen = os.path.join("tmp_update", "Modules")
update_files = os.listdir("tmp_update")
files_project = os.listdir()

path_replacement_files = []

for i in update_files:
    if i in files_project:
        src = os.path.join(os.getcwd(), "tmp_update", i)
        dst = os.path.join(os.getcwd(), i)

        if os.path.exists(i):
            if os.path.isdir(i):
                shutil.rmtree(i)
            else:
                os.remove(i)
            shutil.move(src, dst)



