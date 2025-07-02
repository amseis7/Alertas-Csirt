import os
import shutil
import subprocess
import configparser
import json
from googleapiclient.discovery import build

from Modules.handler_funtions import authentication_gmail
from Modules import handler_variables_email
from Modules.handler_funtions import prueba_google_drive, get_file_folder_url, check_file_exists


def instalar_dependencias(requirements_file):
    try:
        subprocess.check_call(["pip", "install", "-r", requirements_file])
        print("Módulos instalados correctamente.")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Error al instalar dependencias: {e}")


def crear_directorios(base_path):
    for folder in ["Config", "Logs", "Keys"]:
        os.makedirs(os.path.join(base_path, folder), exist_ok=True)
        print(f"Carpeta creada o ya existente: {folder}")


def mover_credenciales(config, base_path):
    key_path = config.get('credentials', 'path_key')
    if not os.path.isfile(key_path):
        raise FileNotFoundError(f"ERROR: No se encontró el archivo '{key_path}'")

    file_name = os.path.basename(key_path)
    dest_path = os.path.join(base_path, "Keys", file_name)
    shutil.move(key_path, dest_path)
    config.set('credentials', 'path_key', dest_path)
    return dest_path


def guardar_config(config, ruta_config):
    with open(ruta_config, 'w') as configfile:
        config.write(configfile)


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
        print("Hoja creada y configurada.")
    else:
        print("Hoja ya existe.")

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
    return {'sheet_id': sheet_id, 'sheet_url': url}


def main():
    print("#" * 55)
    print("#   Preparación de Servicio Gestión CSIRT en Python   #")
    print("#" * 55)

    root_path = os.getcwd()
    requirements_path = os.path.join(root_path, "requeriment.txt")
    config = configparser.ConfigParser()

    instalar_dependencias(requirements_path)
    crear_directorios(root_path)

    print("Creando archivo de configuración...")
    from Modules.handler_funtions import crear_configuracion
    config_path = crear_configuracion(root_path, config)

    config.read(config_path)

    try:
        key_path = mover_credenciales(config, root_path)
        guardar_config(config, config_path)

        creds = authentication_gmail(key_file=key_path)

        print("Verificando acceso a Gmail...")
        if build('gmail', 'v1', credentials=creds).users().messages().list(userId='me').execute():
            print("Acceso exitoso a Gmail.")

        print("Creando carpeta en Google Drive...")
        folder_name = config.get('configurations', 'folder_name')
        drive_data = prueba_google_drive(folder_name, creds)
        config.set('configurations', 'folder_id', drive_data['folder_id'])
        config.set('configurations', 'url_folder', drive_data['url_folder'])
        guardar_config(config, config_path)

        print("Creando y probando hoja en Google Sheets...")
        sheet_name = config.get('configurations', 'sheet_name')
        csirt_names = json.loads(config.get('configurations', 'csirt_names'))
        sheet_data = prueba_google_sheet(sheet_name, csirt_names, creds, config)
        config.set('configurations', 'sheet_id', sheet_data['sheet_id'])
        config.set('configurations', 'sheet_url', sheet_data['sheet_url'])
        guardar_config(config, config_path)

        print("✅ Instalación y configuración completadas.")

    except Exception as e:
        print(f"❌ Error: {e}")
        for folder in ['Config', 'Logs', 'Keys']:
            folder_path = os.path.join(root_path, folder)
            if os.path.exists(folder_path):
                shutil.rmtree(folder_path)


if __name__ == "__main__":
    main()
