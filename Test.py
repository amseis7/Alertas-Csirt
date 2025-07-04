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

archivo_nuevo = os.listdir("tmp_update")
files_project = os.listdir()

for archivo in archivo_nuevo:
    if archivo in files_project:
        src = os.path.join(os.getcwd(), "tmp_update", archivo)
        dst = os.path.join(os.getcwd(), archivo)

        if os.path.exists(archivo):
            if os.path.isdir(archivo):
                shutil.rmtree(archivo)
            else:
                os.remove(archivo)
            shutil.move(src, dst)



