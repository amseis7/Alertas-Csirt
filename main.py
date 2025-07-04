import tkinter as tk
import tkinter.messagebox as messagebox
import base64
import os
import datetime
import requests
import zipfile
import io
import shutil
import sys
import subprocess

from Modules.GUI import MiApp
from Modules.icon import img
from Modules.logger import setup_logger
from dotenv import load_dotenv

load_dotenv()
GITHUB_OWNER = os.getenv("GITHUB_OWNER", "default_owner")
GITHUB_REPO = os.getenv("GITHUB_REPO", "default_repo")
UPDATE_TIMEOUT = int(os.getenv("UPDATE_TIMEOUT", "10"))

# Inicializar logger
logger = setup_logger(log_file="Logs/update.log")

def get_current_version():
    try:
        with open("version.txt", "r") as f:
            version = f.read().strip()
            logger.info(f"Version actual: {version}")
            return version
    except FileNotFoundError:
        logger.warning("Archivo version.txt no encontrado. Usando versión por defecto")
        return "0.0.0"  # Valor por defecto si no existe el archivo


def get_latest_version_and_url():
    url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/releases/latest"
    try:
        response = requests.get(url, timeout=UPDATE_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        tag_version = data["tag_name"].lstrip("v")
        assets = data.get("assets", [])
        if not assets:
            return None, None
        download_url = assets[0]["browser_download_url"]
        return tag_version, download_url
    except requests.RequestException:
        logger.error(f"Error al obtener informacion de actualización: {e}")
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
            backup_dir = None
            try:
                r = requests.get(download_url)
                r.raise_for_status()
                with zipfile.ZipFile(io.BytesIO(r.content)) as zip_ref:
                    zip_ref.extractall("tmp_update")

                # Copiar ruta base del zip
                nuevos_archivos = os.listdir("tmp_update")

                # Crear carpeta de respaldo
                fecha = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_dir = f"backup_{fecha}"
                os.makedirs(backup_dir, exist_ok=True)

                for archivo in nuevos_archivos:
                    src = os.path.join("tmp_update", archivo)
                    dst = os.path.join(os.getcwd(), archivo)

                    # Si el archivo ya existe, hacer respaldo
                    if os.path.exists(dst):
                        backup_path = os.path.join(backup_dir, archivo)
                        if os.path.isdir(dst):
                            shutil.copytree(dst, backup_path, dirs_exist_ok=True)
                            shutil.rmtree(dst)
                        else:
                            shutil.copy2(dst, backup_path)
                            os.remove(dst)

                    # Mover desde tmp_update a raiz
                    shutil.move(src, dst)

                # Escribir nueva versión
                with open("version.txt", "w") as f:
                    f.write(latest_version)

                messagebox.showinfo("Actualización", "Aplicación actualizada correctamente.\nSe reiniciará.")
                logger.info(f"Actualización completada a versión {latest_version}")
                shutil.rmtree("tmp_update", ignore_errors=True)
                subprocess.Popen([sys.executable] + sys.argv)
                sys.exit()

            except Exception as e:
                logger.exception(f"Error durante el proceso de actualización: {e}")
                # Restaurar desde backup si existe
                if backup_dir and os.path.exists(backup_dir):
                    for item in os.listdir(backup_dir):
                        bkp_path = os.path.join(backup_dir, item)
                        dst_path = os.path.join(os.getcwd(), item)

                        if os.path.exists(dst_path):
                            if os.path.isdir(dst_path):
                                shutil.rmtree(dst_path)
                            else:
                                os.remove(dst_path)

                        if os.path.isdir(bkp_path):
                            shutil.copytree(bkp_path, dst_path, dirs_exist_ok=True)
                        else:
                            shutil.copy2(bkp_path, dst_path)

                messagebox.showerror("Error de actualización", f"No se pudo actualizar:\n{e}")

            finally:
                shutil.rmtree("tmp_update", ignore_errors=True)
                if backup_dir and os.path.exists(backup_dir):
                    shutil.rmtree(backup_dir, ignore_errors=True)

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
