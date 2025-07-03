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

                # Proteger archivos importantes
                archivos_protegidos = {"Config", "venv", "Logs", ".git", "version.txt"}
                for archivo in os.listdir():
                    if archivo in archivos_protegidos:
                        continue
                    if os.path.isdir(archivo):
                        shutil.rmtree(archivo)
                    else:
                        os.remove(archivo)

                # Copiar nuevos archivos
                origen = os.path.join("tmp_update", nombre_raiz)
                for archivo in os.listdir(origen):
                    shutil.move(os.path.join(origen, archivo), archivo)

                # Escribir nueva versión
                with open("version.txt", "w") as f:
                    f.write(latest_version)

                shutil.rmtree("tmp_update")
                messagebox.showinfo("Actualización", "Aplicación actualizada correctamente.\nSe reiniciará.")
                os.execl(sys.executable, sys.executable, *sys.argv)
            except Exception as e:
                messagebox.showerror("Error de actualización", f"No se pudo actualizar:\n{e}")
        root.destroy()

if __name__ == '__main__':
    check_and_update()