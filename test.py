import os
import shutil
import subprocess
import configparser
import json
from googleapiclient.discovery import build

from Modules.logger import setup_logger
from Modules.handler_funtions import authenticate_google_services, prueba_google_drive, get_file_folder_url, check_file_exists
from Modules import handler_variables_email

logger = setup_logger()

def instalar_dependencias(requirements_file):
    try:
        subprocess.check_call(["pip", "install", "-r", requirements_file])
        logger.info("Módulos instalados correctamente.")
    except subprocess.CalledProcessError as e:
        logger.exception(f"Error al instalar dependencias: {e}")
        raise


def crear_directorios(base_path):
    for folder in ["Config", "Logs", "Keys"]:
        path = os.path.join(base_path, folder)
        os.makedirs(path, exist_ok=True)
        logger.info(f"Carpeta creada o ya existente: {folder}")


def mover_credenciales(config, base_path):
    if not config.has_option('credentials', 'path_key'):
        raise KeyError("Falta la clave 'path_key' en la configuración")

    key_path = config.get('credentials', 'path_key')
    if not os.path.isfile(key_path):
        raise FileNotFoundError(f"ERROR: No se encontró el archivo '{key_path}'")

    file_name = os.path.basename(key_path)
    dest_path = os.path.join(base_path, "Keys", file_name)

    if not os.path.exists(dest_path):
        shutil.move(key_path, dest_path)
        logger.info(f"Archivo de credencial movido a: {dest_path}")
    else:
        logger.warning(f"Archivo ya existente en destino: {dest_path}")

    config.set('credentials', 'path_key', dest_path)
    return dest_path


def guardar_config(config, ruta_config):
    with open(ruta_config, 'w') as configfile:
        config.write(configfile)
    logger.info(f"Configuración guardada en: {ruta_config}")


def prueba_google_sheet(sheet_name, dict_csirt_name, creds, config):
    service_sheet = build('sheets', 'v4', credentials=creds)
    service_drive = build('drive', 'v3', credentials=creds)

    sheet_id = check_file_exists(service_drive, sheet_name, 'application/vnd.google-apps.spreadsheet')
    spreadsheet_body = {
        'properties': {'title': sheet_name},
        'sheets': [{'properties': {'title': name}} for name in dict_csirt_name.keys()]
    }

    if not sheet_id:
        spreadsheet = service_sheet.spreadsheets().create(body=spreadsheet_body).execute()
        sheet_id = spreadsheet['spreadsheetId']
        for sheet in spreadsheet['sheets']:
            title = sheet['properties']['title']
            values = dict_csirt_name[title]
            requests = handler_variables_email.format_sheets_csirt(sheet['properties']['sheetId'], values)
            service_sheet.spreadsheets().batchUpdate(spreadsheetId=sheet_id, body={'requests': requests}).execute()
        logger.info("Hoja de cálculo creada y configurada.")
    else:
        logger.info("Hoja de cálculo ya existe.")

    file = service_drive.files().get(fileId=sheet_id, fields="parents").execute()
    previous_parents = ",".join(file.get("parents"))
    service_drive.files().update(
        fileId=sheet_id,
        addParents=config.get('configurations', 'folder_id'),
        removeParents=previous_parents,
        fields="id, parents"
    ).execute()
    service_drive.permissions().create(
        fileId=sheet_id,
        body={'role': 'reader', 'type': 'anyone', 'allowFileDiscovery': False}
    ).execute()

    url = get_file_folder_url(service_drive, sheet_id)
    logger.info(f"Hoja de cálculo disponible en: {url}")


def main_setup():
    try:
        base_path = os.getcwd()
        crear_directorios(base_path)

        config = configparser.ConfigParser()
        config.read("Config/configuration.cfg")

        key_path = mover_credenciales(config, base_path)
        guardar_config(config, "Config/configuration.cfg")

        creds = authenticate_google_services(key_path)
        prueba_google_sheet("HojaAlertasCSIRT", handler_variables_email.dict_csirt_name, creds, config)

    except Exception as e:
        logger.exception("Error durante la configuración inicial: %s", e)


if __name__ == "__main__":
    main_setup()
