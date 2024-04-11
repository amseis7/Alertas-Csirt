import subprocess
import configparser
import shutil
import json
import os

archivo_requirements = "requeriment.txt"
root_path = os.path.dirname(os.path.abspath(__file__))
config = configparser.ConfigParser()


def instalar_modulos_desde_requirements(requerimientos_txt):
    if not os.path.isfile(requerimientos_txt):
        raise FileNotFoundError(f"ERROR: No fue posible encontrar el archivo '{requerimientos_txt}'")

    print("Instalando modulos necesarios......")
    # Utiliza subprocess para ejecutar el comando pip install desde el script
    subprocess.check_call(["pip", "install", "-r", requerimientos_txt])
    print(f"Los módulos en {requerimientos_txt} han sido instalados correctamente.")


def crear_configuracion(root_path, config_cfg):
    ruta_archivo_cfg = os.path.join(root_path, 'Config', "configuration.cfg")
    try:
        if not os.path.isfile(ruta_archivo_cfg):
            while True:
                credentials_name = os.path.join(root_path, input(
                    "Ingresar nombre del archivo json descargada de Google: ").strip())
                domain = input("Ingresar dominio permitido de recepción de correo (ej. @gmail.com): ").strip()
                time_wait_str = input("Ingrese el tiempo de cada búsqueda de correos (En segundos): ").strip()
                folder_name = input("Ingresar el nombre de la carpeta compartida a crear en Google Drive: ").strip()
                sheet_name = input("Ingrese el nombre de la Hoja de calculo a crear en Google Drive: ").strip()

                if credentials_name and domain and time_wait_str and folder_name and sheet_name:
                    try:
                        time_wait = int(time_wait_str)
                        if time_wait > 0:
                            break
                        else:
                            print("El tiempo de espera debe ser un número entero positivo.")
                    except ValueError:
                        print("Ingrese un valor numérico válido para el tiempo de espera.")
                else:
                    print("Todos los campos son obligatorios. Por favor, ingrese la información solicitada.")

            config_cfg['credentials'] = {'path_key': credentials_name}
            config_cfg['configurations'] = {'domain': domain, 'time_wait': time_wait, 'folder_name': folder_name,
                                            'sheet_name': sheet_name, 'folder_id': "", 'sheet_id': ""}

            with open(ruta_archivo_cfg, "w") as configfile:
                config_cfg.write(configfile)

            print(f"Archivo '{ruta_archivo_cfg}' creado correctamente.")

            return ruta_archivo_cfg
        else:
            print(f"El archivo '{ruta_archivo_cfg}' ya existe.")
            return ruta_archivo_cfg

    except Exception as e:
        print(f"Error al crear el archivo .cfg: {e}")


def crear_carpeta(root_path, fold):
    # Ruta de la carpeta a crear
    path_folder = os.path.join(root_path, fold)
    if os.path.exists(path_folder):
        print(f"Carpeta {fold} ya existe...")
    else:
        print(f"Se crea carpeta {fold}...")
        os.makedirs(path_folder, exist_ok=True)


def check_file_exists(service, file_name, type_file):
    results = service.files().list(q=f"name='{folder_name}' and mimeType='{type_file}' and trashed=false").execute()
    files = results.get('files', [])
    if files:
        return files[0]['id']
    else:
        return False


def get_file_folder_url(service, file_id):
    # Obtiene la información del archivo
    file_info = service.files().get(fileId=file_id, fields='webViewLink').execute()

    # Obtiene y retorna la URL de visualización del archivo
    return file_info.get('webViewLink', None)


def prueba_google_drive(folder_name, creds):
    folder_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder'
    }

    # Agregar permisos para compartir la carpeta
    share_permission = {
        'type': 'anyone',
        'role': 'writer'
    }

    drive_service = build('drive', 'v3', credentials=creds)
    folder_id = check_file_exists(drive_service, folder_name, 'application/vnd.google-apps.folder')

    if not folder_id:
        folder = drive_service.files().create(body=folder_metadata, fields='id').execute()
        folder_id = folder['id']
        print(f"Prueba de acceso y creacion de carpeta compartida {folder_name} exitosa...")
    else:
        print(f"Prueba de acceso exitosa, carpeta compartida {folder_name} ya existe")

    drive_service.permissions().create(fileId=folder_id, body=share_permission).execute()
    url_folder = get_file_folder_url(drive_service, folder_id)
    data_config = {'url_folder': url_folder, 'folder_id': folder_id}
    return data_config


def format_sheets_csirt(sheet_id, values):
    merge_and_format_requests = [
        {
            'mergeCells': {
                'mergeType': 'MERGE_ROWS',
                'range': {
                    'sheetId': sheet_id,
                    'startRowIndex': 0,
                    'endRowIndex': 1,
                    'startColumnIndex': 0,
                    'endColumnIndex': 6
                }
            }
        },
        {
            'updateCells': {
                'rows': [
                    {
                        'values': [
                            {
                                'userEnteredFormat': {
                                    'backgroundColor': {'red': 1, 'green': 0, 'blue': 0},  # fondo rojo
                                    'textFormat': {'foregroundColor': {'red': 1, 'green': 1, 'blue': 1},
                                                   'fontFamily': 'Calibri', 'fontSize': 20, 'bold': True},
                                    # letras blancas, tamaño 20, negrita
                                    'horizontalAlignment': 'CENTER',  # centrar texto
                                    'borders': {
                                        'bottom': {'style': 'SOLID', 'width': 2,
                                                   'color': {'red': 0, 'green': 0, 'blue': 0}},
                                        'top': {'style': 'SOLID', 'width': 2,
                                                'color': {'red': 0, 'green': 0, 'blue': 0}},
                                        'left': {'style': 'SOLID', 'width': 2,
                                                 'color': {'red': 0, 'green': 0, 'blue': 0}},
                                        'right': {'style': 'SOLID', 'width': 2,
                                                  'color': {'red': 0, 'green': 0, 'blue': 0}}
                                    }
                                },
                                'userEnteredValue': {'stringValue': 'Alertas CSIRT'}
                            }
                        ]
                    }
                ],
                'fields': '*',
                'start': {'sheetId': sheet_id, 'rowIndex': 0, 'columnIndex': 0}
            }
        },
        # Combinar y establecer formato para la segunda fila
        {
            'mergeCells': {
                'mergeType': 'MERGE_ROWS',
                'range': {
                    'sheetId': sheet_id,
                    'startRowIndex': 1,
                    'endRowIndex': 2,
                    'startColumnIndex': 0,
                    'endColumnIndex': 6
                }
            }
        },
        {
            'updateCells': {
                'rows': [
                    {
                        'values': [
                            {
                                'userEnteredFormat': {
                                    'backgroundColor': {'red': 1, 'green': 1, 'blue': 0},  # fondo amarillo
                                    'textFormat': {'foregroundColor': {'red': 0, 'green': 0, 'blue': 0},
                                                   'fontFamily': 'Calibri', 'fontSize': 16, 'bold': True},
                                    # letras negras, tamaño 20, negrita
                                    'horizontalAlignment': 'CENTER',  # centrar texto
                                    'borders': {
                                        'bottom': {'style': 'SOLID', 'width': 1,
                                                   'color': {'red': 0, 'green': 0, 'blue': 0}},
                                        'top': {'style': 'SOLID', 'width': 1,
                                                'color': {'red': 0, 'green': 0, 'blue': 0}},
                                        'left': {'style': 'SOLID', 'width': 1,
                                                 'color': {'red': 0, 'green': 0, 'blue': 0}},
                                        'right': {'style': 'SOLID', 'width': 1,
                                                  'color': {'red': 0, 'green': 0, 'blue': 0}}
                                    }
                                },
                                'userEnteredValue': {'stringValue': values}
                            }
                        ]
                    }
                ],
                'fields': '*',
                'start': {'sheetId': sheet_id, 'rowIndex': 1, 'columnIndex': 0}
            }
        },
        # Establecer formato para la tercera fila
        {
            'updateCells': {
                'rows': [
                    {
                        'values': [
                            # Valor para la primera celda
                            {
                                'userEnteredFormat': {
                                    'backgroundColor': {'red': 0.7176, 'green': 0.8824, 'blue': 0.8039},
                                    # fondo verde claro
                                    'textFormat': {'foregroundColor': {'red': 0, 'green': 0, 'blue': 0},
                                                   'fontFamily': 'Calibri', 'fontSize': 11, 'bold': True},
                                    # letras negras, tamaño 8, negrita
                                    'horizontalAlignment': 'CENTER',
                                    'borders': {
                                        'bottom': {'style': 'SOLID', 'width': 1,
                                                   'color': {'red': 0, 'green': 0, 'blue': 0}},
                                        'top': {'style': 'SOLID', 'width': 1,
                                                'color': {'red': 0, 'green': 0, 'blue': 0}},
                                        'left': {'style': 'SOLID', 'width': 1,
                                                 'color': {'red': 0, 'green': 0, 'blue': 0}},
                                        'right': {'style': 'SOLID', 'width': 1,
                                                  'color': {'red': 0, 'green': 0, 'blue': 0}}
                                    }
                                },
                                'userEnteredValue': {'stringValue': 'Alerta'}
                            },
                            # Valor para la segunda celda
                            {
                                'userEnteredFormat': {
                                    'backgroundColor': {'red': 0.7176, 'green': 0.8824, 'blue': 0.8039},
                                    # fondo verde claro
                                    'textFormat': {'foregroundColor': {'red': 0, 'green': 0, 'blue': 0},
                                                   'fontFamily': 'Calibri', 'fontSize': 11, 'bold': True},
                                    # letras negras, tamaño 8, negrita
                                    'horizontalAlignment': 'CENTER',
                                    'borders': {
                                        'bottom': {'style': 'SOLID', 'width': 1,
                                                   'color': {'red': 0, 'green': 0, 'blue': 0}},
                                        'top': {'style': 'SOLID', 'width': 1,
                                                'color': {'red': 0, 'green': 0, 'blue': 0}},
                                        'left': {'style': 'SOLID', 'width': 1,
                                                 'color': {'red': 0, 'green': 0, 'blue': 0}},
                                        'right': {'style': 'SOLID', 'width': 1,
                                                  'color': {'red': 0, 'green': 0, 'blue': 0}}
                                    }
                                },
                                'userEnteredValue': {'stringValue': 'Revision'}
                            },
                            {
                                'userEnteredFormat': {
                                    'backgroundColor': {'red': 0.7176, 'green': 0.8824, 'blue': 0.8039},
                                    # fondo verde claro
                                    'textFormat': {'foregroundColor': {'red': 0, 'green': 0, 'blue': 0},
                                                   'fontFamily': 'Calibri', 'fontSize': 11, 'bold': True},
                                    # letras negras, tamaño 8, negrita
                                    'horizontalAlignment': 'CENTER',
                                    'borders': {
                                        'bottom': {'style': 'SOLID', 'width': 1,
                                                   'color': {'red': 0, 'green': 0, 'blue': 0}},
                                        'top': {'style': 'SOLID', 'width': 1,
                                                'color': {'red': 0, 'green': 0, 'blue': 0}},
                                        'left': {'style': 'SOLID', 'width': 1,
                                                 'color': {'red': 0, 'green': 0, 'blue': 0}},
                                        'right': {'style': 'SOLID', 'width': 1,
                                                  'color': {'red': 0, 'green': 0, 'blue': 0}}
                                    }
                                },
                                'userEnteredValue': {'stringValue': 'Responsable'}
                            },
                            {
                                'userEnteredFormat': {
                                    'backgroundColor': {'red': 0.7176, 'green': 0.8824, 'blue': 0.8039},
                                    # fondo verde claro
                                    'textFormat': {'foregroundColor': {'red': 0, 'green': 0, 'blue': 0},
                                                   'fontFamily': 'Calibri', 'fontSize': 11, 'bold': True},
                                    # letras negras, tamaño 8, negrita
                                    'horizontalAlignment': 'CENTER',
                                    'borders': {
                                        'bottom': {'style': 'SOLID', 'width': 1,
                                                   'color': {'red': 0, 'green': 0, 'blue': 0}},
                                        'top': {'style': 'SOLID', 'width': 1,
                                                'color': {'red': 0, 'green': 0, 'blue': 0}},
                                        'left': {'style': 'SOLID', 'width': 1,
                                                 'color': {'red': 0, 'green': 0, 'blue': 0}},
                                        'right': {'style': 'SOLID', 'width': 1,
                                                  'color': {'red': 0, 'green': 0, 'blue': 0}}
                                    }
                                },
                                'userEnteredValue': {'stringValue': 'Fecha de realizacion'}
                            },
                            {
                                'userEnteredFormat': {
                                    'backgroundColor': {'red': 0.7176, 'green': 0.8824, 'blue': 0.8039},
                                    # fondo verde claro
                                    'textFormat': {'foregroundColor': {'red': 0, 'green': 0, 'blue': 0},
                                                   'fontFamily': 'Calibri', 'fontSize': 11, 'bold': True},
                                    # letras negras, tamaño 8, negrita
                                    'horizontalAlignment': 'CENTER',
                                    'borders': {
                                        'bottom': {'style': 'SOLID', 'width': 1,
                                                   'color': {'red': 0, 'green': 0, 'blue': 0}},
                                        'top': {'style': 'SOLID', 'width': 1,
                                                'color': {'red': 0, 'green': 0, 'blue': 0}},
                                        'left': {'style': 'SOLID', 'width': 1,
                                                 'color': {'red': 0, 'green': 0, 'blue': 0}},
                                        'right': {'style': 'SOLID', 'width': 1,
                                                  'color': {'red': 0, 'green': 0, 'blue': 0}}
                                    }
                                },
                                'userEnteredValue': {'stringValue': 'Tickets'}
                            },
                            {
                                'userEnteredFormat': {
                                    'backgroundColor': {'red': 0.7176, 'green': 0.8824, 'blue': 0.8039},
                                    # fondo verde claro
                                    'textFormat': {'foregroundColor': {'red': 0, 'green': 0, 'blue': 0},
                                                   'fontFamily': 'Calibri', 'fontSize': 11, 'bold': True},
                                    # letras negras, tamaño 8, negrita
                                    'horizontalAlignment': 'CENTER',
                                    'borders': {
                                        'bottom': {'style': 'SOLID', 'width': 1,
                                                   'color': {'red': 0, 'green': 0, 'blue': 0}},
                                        'top': {'style': 'SOLID', 'width': 1,
                                                'color': {'red': 0, 'green': 0, 'blue': 0}},
                                        'left': {'style': 'SOLID', 'width': 1,
                                                 'color': {'red': 0, 'green': 0, 'blue': 0}},
                                        'right': {'style': 'SOLID', 'width': 1,
                                                  'color': {'red': 0, 'green': 0, 'blue': 0}}
                                    }
                                },
                                'userEnteredValue': {'stringValue': 'Gestionado'}
                            },
                            # ... Repite para las celdas restantes
                        ]
                    }
                ],
                'fields': '*',
                'start': {'sheetId': sheet_id, 'rowIndex': 2, 'columnIndex': 0}
            }
        },
        # Ancho de la primera columna
        {
            'updateDimensionProperties': {
                'range': {
                    'sheetId': sheet_id,
                    'dimension': 'COLUMNS',  # Indicar que es una columna
                    'startIndex': 0,  # Índice de la columna a modificar
                    'endIndex': 1  # Índice de la columna a modificar
                },
                'properties': {
                    'pixelSize': 120  # Nuevo ancho de la columna en píxeles
                },
                'fields': 'pixelSize'  # Especificar que se actualice solo el tamaño en píxeles
            }
        },
        # Ancho de la segunda columna
        {
            'updateDimensionProperties': {
                'range': {
                    'sheetId': sheet_id,
                    'dimension': 'COLUMNS',  # Indicar que es una columna
                    'startIndex': 1,  # Índice de la columna a modificar
                    'endIndex': 2  # Índice de la columna a modificar
                },
                'properties': {
                    'pixelSize': 60  # Nuevo ancho de la columna en píxeles
                },
                'fields': 'pixelSize'  # Especificar que se actualice solo el tamaño en píxeles
            }
        },
        # Ancho de la tercera columna
        {
            'updateDimensionProperties': {
                'range': {
                    'sheetId': sheet_id,
                    'dimension': 'COLUMNS',  # Indicar que es una columna
                    'startIndex': 2,  # Índice de la columna a modificar
                    'endIndex': 3  # Índice de la columna a modificar
                },
                'properties': {
                    'pixelSize': 230  # Nuevo ancho de la columna en píxeles
                },
                'fields': 'pixelSize'  # Especificar que se actualice solo el tamaño en píxeles
            }
        },
        # Ancho de la cuarta columna
        {
            'updateDimensionProperties': {
                'range': {
                    'sheetId': sheet_id,
                    'dimension': 'COLUMNS',  # Indicar que es una columna
                    'startIndex': 3,  # Índice de la columna a modificar
                    'endIndex': 4  # Índice de la columna a modificar
                },
                'properties': {
                    'pixelSize': 130  # Nuevo ancho de la columna en píxeles
                },
                'fields': 'pixelSize'  # Especificar que se actualice solo el tamaño en píxeles
            }
        },
        # Ancho de la quinta segunda columna
        {
            'updateDimensionProperties': {
                'range': {
                    'sheetId': sheet_id,
                    'dimension': 'COLUMNS',  # Indicar que es una columna
                    'startIndex': 4,  # Índice de la columna a modificar
                    'endIndex': 5  # Índice de la columna a modificar
                },
                'properties': {
                    'pixelSize': 85  # Nuevo ancho de la columna en píxeles
                },
                'fields': 'pixelSize'  # Especificar que se actualice solo el tamaño en píxeles
            }
        },
        # Ancho de la sexta columna
        {
            'updateDimensionProperties': {
                'range': {
                    'sheetId': sheet_id,
                    'dimension': 'COLUMNS',  # Indicar que es una columna
                    'startIndex': 5,  # Índice de la columna a modificar
                    'endIndex': 6  # Índice de la columna a modificar
                },
                'properties': {
                    'pixelSize': 80  # Nuevo ancho de la columna en píxeles
                },
                'fields': 'pixelSize'  # Especificar que se actualice solo el tamaño en píxeles
            }
        }
    ]

    return merge_and_format_requests


def prueba_google_sheet(sheet_name, creds):
    spreadsheet_body = {
        'properties': {'title': sheet_name},
        'sheets': [
            {'properties': {'title': '8FPH'}},
            {'properties': {'title': '2CMV'}},
            {'properties': {'title': '8FFR'}},
            {'properties': {'title': '4IIA'}},
            {'properties': {'title': '4IIV'}},
        ]
    }

    permission_body = {
        'role': 'reader',
        'type': 'anyone',
        'allowFileDiscovery': False
    }

    service_sheet = build('sheets', 'v4', credentials=creds)
    service_drive = build('drive', 'v3', credentials=creds)
    sheet_id = check_file_exists(service_drive, sheet_name, 'application/vnd.google-apps.spreadsheet')

    if not sheet_id:
        spreadsheet = service_sheet.spreadsheets().create(body=spreadsheet_body).execute()
        sheet_id = spreadsheet['spreadsheetId']
        for sheets in spreadsheet['sheets']:
            if sheets['properties'].get('title') == '8FPH':
                values = 'Phishing'
            elif sheets['properties'].get('title') == '2CMV':
                values = 'Malware'
            elif sheets['properties'].get('title') == '8FFR':
                values = 'Sitios Fraudulentos'
            elif sheets['properties'].get('title') == '4IIA' or sheets['properties'].get('title') == '4IIV':
                values = 'Ataques de Fuerza Bruta'
            merge_and_format_requests = format_sheets_csirt(sheets['properties'].get('sheetId'), values)
            response = service_sheet.spreadsheets().batchUpdate(spreadsheetId=sheet_id,
                                                                body={'requests': merge_and_format_requests}).execute()
        print(
            "Pruebas de acceso a Sheet Google API y creacion de planilla con alertas CSIRT realizadas exitosamente...")
    else:
        print("Pruebas de acceso a Sheet Google API exitosa, planilla con alertas CSIRT ya existe...")

    file = service_drive.files().get(fileId=sheet_id, fields="parents").execute()
    previous_parents = ",".join(file.get("parents"))
    file = service_drive.files().update(fileId=sheet_id, addParents=config.get('configurations', 'folder_id'),
                                        removeParents=previous_parents, fields="id, parents").execute()
    service_drive.permissions().create(fileId=sheet_id, body=permission_body).execute()
    url_sheet = get_file_folder_url(service_drive, sheet_id)
    data_sheet = {'sheet_id': sheet_id, 'sheet_url': url_sheet}
    return data_sheet


# Menu
print("#" * 55)
print("#   Preparación de Servicio Gestión CSIRT en Python   #")
print("#" * 55)

# Instalacion de modulos necesarios para el programa
instalar_modulos_desde_requirements(archivo_requirements)

# Crear carpeta Config, Logs y archivo de configuracion
print("Creando carpeta Config y Logs...")
crear_carpeta(root_path, 'Config')
crear_carpeta(root_path, 'Logs')
crear_carpeta(root_path, 'Keys')
print("Creando archivo de configuracion...")
ruta_config = crear_configuracion(root_path, config)

# Importar librerias necesaria para Google API
try:
    from Modules.handler_funtions import authentication_gmail
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError

    # Variables
    config.read(ruta_config)
    key_path = config.get('credentials', 'path_key')
    folder_name = config.get('configurations', 'folder_name')
    sheet_name = config.get('configurations', 'sheet_name')

    # Pruebas de archivo de configuracion creadas y archivo .json con credenciales de acceso a los servicios y APIs de Google
    print("Realizando pruebas de credenciales.......")
    if not os.path.isfile(key_path):
        raise FileNotFoundError(
            f"ERROR: No se ha encontrado el archivo '{key_path}'\nRevisar si en el archivo '{os.path.join(root_path, ruta_config)}' en el valor path_key tenga la ruta y nombre correcto del archivo JSON de Google.")

    else:
        original_key_path = key_path
        file_key = key_path.split('\\')
        shutil.move(key_path, f"{root_path}\\Keys\\{file_key[-1]}")
        config.set('credentials', 'path_key',f"{root_path}\\Keys\\{file_key[-1]}")
        with open(ruta_config, 'w') as configfile:
            config.write(configfile)

    key_path = config.get('credentials', 'path_key')
    print(key_path)
    creds = authentication_gmail(key_file=key_path)

    # Prueba de permisos Gmail
    print("Probando accesos a API GMAIL...")
    gmail_service = build('gmail', 'v1', credentials=creds)
    if gmail_service.users().messages().list(userId='me').execute():
        print("Prueba de acceso a GMAIL exitoso.")

    # Prueba de permisos Google Drive y creacion de carpeta compartida
    print("Probando acceso a API Google Drive y creando carpeta compartida...")
    data_drive = prueba_google_drive(folder_name, creds)
    config.set('configurations','folder_id', data_drive['folder_id'])
    # config['configurations']['folder_id'] = data_drive['folder_id']
    config.set('configurations', 'url_folder', data_drive['url_folder'])
    # config['configurations']['url_folder'] = data_drive['url_folder']
    with open(ruta_config, 'w') as configfile:
        config.write(configfile)

    # Prueba de permisos Google Sheet y creacion de planilla compartida
    print("Probando acceso a Sheet Google API y creacion de planilla con alertas CSIRT")
    data_sheet = prueba_google_sheet(sheet_name, creds)
    config.set('configurations', 'sheet_id', data_sheet['sheet_id'])
    # config['configurations']['sheet_id'] = data_sheet['sheet_id']
    config.set('configurations', 'sheet_url', data_sheet['sheet_url'])
    # config['configurations']['sheet_url'] = data_sheet['sheet_url']
    with open(ruta_config, 'w') as configfile:
        config.write(configfile)

    print("Instalacion y preparación terminadas.")

except FileNotFoundError as e:
    print(e)
    ruta_archivo_cfg = os.path.join(root_path, 'Config')
    ruta_log = os.path.join(root_path, 'Logs')
    ruta_key = os.path.join(root_path, 'Keys')
    shutil.rmtree(ruta_archivo_cfg)
    shutil.rmtree(ruta_log)
    shutil.rmtree(ruta_key)

except subprocess.CalledProcessError as e:
    print(f"Error al instalar los módulos desde {archivo_requirements}: {e}")

except HttpError as e:
    error_data = json.loads(e.content)
    error_message = error_data['error']['message']
    print(f"API NO HABILITADA!: {error_message}")
    config = configparser.ConfigParser()
    config.read(os.path.join(root_path, 'Config', 'configuration.cfg'))
    path_key = config.get('credentials', 'path_key')
    credentials = authentication_gmail(key_file=path_key)
    drive_service = build('drive', 'v3', credentials=credentials)
    if config.get('configurations', 'sheet_id'):
        drive_service.files().delete(fileId=config.get('configurations', 'sheet_id')).execute()
    if config.get('configurations', 'folder_id'):
        drive_service.files().delete(fileId=config.get('configurations', 'folder_id')).execute()
    shutil.move(f"{root_path}\\Keys\\{file_key[-1]}", original_key_path)
    ruta_archivo_cfg = os.path.join(root_path, 'Config')
    ruta_log = os.path.join(root_path, 'Logs')
    ruta_key = os.path.join(root_path, 'Keys')
    shutil.rmtree(ruta_archivo_cfg)
    shutil.rmtree(ruta_log)
    shutil.rmtree(ruta_key)