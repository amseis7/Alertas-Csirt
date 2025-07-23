import zipfile
import os
import importlib.util


def obtener_version():
    ruta = os.path.join("Modules", "version.py")
    spec = importlib.util.spec_from_file_location("version", ruta)
    version_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(version_mod)
    return version_mod.__version__


def crear_version_txt(version):
    with open("version.txt", "w") as f:
        f.write(version)


def crear_zip(nombre_zip, carpetas_incluir, archivos_incluir=None):
    if archivos_incluir is None:
        archivos_incluir = []

    with zipfile.ZipFile(nombre_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for carpeta in carpetas_incluir:
            for root, _, files in os.walk(carpeta):
                for file in files:
                    filepath = os.path.join(root, file)
                    arcname = os.path.relpath(filepath)
                    zipf.write(filepath, arcname)

        for archivo in archivos_incluir:
            if os.path.exists(archivo):
                zipf.write(archivo)

    print(f"✅ Archivo '{nombre_zip}' creado correctamente.")


if __name__ == "__main__":
    version = obtener_version()
    crear_version_txt(version)

    carpetas = ["Modules"]
    archivos = ["main.py", "setup.py"]

    nombre_zip = f"Alertas-Csirt-v{version}.zip"
    crear_zip(nombre_zip, carpetas, archivos)
