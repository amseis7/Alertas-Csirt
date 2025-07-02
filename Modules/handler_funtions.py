from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from email.mime.multipart import MIMEMultipart
from googleapiclient.discovery import build
import Modules.handler_variables_email
from email.mime.text import MIMEText
from datetime import datetime
import google.auth.exceptions
from bs4 import BeautifulSoup
import pandas as pd
import requests
import logging
import base64
import locale
import time
import json
import copy
import re
import os


REG_SUBJECT = r'\[(.*)\]\s((ioc|reporte)\scsirt)$'
reg_ip = r"(((25[0-5]|2[0-4]\d|[01]?\d\d?)\[?\.]?){3}(25[0-5]|2[0-4]\d|[01]?\d\d?))"
reg_url = r"((hxxps|hxxp|https|http)\[?\:?\]?\/\/\]?[a-zA-Z0-9]+.*)$"
reg_correo = r"(.*\@.*\[?\.\]?\w{1,4}?)$"
reg_dominio = r"([a-zA-Z0-9]+((\.|\-|\_)?)([a-zA-Z0-9]+)?\[?\.\]?\w{2,5})$"
reg_sha2 = r"([0-9a-fA-F]{64}$)"
reg_sha1 = r"(^[0-9a-fA-F]{40}$)"
reg_md5 = r"(^[0-9a-fA-F]{32}$)"
logging.basicConfig(filename='.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def authentication_gmail(token_file='Keys\\token.json', key_file=''):
        scopes = [
            'https://www.googleapis.com/auth/drive.metadata.readonly',
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive.file',
            'https://www.googleapis.com/auth/drive',
            'https://www.googleapis.com/auth/gmail.readonly',
            'https://www.googleapis.com/auth/gmail.modify'
            ]

        credentials = None

        try:
            # Intentar cargar las credenciales desde el archivo
            credentials = Credentials.from_authorized_user_file(token_file, scopes=scopes)

            # Comprobar si las credenciales han expirado
            if credentials.expired:
                # Renovar las credenciales
                credentials.refresh(Request())
                # Guardar las nuevas credenciales en el archivo
                with open(token_file, 'w') as token:
                    token.write(credentials.to_json())

        except (FileNotFoundError, ValueError, google.auth.exceptions.RefreshError):
            # Si el archivo no existe o no tiene el formato esperado, iniciar el flujo de autorización
            print("Se requiere autorización del usuario. Abriendo ventana de autorización...")
            flow = InstalledAppFlow.from_client_secrets_file(key_file, scopes)
            credentials = flow.run_local_server(port=0)
            # Guardar las credenciales en el archivo
            with open(token_file, 'w') as token:
                token.write(credentials.to_json())
            print("Autorización exitosa. Credenciales guardadas.")

        return credentials


def list_messages(creds, user_id='me', query=''):
    service = build('gmail', 'v1', credentials=creds)
    response = service.users().messages().list(userId=user_id, q=query).execute()
    messages = response.get('messages', [])
    return messages


def handler_sheets(command, sheet_id, credentials, values_csirt=None):
    service = build('sheets', 'v4', credentials=credentials)
    sheet = service.spreadsheets()
    res = sheet.get(spreadsheetId=sheet_id).execute()

    if command == "get":
        sheets_name = [x.get('properties').get('title') for x in res.get("sheets", [])]
        last_csirt = {}
        for sheet_name in sheets_name:
            len_value = -1
            data = sheet.values().get(spreadsheetId=sheet_id, range=sheet_name).execute()
            last_csirt[sheet_name] = data.get('values', [])[len_value][0]
            while last_csirt[sheet_name] == "":
                len_value -= 1
                last_csirt[sheet_name] = data.get('values', [])[len_value][0]
        return last_csirt

    elif command == "insert":
        sheet_dict = {item['properties']['title']: item['properties']['sheetId'] for item in res.get("sheets", [])}
        new_dict = copy.deepcopy(values_csirt)
        for csirt_code in new_dict:
            matriz_values = []
            for value in new_dict[csirt_code]:
                value.pop('ioc')
                matriz_values.append(list(value.values()))
            data = sheet.values().get(spreadsheetId=sheet_id, range=csirt_code).execute()
            format_requests = []
            for row_index, row in enumerate(matriz_values):
                for col_index, value in enumerate(row):
                    cell_range = {
                        'sheetId': sheet_dict.get(csirt_code),
                        'startRowIndex': len(data['values']) + row_index,
                        'endRowIndex': len(data['values']) + row_index + 1,
                        'startColumnIndex': col_index,
                        'endColumnIndex': col_index + 1
                    }

                    border_format = {
                        'border': {
                            'top': {'style': 'SOLID', 'width': 1, 'color': {'red': 0, 'green': 0, 'blue': 0}},
                            'bottom': {'style': 'SOLID', 'width': 1, 'color': {'red': 0, 'green': 0, 'blue': 0}},
                            'left': {'style': 'SOLID', 'width': 1, 'color': {'red': 0, 'green': 0, 'blue': 0}},
                            'right': {'style': 'SOLID', 'width': 1, 'color': {'red': 0, 'green': 0, 'blue': 0}}

                        }
                    }

                    format_requests.append({
                        'repeatCell': {
                            'range': cell_range,
                            'cell': {
                                'userEnteredFormat': {
                                    'textFormat': {
                                        'foregroundColor': {'red': 0, 'green': 0, 'blue': 0},
                                        'fontFamily': 'Calibri',
                                        'fontSize': 11,
                                        'bold': False
                                    },
                                    'horizontalAlignment': 'CENTER'
                                }
                            },
                            'fields': 'userEnteredFormat(textFormat,horizontalAlignment)'
                        }
                    })

                    format_requests.append({
                        'updateBorders': {
                            'range': cell_range,
                            'bottom': border_format['border']['bottom'],
                            'top': border_format['border']['top'],
                            'left': border_format['border']['left'],
                            'right': border_format['border']['right'],
                            'innerHorizontal': border_format['border']['bottom'],
                            'innerVertical': border_format['border']['right']
                        }
                    })
            result = sheet.values().append(spreadsheetId=sheet_id,
                                           range=csirt_code,
                                           valueInputOption='USER_ENTERED',
                                           body={'values': matriz_values}).execute()
            if format_requests:
                sheet.batchUpdate(spreadsheetId=sheet_id, body={'requests': format_requests}).execute()
            print(f"Datos insertados correctamente.\n{(result.get('updates').get('updatedCells'))}")


def search_csirt(list_csirt, gui, csirt_name, responsable='', ticket=''):
    max_attempts = 5
    url = "https://www.csirt.gob.cl/"

    url_list = {i: [] for i in csirt_name}
    #url_list = {'8FPH': [], '2CMV': [], '8FFR': [], '4IIVº': [], '4IIA': []}
    filter_csirt = []
    for page in range(1, 10):
        attempts = 1
        while attempts <= max_attempts:
            try:
                data = requests.get(url+"alertas/"+"?p="+str(page))
                data.raise_for_status()
                break
            except requests.exceptions.ConnectionError as e:
                print(f"Error al obtener la página {page}: {e}")
                gui.update_text("error", f"Error al obtener la página {page}: {e}")
                print(f"Intento {attempts}/{max_attempts}. Esperando 10 segundos antes de volver a intentar...")
                time.sleep(10)  # Esperar 10 segundos antes de intentar nuevamente
                attempts += 1
        else:
            # Si se alcanza el máximo de intentos sin éxito, mostrar un mensaje y continuar con la siguiente página
            gui.update_text("error", f"No se pudo obtener la página {page} después de {max_attempts} intentos. Pasando a la siguiente página...")
            print(f"No se pudo obtener la página {page} después de {max_attempts} intentos. Pasando a la siguiente página...")
            continue

        soup = BeautifulSoup(data.text, 'html.parser')
        for i in soup.find_all('a', href=lambda x: x and x.startswith('/alertas/')):
            if not i.find('picture'):
                try:
                    link = i.find('h3').get_text().upper()
                    date = convert_date(i.find('time').get_text().replace(" ", ""))

                    if any(link.lower() in value.lower() for value in list_csirt.values()):
                        filter_csirt.append(re.search(r'(?:(?<=\b)\d{1})?(\w{3})(?=\d{2})', link).group(1))
                    elif re.search(r'(?:(?<=\b)\d)?(\w{3})(?=\d{2})', link).group(1) in filter_csirt:
                        continue
                    else:
                        try:
                            revision = re.search(r'\b\d{2}\b', link.replace("/", "")).group()
                        except AttributeError as e:
                            revision = "0"

                        dict_temp = {
                            'name': link.replace("/", ""),
                            'revision': revision,
                            'responsible': responsable,
                            'date': date,
                            'Ticket': f"Ticket padre {ticket}",
                            'Gestionado': ""
                        }
                        try:
                            key = re.search(r'(?:(?<=\b)\d)?(\w{3})(?=\d{2})', link).group(1)
                            for clave in url_list.keys():
                                if key in clave:
                                    url_list[clave].append(dict_temp),
                                    url_list[clave] = sorted(url_list[clave], key=lambda d: d['name'])
                        except KeyError:
                            pass
                except AttributeError:
                    pass

    return url_list


def convert_date(date):
    locale.setlocale(locale.LC_TIME, 'es_ES.utf-8')
    try:
        date_parts = date.split("alas")
        date_parts = date_parts[0].replace(" ", "").replace(chr(10), "")
        setting_date = date_parts.lower().split("de")
        setting_date = " ".join(setting_date)
        date_datetime = datetime.strptime(setting_date, "%d %B %Y")
        format_date = date_datetime.strftime("%d/%m/%Y")
        return format_date
    except ValueError:
        return None


def get_ioc(dict_csirt, gui):
    for keywords, values in dict_csirt.items():
        for value in values:
            if value['name'] != "[]":
                print(f"Extrayendo IoC de la alerta {value['name']}")
                gui.update_text("info", f"Extrayendo IoC de la alerta {value['name']}")
                dict_ioc = download_ioc(value['name'], gui)
                value['name'] = re.search(r'(\d?\w{3}\d{2}-\d+(?:-\d{2})?)', value['name']).group(1)
                value['ioc'] = dict_ioc
    return dict_csirt


def download_ioc(name_csirt, gui):
    def decrypt_cfemail(cfemail):
        email = ""
        key = int(cfemail[:2], 16)
        for i in range(2, len(cfemail), 2):
            char_code = int(cfemail[i:i+2], 16) ^ key
            email += chr(char_code)
        return email

    url = "https://www.csirt.gob.cl/alertas/"
    dict_ioc = creater_dict_csirt()
    max_attempts = 5
    attempts = 1
    while attempts <= max_attempts:
        try:
            data = requests.get(url+name_csirt.lower())
            data.raise_for_status()
            break
        except requests.RequestException as e:
            print(f"Error al obtener la página {url+name_csirt.lower()}: {e}")
            gui.update_text("error", f"Error al obtener la página {url+name_csirt.lower()}: {e}")
            print(f"Intento {attempts}/{max_attempts}. Esperando 10 segundos antes de volver a intentar...")
            time.sleep(10)  # Esperar 5 segundos antes de intentar nuevamente
            attempts += 1
    else:
        # Si se alcanza el máximo de intentos sin éxito, mostrar un mensaje y continuar con la siguiente página
        print(f"No se pudo obtener los IoC de {url+name_csirt.lower()} después de {max_attempts} intentos. Pasando a la siguiente página...")
        new_dict_ioc = {k: "[null]" for k, v in dict_ioc.items()}
        return new_dict_ioc

    soup = BeautifulSoup(data.text, 'html.parser')

    # Encontrar la tabla
    tabla = soup.find('table')

    # Inicializar una lista para almacenar los datos de la tabla
    datos_tabla = []

    # Iterar sobre las filas de la tabla
    for fila in tabla.find_all('tr'):
        # Obtener todas las celdas de la fila
        celdas = fila.find_all(['th', 'td'])
        # Extraer el texto de cada celda y eliminar los espacios en blanco adicionales
        datos_fila = []
        for celda in celdas:
            # Verificar si la celda contiene un enlace cifrado
            enlace_cfemail = celda.find('a', class_='__cf_email__')
            if enlace_cfemail:
                # Si se encuentra un enlace cifrado, descifrar y agregar el valor real
                correo_real = decrypt_cfemail(enlace_cfemail['data-cfemail'])
                datos_fila.append(correo_real)
            else:
                # Si no se encuentra un enlace cifrado, simplemente agregar el texto de la celda
                datos_fila.append(celda.get_text(strip=True))
        # Agregar los datos de la fila a la lista de datos de la tabla
        datos_tabla.append(datos_fila)

    # Imprimir los datos de la tabla

    for fila in datos_tabla:
        if fila[0] == "IPv4" or fila[0].lower() == "ip:puerto":
            if "sitio falso" in fila[2].lower():
                dict_ioc["ips"].append(fila[1])
            elif "smtp" in fila[2].lower():
                dict_ioc['smtp'].append(fila[1])
            else:
                dict_ioc["ips"].append(fila[1])
        elif fila[0].lower() == "url":
            dict_ioc['url'].append(fila[1])
        elif fila[0].lower() == "email":
            dict_ioc['correo'].append(fila[1])
        elif fila[0].lower() == "sha256":
            dict_ioc['sha2'].append(fila[1])
        elif fila[0].lower() == "dominio":
            dict_ioc['dominio'].append(fila[1])

    new_dict_ioc = {k: v for k, v in dict_ioc.items() if [item for item in v if item != "[]"]}
    return new_dict_ioc


def creater_dict_csirt():
    dict_csirt = {
        'url': [],
        'ips': [],
        'correo': [],
        'smtp': [],
        'md5': [],
        'sha1': [],
        'sha2': [],
        'dominio': []
    }
    return dict_csirt


def create_spreadsheet(credentials, folder_name, file_name):
    drive_service = build('drive', 'v3', credentials=credentials)
    results_drive = drive_service.files().list(
        q=f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'", fields="files(id, name)").execute()
    folder_data = results_drive.get('files', [])[0]

    drive_file_metadata = {
        'name': [file_name],
        'parents': [folder_data['id']],
        'mimeType': 'application/vnd.google-apps.spreadsheet'
    }

    drive_file = drive_service.files().create(body=drive_file_metadata, media_body='').execute()

    return drive_file['id']


def load_ioc_csirt(credentials, spreadsheet_id, data):
    service = build('sheets', 'v4', credentials=credentials)
    sheet = service.spreadsheets()
    html_table = ""
    ioc = []
    list_url = []
    list_ips = []
    list_hash = []
    list_correo = []
    list_smtp = []

    for category, values in data.items():
        if values:
            [ioc.append(iocs.pop('ioc')) for iocs in values]
            df = pd.DataFrame(values)
            html_table += f"<h3>{category}</h3>{df.to_html(index=False, classes='table table-hover')} <br>"
            sheet.batchUpdate(spreadsheetId=spreadsheet_id,
                              body={'requests': [{'addSheet': {'properties': {'title': category}}}]}).execute()
            body = {'values': [df.columns.tolist()] + df.values.tolist()}

            sheet.values().update(spreadsheetId=spreadsheet_id, range=category,
                                  valueInputOption='RAW', body=body).execute()

    info_sheets = sheet.get(spreadsheetId=spreadsheet_id).execute()['sheets']
    for info_sheet in info_sheets:
        properties = info_sheet['properties']
        sheet_id = properties['sheetId']

        if properties['title'] == 'Hoja 1':
            sheet.batchUpdate(spreadsheetId=spreadsheet_id,
                              body={'requests': [{'deleteSheet': {'sheetId': sheet_id}}]}).execute()

    for value in ioc:
        list_url = list_url + value.get('url', list(""))
        list_ips = list_ips + value.get('ips', list(""))
        list_hash = list_hash + value.get('md5', list(""))
        list_hash = list_hash + value.get('sha1', list(""))
        list_hash = list_hash + value.get('sha2', list(""))
        list_correo = list_correo + value.get('correo', list(""))
        list_smtp = list_smtp + value.get('smtp', list(""))

    d = {'url': list_url, 'ips': list_ips, 'hash': list_hash, 'correo': list_correo, 'smtp': list_smtp}
    df = pd.DataFrame(dict([(key, pd.Series(value)) for key, value in d.items() if value]))
    sheet.batchUpdate(spreadsheetId=spreadsheet_id,
                      body={'requests': [{'addSheet': {'properties': {'title': 'IoC'}}}]}).execute()
    body = {'values': [df.columns.tolist()] + [[str(cell) if not pd.isna(cell) else '' for cell in row]
                                               for row in df.values.tolist()]}

    sheet.values().update(spreadsheetId=spreadsheet_id, range='IoC', valueInputOption='RAW', body=body).execute()

    return Modules.handler_variables_email.style_html + html_table


def get_alert_csirt_lastweek(data_csirt, first_day_lastweek, last_day_lastweek):
    alert_csirt_last_week = []
    try:

        for values_csirt in reversed(data_csirt['values']):
            target_date = datetime.strptime(values_csirt[3], "%d/%m/%Y")
            if last_day_lastweek <= target_date:
                pass
            elif first_day_lastweek <= target_date:
                alert_csirt_last_week.append(values_csirt)
            elif target_date <= first_day_lastweek:
                return alert_csirt_last_week
        return alert_csirt_last_week

    except ValueError as e:
        print(f"Error al procesar la fecha {data_csirt}: {e}")


def get_html_report(data_csirt, csirt_names):
    count = 1
    matriz_data = []
    columns = [
        'Nº',
        'Fecha',
        'Detalle Incidente / Reporte de vulnerabilidades',
        'Tipo (Phishing, virus, etc.)',
        'Criticidad (Alta, Media, Baja)',
        'Canal de información de obtención (Twitter, email, etc.)',
        'Plan de acción',
        'Fecha de implementación',
        'Chequeo post remediación'
    ]

    for csirt, values in data_csirt.items():
        for value in values:
            data_individual = []
            data_individual.extend([
                    count,
                    value[3],
                    value[0],
                    'Fraude Phishing',
                    'Alta',
                    'CSIRT',
                    csirt_names[csirt],
                    value[3],
                    'OK'
                ])


            matriz_data.append(data_individual)
            count += 1
    df = pd.DataFrame(matriz_data, columns=columns)
    html = df.to_html(escape=False, classes='table table-hover', border=0,
                      index=False)  # escape=False para permitir HTML en los datos

    # Agregar el estilo CSS al HTML generado
    return Modules.handler_variables_email.style_html + html


def send_reply(creds, user_id='me', sender_to='', reply_subject='', reply_body=''):
    service = build('gmail', 'v1', credentials=creds)
    # Construir el cuerpo del mensaje de respuesta
    reply_message = MIMEMultipart()
    reply_message['to'] = sender_to
    reply_message['subject'] = reply_subject

    # Agregar el cuerpo del mensaje de respuesta
    msg_body = MIMEText(reply_body, 'html')
    reply_message.attach(msg_body)

    # Convertir el mensaje a formato raw para enviarlo
    raw_message = base64.urlsafe_b64encode(reply_message.as_bytes()).decode('utf-8')
    body = {'raw': raw_message}

    # Enviar el mensaje de respuesta
    service.users().messages().send(userId=user_id, body=body).execute()


def validations_and_get_email(creds, user_id='me', msg_id=''):
    service = build('gmail', 'v1', credentials=creds)
    email_data = {}
    msg = service.users().messages().get(userId=user_id, id=msg_id).execute()

    email_data['sender_name'] = [header['value'] for header in msg['payload']['headers']
                                 if header['name'] == 'From'][0].replace('"', '').split("<")[0]
    email_data['subject'] = [header['value'] for header in msg['payload']['headers']
                             if header['name'] == 'Subject'][0]
    email_data['sender_email'] = [header['value'] for header in msg['payload']['headers']
                                  if header['name'] == 'Return-Path'][0][1:-1]

    if re.match(REG_SUBJECT, email_data.get('subject')):
        email_data['ticket_action'] = re.match(REG_SUBJECT, email_data['subject']).groups()
        email_data['isCorrect'] = True
        return email_data
    else:
        email_data['isCorrect'] = False
        return email_data


def mark_as_read(creds, user_id='me', msg_id=''):
    service = build('gmail', 'v1', credentials=creds)
    body = {'removeLabelIds': ['UNREAD']}
    service.users().messages().modify(userId=user_id, id=msg_id, body=body).execute()

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

def get_file_folder_url(service, file_id):
    # Obtiene la información del archivo
    file_info = service.files().get(fileId=file_id, fields='webViewLink').execute()

    # Obtiene y retorna la URL de visualización del archivo
    return file_info.get('webViewLink', None)

def check_file_exists(service, file_name, type_file):
    results = service.files().list(q=f"name='{file_name}' and mimeType='{type_file}' and trashed=false").execute()
    files = results.get('files', [])
    if files:
        return files[0]['id']
    else:
        return False


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

            csirt_mapping = {
                "8FPH": "Phishing",
                "2CMV": "Malware",
                "8FFR": "Sitios Fraudulentos",
                "4IIA": "Ataques de Fuerza Bruta",
                "4IIV": "Ataques de Fuerza Bruta",
                "ACF": "Campaña Fraudulenta",
                "AIA": "Investigacion de Amenazas"
            }

            config_cfg['credentials'] = {'path_key': credentials_name}
            config_cfg['configurations'] = {'domain': domain,
                                            'time_wait': time_wait,
                                            'folder_name': folder_name,
                                            'sheet_name': sheet_name,
                                            'folder_id': "",
                                            'sheet_id': "",
                                            'csirt_names': json.dumps(csirt_mapping, ensure_ascii=False)}

            with open(ruta_archivo_cfg, "w") as configfile:
                config_cfg.write(configfile)

            print(f"Archivo '{ruta_archivo_cfg}' creado correctamente.")

            return ruta_archivo_cfg
        else:
            print(f"El archivo '{ruta_archivo_cfg}' ya existe.")
            return ruta_archivo_cfg

    except Exception as e:
        print(f"Error al crear el archivo .cfg: {e}")
