import tkinter as tk
import base64
import os

from Modules.GUI import MiApp
from Modules.icon import img

def main():
    # Crear y guardar ícono temporal
    with open("tmp.ico", "wb") as tmp:
        tmp.write(base64.b64decode(img))

    try:
        ventana_principal = tk.Tk()
        ventana_principal.title("Servicio Gestión IoC Csirt")
        ventana_principal.iconbitmap("tmp.ico")

        app1 = MiApp(ventana_principal)
        ventana_principal.protocol("WM_DELETE_WINDOW", app1.on_closing)

        ventana_principal.mainloop()

    finally:
        if os.path.exists("tmp.ico"):
            os.remove("tmp.ico")

if __name__ == "__main__":
    main()
