from Modules.GUI import MiApp
import tkinter as tk
import base64
from Modules.icon import img
import os

tmp = open("tmp.ico", "wb")
tmp.write(base64.b64decode(img))
tmp.close()

def main():
    # Crear la ventana principal
    ventana_principal = tk.Tk()
    ventana_principal.title("Servicio Gestion IoC Csirt")
    ventana_principal.iconbitmap('tmp.ico')

    # Crear una instancia de la clase FirewallBlockerApp para la primera página
    app1 = MiApp(ventana_principal)
    ventana_principal.protocol("WM_DELETE_WINDOW", app1.on_closing)

    # Iniciar el ciclo de eventos
    ventana_principal.mainloop()

    # Eliminacion de archivo ico
    os.remove("tmp.ico")


# Ejecutar la función main() al final del script
if __name__ == "__main__":
    main()