import tkinter as tk
import tkinter.messagebox as messagebox
import base64
import os
import requests
import zipfile
import io
import shutil
import sys
import subprocess

from Modules.GUI import MiApp
from Modules.icon import img

GITHUB_OWNER = "amseis7"
GITHUB_REPO = "Alertas-Csirt"

def get_current_version():
    try:
        with open("version.txt", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return "0.0.0"  # Valor por defecto si no existe el archivo

def get_latest_version_and_url():
    url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/releases/latest"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        tag_version = data["tag_name"].lstrip("v")
        assets = data.get("assets", [])
        if not assets:
            return None, None
        download_url = assets[0]["browser_download_url"]
        return tag_version, download_url
    except requests.RequestException:
        return None, None

def check_and_update():
    current_version = get_current_version()
    latest_version, download_url = get_latest_version_and_url()

    if latest_version and latest_version != current_version:
        root = tk.Tk()
        root.withdraw()
        respuesta = messagebox.askyesno(
            "Actualización disponible",
            f"Se encontró una nueva versión {latest_version}.\n¿Deseas actualizar ahora?"
        )
        if respuesta:
            try:
                r = requests.get(download_url)
                r.raise_for_status()
                with zipfile.ZipFile(io.BytesIO(r.content)) as zip_ref:
                    nombre_raiz = zip_ref.namelist()[0].split("/")[0]
                    zip_ref.extractall("tmp_update")

                # Copiar ruta base del zip
                origen = os.path.join("tmp_update", nombre_raiz)

                # Identificar archivos y carpetas a reemplazar
                archivos_nuevos = os.listdir(origen)

                # Eliminar solo los archivos y carpetas que serán reemplazados
                for archivo in archivos_nuevos:
                    if os.path.exists(archivo):
                        if os.path.isdir(archivo):
                            shutil.rmtree(archivo)
                        else:
                            os.remove(archivo)

                # Copiar nuevos archivos
                for archivo in archivos_nuevos:
                    shutil.move(os.path.join(origen, archivo), archivo)

                # Escribir nueva versión
                with open("version.txt", "w") as f:
                    f.write(latest_version)

                shutil.rmtree("tmp_update")
                messagebox.showinfo("Actualización", "Aplicación actualizada correctamente.\nSe reiniciará.")
                subprocess.Popen([sys.executable] + sys.argv)
                sys.exit()

            except Exception as e:
                messagebox.showerror("Error de actualización", f"No se pudo actualizar:\n{e}")
        root.destroy()

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
    check_and_update()
    main()
