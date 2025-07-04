import os
import re
import json
import copy
import base64
import locale
import logging
import requests
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import Modules.handler_variables_email

REG_SUBJECT = r'\[(.*)\]\s((ioc|reporte)\scsirt)$'
reg_ip = r"(((25[0-5]|2[0-4]\d|[01]?\d\d?)\\[?\\.]?){3}(25[0-5]|2[0-4]\d|[01]?\d\d?))"
reg_url = r"((hxxps|hxxp|https|http)\\[?\\:?]?\/\\/?[a-zA-Z0-9]+.*)$"
reg_correo = r"(.*\@.*\\[?\\.]?\w{1,4}?)$"
reg_dominio = r"([a-zA-Z0-9]+((\\.|\\-|\\_)?)([a-zA-Z0-9]+)?\\[?\\.]?\w{2,5})$"
reg_sha2 = r"([0-9a-fA-F]{64}$)"
reg_sha1 = r"(^[0-9a-fA-F]{40}$)"
reg_md5 = r"(^[0-9a-fA-F]{32}$)"

logging.basicConfig(filename='Logs/handler.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


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


def authenticate_google_services(token_file='Keys/token.json', key_file=''):
    scopes = [
        'https://www.googleapis.com/auth/drive.metadata.readonly',
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive.file',
        'https://www.googleapis.com/auth/drive',
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.modify'
    ]
    try:
        creds = Credentials.from_authorized_user_file(token_file, scopes)
        if creds.expired:
            creds.refresh(Request())
            with open(token_file, 'w') as token:
                token.write(creds.to_json())
    except (FileNotFoundError, ValueError, Exception):
        flow = InstalledAppFlow.from_client_secrets_file(key_file, scopes)
        creds = flow.run_local_server(port=0)
        with open(token_file, 'w') as token:
            token.write(creds.to_json())
    return creds


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
    url = "https://www.csirt.gob.cl/"
    url_list = {i: [] for i in csirt_name}
    filter_csirt = []
    for page in range(1, 10):
        try:
            data = requests.get(url + "alertas/" + f"?p={page}")
            data.raise_for_status()
        except Exception as e:
            gui.update_text("error", f"Error al obtener la página {page}: {e}")
            continue
        soup = BeautifulSoup(data.text, 'html.parser')
        for i in soup.find_all('a', href=lambda x: x and x.startswith('/alertas/')):
            if not i.find('picture'):
                try:
                    link = i.find('h3').get_text().upper()
                    date = convert_date(i.find('time').get_text().replace(" ", ""))
                    if any(link.lower() in value.lower() for value in list_csirt.values()):
                        filter_csirt.append(re.search(r'(?:(?<=\b)\d)?(\w{3})(?=\d{2})', link).group(1))
                    elif re.search(r'(?:(?<=\b)\d)?(\w{3})(?=\d{2})', link).group(1) in filter_csirt:
                        continue
                    else:
                        revision = re.search(r'\b\d{2}\b', link.replace("/", "")).group() if re.search(r'\b\d{2}\b', link.replace("/", "")) else "0"
                        dict_temp = {
                            'name': link.replace("/", ""),
                            'revision': revision,
                            'responsible': responsable,
                            'date': date,
                            'Ticket': f"Ticket padre {ticket}",
                            'Gestionado': ""
                        }
                        key = re.search(r'(?:(?<=\b)\d)?(\w{3})(?=\d{2})', link).group(1)
                        for clave in url_list.keys():
                            if key in clave:
                                url_list[clave].append(dict_temp)
                                url_list[clave] = sorted(url_list[clave], key=lambda d: d['name'])
                except Exception:
                    pass
    return url_list


def get_ioc(dict_csirt, gui):
    for keyword, values in dict_csirt.items():
        for value in values:
            if value['name'] != "[]":
                gui.update_text("info", f"Extrayendo IoC de la alerta {value['name']}")
                print(f"Extrayendo IoC de la alerta {value['name']}")
                dict_ioc = download_ioc(value['name'], gui)
                try:
                    value['name'] = re.search(r'(\d?\w{3}\d{2}-\d+(?:-\d{2})?)', value['name']).group(1)
                except Exception:
                    pass
                value['ioc'] = dict_ioc
    return dict_csirt


def download_ioc(name_csirt, gui):
    def decrypt_cfemail(cfemail):
        key = int(cfemail[:2], 16)
        return ''.join(chr(int(cfemail[i:i+2], 16) ^ key) for i in range(2, len(cfemail), 2))

    url = f"https://www.csirt.gob.cl/alertas/{name_csirt.lower()}"
    dict_ioc = {
        'url': [], 'ips': [], 'correo': [], 'smtp': [],
        'md5': [], 'sha1': [], 'sha2': [], 'dominio': []
    }

    try:
        response = requests.get(url)
        response.raise_for_status()
    except Exception as e:
        gui.update_text("error", f"Error al acceder a {url}: {e}")
        return {k: ["[null]"] for k in dict_ioc}

    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table')
    if not table:
        return {k: ["[null]"] for k in dict_ioc}

    for row in table.find_all('tr'):
        cols = row.find_all(['th', 'td'])
        clean = []
        for cell in cols:
            encrypted = cell.find('a', class_='__cf_email__')
            if encrypted:
                clean.append(decrypt_cfemail(encrypted['data-cfemail']))
            else:
                clean.append(cell.get_text(strip=True))
        if len(clean) < 3:
            continue
        tipo, valor, descripcion = clean[0].lower(), clean[1], clean[2].lower()
        if tipo in ("ipv4", "ip:puerto"):
            if "smtp" in descripcion:
                dict_ioc['smtp'].append(valor)
            else:
                dict_ioc['ips'].append(valor)
        elif tipo == "url":
            dict_ioc['url'].append(valor)
        elif tipo == "email":
            dict_ioc['correo'].append(valor)
        elif tipo == "sha256":
            dict_ioc['sha2'].append(valor)
        elif tipo == "dominio":
            dict_ioc['dominio'].append(valor)

    return {k: v for k, v in dict_ioc.items() if v}


def create_spreadsheet(credentials, folder_name, file_name):
    drive_service = build('drive', 'v3', credentials=credentials)
    results = drive_service.files().list(
        q=f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'",
        fields="files(id, name)"
    ).execute()
    folder = results.get('files', [])[0]

    metadata = {
        'name': file_name,
        'parents': [folder['id']],
        'mimeType': 'application/vnd.google-apps.spreadsheet'
    }

    spreadsheet = drive_service.files().create(body=metadata, fields='id').execute()
    return spreadsheet['id']


def load_ioc_csirt(credentials, spreadsheet_id, data):
    sheet_service = build('sheets', 'v4', credentials=credentials)
    sheet = sheet_service.spreadsheets()

    html_table = ""
    ioc_all = []

    for category, values in data.items():
        if values:
            [ioc_all.append(entry.pop('ioc')) for entry in values if 'ioc' in entry]
            df = pd.DataFrame(values)
            html_table += f"<h3>{category}</h3>" + df.to_html(index=False, classes='table table-hover') + "<br>"
            sheet.batchUpdate(spreadsheetId=spreadsheet_id,
                              body={'requests': [{'addSheet': {'properties': {'title': category}}}]}).execute()
            body = {'values': [df.columns.tolist()] + df.values.tolist()}
            sheet.values().update(spreadsheetId=spreadsheet_id, range=category,
                                  valueInputOption='RAW', body=body).execute()

    info_sheets = sheet.get(spreadsheetId=spreadsheet_id).execute()['sheets']
    for info in info_sheets:
        if info['properties']['title'] == 'Hoja 1':
            sheet.batchUpdate(spreadsheetId=spreadsheet_id,
                              body={'requests': [{'deleteSheet': {'sheetId': info['properties']['sheetId']}}]}).execute()

    flat_iocs = {'url': [], 'ips': [], 'hash': [], 'correo': [], 'smtp': []}
    for ioc_dict in ioc_all:
        flat_iocs['url'].extend(ioc_dict.get('url', []))
        flat_iocs['ips'].extend(ioc_dict.get('ips', []))
        flat_iocs['hash'].extend(ioc_dict.get('md5', []) + ioc_dict.get('sha1', []) + ioc_dict.get('sha2', []))
        flat_iocs['correo'].extend(ioc_dict.get('correo', []))
        flat_iocs['smtp'].extend(ioc_dict.get('smtp', []))

    df_ioc = pd.DataFrame({k: pd.Series(v) for k, v in flat_iocs.items() if v})
    sheet.batchUpdate(spreadsheetId=spreadsheet_id,
                      body={'requests': [{'addSheet': {'properties': {'title': 'IoC'}}}]}).execute()
    body_ioc = {'values': [df_ioc.columns.tolist()] + df_ioc.fillna('').values.tolist()}
    sheet.values().update(spreadsheetId=spreadsheet_id, range='IoC',
                          valueInputOption='RAW', body=body_ioc).execute()

    return Modules.handler_variables_email.style_html + html_table


def get_alert_csirt_lastweek(data, first_day, last_day):
    headers = data.get('values', [])[0]
    date_idx = headers.index("date") if "date" in headers else -1
    rows = data.get('values', [])[1:]
    if date_idx == -1:
        return []
    filtered = [row for row in rows if len(row) > date_idx and first_day.strftime("%d/%m/%Y") <= row[date_idx] <= last_day.strftime("%d/%m/%Y")]
    return filtered


def get_html_report(csirt_data, csirt_name):
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

    for csirt, values in csirt_data.items():
        for value in values:
            data_individual = []
            data_individual.extend([
                    count,
                    value[3],
                    value[0],
                    'Fraude Phishing',
                    'Alta',
                    'CSIRT',
                    csirt_name[csirt],
                    value[3],
                    'OK'
                ])

            matriz_data.append(data_individual)
            count += 1
    df = pd.DataFrame(matriz_data, columns=columns)
    html = df.to_html(escape=False, classes='table table-hover', border=0,
                      index=False)

    # Agregar el estilo CSS al HTML generado
    return Modules.handler_variables_email.style_html + html


def send_reply(creds, sender_to, reply_subject, reply_body):
    service = build('gmail', 'v1', credentials=creds)
    message = MIMEMultipart('alternative')
    message['to'] = sender_to
    message['subject'] = reply_subject
    part1 = MIMEText(reply_body, 'html')
    message.attach(part1)

    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    message_body = {'raw': raw_message}
    service.users().messages().send(userId='me', body=message_body).execute()


def mark_as_read(creds, msg_id):
    service = build('gmail', 'v1', credentials=creds)
    service.users().messages().modify(userId='me', id=msg_id, body={'removeLabelIds': ['UNREAD']}).execute()


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
    else:
        email_data['isCorrect'] = False

    return email_data


def crear_configuracion(root_path, config_cfg):
    ruta_archivo_cfg = os.path.join(root_path, 'Config', "configuration.cfg")
    try:
        if not os.path.isfile(ruta_archivo_cfg):
            while True:
                credentials_name = os.path.join(root_path, input("Ingresar nombre del archivo json descargada de Google: ").strip())
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


def prueba_google_drive(folder_name, creds):
    folder_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder'
    }

    share_permission = {
        'type': 'anyone',
        'role': 'writer'
    }

    drive_service = build('drive', 'v3', credentials=creds)
    folder_id = check_file_exists(drive_service, folder_name, 'application/vnd.google-apps.folder')

    if not folder_id:
        folder = drive_service.files().create(body=folder_metadata, fields='id').execute()
        folder_id = folder['id']
        print(f"Prueba de acceso y creación de carpeta compartida {folder_name} exitosa...")
    else:
        print(f"Prueba de acceso exitosa, carpeta compartida {folder_name} ya existe")

    drive_service.permissions().create(fileId=folder_id, body=share_permission).execute()
    url_folder = get_file_folder_url(drive_service, folder_id)
    return {'url_folder': url_folder, 'folder_id': folder_id}


def get_file_folder_url(service, file_id):
    file_info = service.files().get(fileId=file_id, fields='webViewLink').execute()
    return file_info.get('webViewLink', None)


def check_file_exists(service, file_name, type_file):
    results = service.files().list(q=f"name='{file_name}' and mimeType='{type_file}' and trashed=false").execute()
    files = results.get('files', [])
    return files[0]['id'] if files else False
