import configparser
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
import Modules.handler_funtions as handler_funtions
import google.auth.exceptions
import pandas as pd
import locale
import os
import re
import requests
import json
import time
from datetime import datetime
from googleapiclient.discovery import build
from datetime import datetime, timedelta

from bs4 import BeautifulSoup


def authentication_gmail(token_file='Keys\\token.json', key_file=''):
        scopes = [
            'https://www.googleapis.com/auth/drive.metadata.readonly',
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive.file',
            'https://www.googleapis.com/auth/drive',
            'https://www.googleapis.com/auth/gmail.readonly',
            'https://www.googleapis.com/auth/gmail.modify'
        ]

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


def management_report_csirt(creds, sheet_id, csirt_name):
        alert_csirt_last_week = {}
        service_drive = build('sheets', 'v4', credentials=creds)
        sheet = service_drive.spreadsheets()

        res = sheet.get(spreadsheetId=sheet_id).execute()
        sheets_name = [x.get('properties').get('title') for x in res.get("sheets", [])]


        # Obtener la fecha de inicio y fin de la semana pasada
        today = datetime.now()
        first_day_lastweek = today - timedelta(days=today.weekday() + 8)
        last_day_lastweek = first_day_lastweek + timedelta(days=7)

        for sheet_name in sheets_name:
            data = sheet.values().get(spreadsheetId=sheet_id, range=sheet_name).execute()
            result = handler_funtions.get_alert_csirt_lastweek(data, first_day_lastweek, last_day_lastweek)
            if result:
                alert_csirt_last_week[sheet_name] = result
        first_day_lastweek += timedelta(days=1)
        html_email = get_html_report(alert_csirt_last_week, csirt_name)

        #return html_email

def get_html_report(data_csirt, csirt_name):
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
                    csirt_name[csirt],
                    value[3],
                    'OK'
                ])
            """if csirt == '8FPH':
                data_individual.extend([
                    count,
                    value[3],
                    value[0],
                    'Fraude Phishing',
                    'Alta',
                    'CSIRT',
                    'Bloqueo URL/SMTP/Filtro contenido',
                    value[3],
                    'OK'
                ])
            elif csirt == '2CMV':
                data_individual.extend([
                    count,
                    value[3],
                    value[0],
                    'Fraude Malware',
                    'Alta',
                    'CSIRT',
                    'Bloqueo URL/Dominio/Hash',
                    value[3],
                    'OK'
                ])
            elif csirt == '8FFR':
                data_individual.extend([
                    count,
                    value[3],
                    value[0],
                    'Fraude Malware',
                    'Alta',
                    'CSIRT',
                    'Bloqueo URL/Dominio',
                    value[3],
                    'OK'
                ])"""
            matriz_data.append(data_individual)
            count += 1
    df = pd.DataFrame(matriz_data, columns=columns)
    print(df)
    html = df.to_html(escape=False, classes='table table-hover', border=0,
                      index=False)  # escape=False para permitir HTML en los datos

configuracion = configparser.ConfigParser()
configuracion.read('Config\\configuration.cfg')
csirt_name = json.loads(configuracion['configurations']['csirt_names'])
sheet_id = configuracion.get('configurations', 'sheet_id')
key = configuracion.get('credentials', 'path_key')
creds = authentication_gmail(key_file=key)

resultado = management_report_csirt(creds, sheet_id, csirt_name)

print(resultado)
