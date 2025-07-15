from google_auth_oauthlib.flow import InstalledAppFlow
import Modules.handler_funtions as handler_funtions
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import Modules.handler_variables_email
import google.auth.exceptions
import threading
import httplib2
import json
import os
import logging


class GestionIoc(threading.Thread):
    def __init__(self, configuration, gui):
        super().__init__()
        self.stop_event = threading.Event()  # Crear el evento para controlar la detención del hilo
        self.gui = gui
        self.configuracion = configuration
        self.cargar_configuracion()
        self.creds = self.authentication_gmail(key_file=self.key)

        log_path = os.path.join("Logs", "servicio.log")
        self.logger = logging.getLogger("gestion_ioc")
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            handler = logging.FileHandler(log_path, encoding='utf-8')
            handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
            self.logger.addHandler(handler)

    def cargar_configuracion(self):
        self.key = self.configuracion.get('credentials', 'path_key')
        self.domain = self.configuracion.get('configurations', 'domain')
        self.time_wait = int(self.configuracion.get('configurations', 'time_wait'))
        self.sheet_name = self.configuracion.get('configurations', 'sheet_name')
        self.folder_name = self.configuracion.get('configurations', 'folder_name')
        self.sheet_id = self.configuracion.get('configurations', 'sheet_id')
        self.folder_id = self.configuracion.get('configurations', 'folder_id')
        self.sheet_url = self.configuracion.get('configurations', 'sheet_url')
        self.url_folder = self.configuracion.get('configurations', 'url_folder')
        self.csirt_name = json.loads(self.configuracion['configurations']['csirt_names'])

    def stop(self):
        self.stop_event.set()

    def run(self):
        try:
            while not self.stop_event.is_set():
                self.logger.info("Revisando si hay nuevo correo")
                self.gui.update_text("info", "Revisando si hay nuevo correo")
                self.monitor_correos()
                self.stop_event.wait(self.time_wait)
        except Exception as e:
            self.handle_error(e)

    def handle_error(self, error):
        import traceback
        self.logger.error(f"Error inesperado: {type(error).__name__} - {error}")
        self.gui.update_text("error", f"Error inesperado: {type(error).__name__} - {error}", is_error=True)
        traceback.print_exc()
        self.stop()

    def monitor_correos(self):
        try:
            messages = handler_funtions.list_messages(self.creds, query=f'is:unread from:{self.domain}')
            if messages:
                self.logger.info("Nuevo correo detectado")
                self.gui.update_text("info", "Nuevo correo detectado, se da inicio a la gestion requerida")
                for message in messages:
                    self.procesar_mensaje(message)
            else:
                msg = f"No hay correos nuevos que gestionar, se volverá a revisar en {self.time_wait} seg."
                self.logger.info(msg)
                self.gui.update_text("info", msg)
        except httplib2.error.ServerNotFoundError as e:
            self.handle_error(e)

    def procesar_mensaje(self, message):
        msg_id = message['id']
        email_info = handler_funtions.validations_and_get_email(self.creds, msg_id=msg_id)
        if email_info['isCorrect']:
            handler_funtions.send_reply(
                self.creds,
                sender_to=email_info['sender_email'],
                reply_subject=f"Re: {email_info['subject']}",
                reply_body=Modules.handler_variables_email.body_messages["validation"]
            )
            self.gui.update_text("info", f"Validacion exitosa, respuesta enviada a: {email_info['sender_email']}")

            if email_info['ticket_action'][2] == "ioc":
                self.management_ioc_csirt(email_info)
            elif email_info['ticket_action'][2] == "reporte":
                self.management_report_csirt(email_info)
        else:
            handler_funtions.send_reply(
                self.creds,
                sender_to=email_info['sender_email'],
                reply_subject=f"Re: {email_info['subject']}",
                reply_body=f"{Modules.handler_variables_email.body_messages['invalidation']} {email_info['subject']}"
            )
            self.gui.update_text("warning", f"Correo fallido: {email_info['subject']}")

        self.gui.update_text("info", "Se marca el correo como leido!")
        handler_funtions.mark_as_read(self.creds, msg_id=msg_id)

    def management_ioc_csirt(self, email_info):
        self.gui.update_text("info", "Obteniendo ultimos CSIRT desde el google drive")
        last_csirt_in_sheets = handler_funtions.handler_sheets("get", self.sheet_id, credentials=self.creds)
        last_csirt_in_web = handler_funtions.search_csirt(
            last_csirt_in_sheets, self.gui, self.csirt_name,
            responsable=email_info['sender_name'],
            ticket=email_info['ticket_action'][0]
        )

        if not all(not details for details in last_csirt_in_web.values()):
            self.gui.update_text("info", "Buscando y extrayendo los IoC de las alertas no gestionadas")
            handler_funtions.get_ioc(last_csirt_in_web, self.gui)

            self.gui.update_text("info", "Importando Alertas CSIRT a Google Drive")
            handler_funtions.handler_sheets("insert", self.sheet_id, self.creds, last_csirt_in_web)

            self.gui.update_text("info", "Creando archivo en google drive de alertas e ioc")
            new_sheet = handler_funtions.create_spreadsheet(self.creds, self.folder_name, email_info['ticket_action'][0])

            self.gui.update_text("info", "Cargando IoCs")
            html_table = handler_funtions.load_ioc_csirt(self.creds, new_sheet, last_csirt_in_web)

            self.gui.update_text("info", "Enviando correo!")
            handler_funtions.send_reply(
                self.creds,
                sender_to=email_info['sender_email'],
                reply_subject=f"Re: {email_info['subject']}",
                reply_body=(
                    f"{Modules.handler_variables_email.body_messages['send_alert']}{html_table}"
                    f"{Modules.handler_variables_email.body_messages['link_sheet']}{self.sheet_url}"
                    f"{Modules.handler_variables_email.body_messages['ioc']}{self.url_folder}"
                )
            )
        else:
            handler_funtions.send_reply(
                self.creds,
                sender_to=email_info['sender_email'],
                reply_subject=f"Re: {email_info['subject']}",
                reply_body=Modules.handler_variables_email.body_messages['no_alerts']
            )
            self.gui.update_text("info", f"No hay alertas CSIRT nuevas, correo enviado a {email_info['sender_email']}")

    def management_report_csirt(self, email_info):
        alert_csirt_last_week = {}
        service_drive = build('sheets', 'v4', credentials=self.creds)
        sheet = service_drive.spreadsheets()

        res = sheet.get(spreadsheetId=self.sheet_id).execute()
        sheets_name = [x.get('properties').get('title') for x in res.get("sheets", [])]

        today = datetime.now()
        first_day_lastweek = today - timedelta(days=today.weekday() + 8)
        last_day_lastweek = first_day_lastweek + timedelta(days=7)

        for name in sheets_name:
            data = sheet.values().get(spreadsheetId=self.sheet_id, range=name).execute()
            print(data)
            result = handler_funtions.get_alert_csirt_lastweek(data, first_day_lastweek, last_day_lastweek)
            if result:
                alert_csirt_last_week[name] = result

        first_day_lastweek += timedelta(days=1)
        html_email = handler_funtions.get_html_report(alert_csirt_last_week, self.csirt_name)

        handler_funtions.send_reply(
            self.creds,
            sender_to=email_info['sender_email'],
            reply_subject=(
                f"Re: {email_info['subject'].split(' ')[0]} REPORTE SEGURIDAD SEMANA "
                f"{first_day_lastweek.day}-{str(first_day_lastweek.month).zfill(2)}-{first_day_lastweek.year} "
                f"al {last_day_lastweek.day}-{str(last_day_lastweek.month).zfill(2)}-{last_day_lastweek.year}"
            ),
            reply_body=(
                f"{Modules.handler_variables_email.body_messages['send_report']}<br>{html_email}<br>"
                f"{Modules.handler_variables_email.body_messages['link_sheet']}{self.sheet_url}"
            )
        )

    def authentication_gmail(self, token_file=os.path.join('Keys', 'token.json'), key_file=''):
        scopes = [
            'https://www.googleapis.com/auth/drive.metadata.readonly',
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive.file',
            'https://www.googleapis.com/auth/drive',
            'https://www.googleapis.com/auth/gmail.readonly',
            'https://www.googleapis.com/auth/gmail.modify'
        ]

        try:
            credentials = Credentials.from_authorized_user_file(token_file, scopes=scopes)
            if credentials.expired:
                credentials.refresh(Request())
                with open(token_file, 'w') as token:
                    token.write(credentials.to_json())
        except (FileNotFoundError, ValueError, google.auth.exceptions.RefreshError):
            self.gui.update_text("warning", "Se requiere autorización. Abriendo navegador...")
            flow = InstalledAppFlow.from_client_secrets_file(key_file, scopes)
            credentials = flow.run_local_server(port=0)
            with open(token_file, 'w') as token:
                token.write(credentials.to_json())
            self.gui.update_text("info", "Autorización exitosa. Credenciales guardadas.")

        return credentials
