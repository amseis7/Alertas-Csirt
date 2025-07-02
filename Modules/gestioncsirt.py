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


class GestionIoc(threading.Thread):
    def __init__(self, configuration, gui):
        super().__init__()
        self.stop_event = threading.Event()  # Crear el evento para controlar la detención del hilo
        self.gui = gui
        self.key = configuration.get('credentials', 'path_key')
        self.domain = configuration.get('configurations', 'domain')
        self.time_wait = int(configuration.get('configurations', 'time_wait'))
        self.sheet_name = configuration.get('configurations', 'sheet_name')
        self.folder_name = configuration.get('configurations', 'folder_name')
        self.sheet_id = configuration.get('configurations', 'sheet_id')
        self.folder_id = configuration.get('configurations', 'folder_id')
        self.sheet_url = configuration.get('configurations', 'sheet_url')
        self.url_folder = configuration.get('configurations', 'url_folder')
        self.csirt_name = json.loads(configuration['configurations']['csirt_names'])
        self.creds = self.authentication_gmail(key_file=self.key)

    def stop(self):
        self.stop_event.set()

    def run(self):
        while not self.stop_event.is_set():
            try:
                # Realizar alguna tarea
                self.gui.update_text("info", "Revisando si hay nuevo correo")
                print("Revisando si hay nuevo correo")
                self.monitor_correos()
                # Esperar un tiempo antes de continuar
                self.stop_event.wait(self.time_wait)

            except httplib2.error.ServerNotFoundError as e:
                self.stop()
                print(f"Error: {e}, no se puede acceder a los servidores de Google, favor de probar la conexion a internet")
                self.gui.update_text(f"Error: {e}, no se puede acceder a los servidores de Google, favor de probar la conexion a internet", is_error=True)

            # except Exception as e:
            #     # Obtener información detallada sobre la excepción
            #     _, _, exc_tb = sys.exc_info()
            #     fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            #     line_number = exc_tb.tb_lineno
            #     print(f"Type: {type(e).__name__}, Error: {e}., Archivo: {fname}, Línea: {line_number}")
            #     self.gui.update_text("error", f"Type: {type(e).__name__}, Error: {e}., Archivo: {fname}, Línea: {line_number}")
            #     self.creds = self.authentication_gmail(key_file=self.key)
            #     time.sleep(5)

    def management_ioc_csirt(self, email_info):
        print("Obteniendo ultimos CSIRT desde el google drive")
        self.gui.update_text("info", "Obteniendo ultimos CSIRT desde el google drive")
        last_csirt_in_sheets = handler_funtions.handler_sheets("get", self.sheet_id, credentials=self.creds)
        print(last_csirt_in_sheets)
        last_csirt_in_web = handler_funtions.search_csirt(last_csirt_in_sheets, self.gui, self.csirt_name, responsable=email_info['sender_name'],
                                                          ticket=email_info['ticket_action'][0])
        print(last_csirt_in_web)
        if not all(not details for details in last_csirt_in_web.values()):
            print("Buscando y extrayendo los IoC de las alertas no gestionadas")
            self.gui.update_text("info", "Buscando y extrayendo los IoC de las alertas no gestionadas")
            handler_funtions.get_ioc(last_csirt_in_web, self.gui)
            print("Importando Alertas CSIRT a Google Drive")
            self.gui.update_text("info", "Importando Alertas CSIRT a Google Drive")
            handler_funtions.handler_sheets("insert", self.sheet_id, self.creds, last_csirt_in_web)
            print("Creando archivo en google drive de alertas e ioc")
            self.gui.update_text("info", "Creando archivo en google drive de alertas e ioc")
            new_sheet = handler_funtions.create_spreadsheet(self.creds, self.folder_name,
                                                            email_info['ticket_action'][0])
            print("Cargando IoCs")
            self.gui.update_text("info", "Cargando IoCs")
            html_table = handler_funtions.load_ioc_csirt(self.creds, new_sheet, last_csirt_in_web)
            print("Enviando correo!")
            self.gui.update_text("info", "Enviando correo!")
            handler_funtions.send_reply(self.creds, sender_to=email_info['sender_email'],
                                        reply_subject=f"Re: {email_info['subject']}",
                                        reply_body=f"{Modules.handler_variables_email.body_send_alert}{html_table}"
                                                   f"{Modules.handler_variables_email.body_link_sheet}{self.sheet_url}"
                                                   f"{Modules.handler_variables_email.body_ioc}{self.url_folder}")
        else:
            handler_funtions.send_reply(self.creds, sender_to=email_info['sender_email'],
                                        reply_subject=f"Re: {email_info['subject']}",
                                        reply_body=Modules.handler_variables_email.body_not_new_alerts)
            self.gui.update_text("info", f"No hay alertas CSIRT nuevas, se envia correo a "
                                 f"{email_info['sender_email']} informando.")
            print(f"No hay alertas CSIRT nuevas, se envia correo a {email_info['sender_email']} informando.")

    def management_report_csirt(self, email_info):
        alert_csirt_last_week = {}
        service_drive = build('sheets', 'v4', credentials=self.creds)
        sheet = service_drive.spreadsheets()

        res = sheet.get(spreadsheetId=self.sheet_id).execute()
        sheets_name = [x.get('properties').get('title') for x in res.get("sheets", [])]

        # Obtener la fecha de inicio y fin de la semana pasada
        today = datetime.now()
        first_day_lastweek = today - timedelta(days=today.weekday() + 8)
        last_day_lastweek = first_day_lastweek + timedelta(days=7)

        for sheet_name in sheets_name:
            data = sheet.values().get(spreadsheetId=self.sheet_id, range=sheet_name).execute()
            result = handler_funtions.get_alert_csirt_lastweek(data, first_day_lastweek, last_day_lastweek)
            if result:
                alert_csirt_last_week[sheet_name] = result
        first_day_lastweek += timedelta(days=1)
        html_email = handler_funtions.get_html_report(alert_csirt_last_week, self.csirt_name)
        handler_funtions.send_reply(self.creds, sender_to=email_info['sender_email'],
                                    reply_subject=f'Re: {email_info["subject"].split(" ")[0]} '
                                                  f'REPORTE SEGURIDAD SEMANA '
                                                  f'{first_day_lastweek.day}-'
                                                  f'{str(first_day_lastweek.month).zfill(2)}-'
                                                  f'{first_day_lastweek.year} al {last_day_lastweek.day}-'
                                                  f'{str(last_day_lastweek.month).zfill(2)}-'
                                                  f'{last_day_lastweek.year}',
                                    reply_body=f"{Modules.handler_variables_email.body_send_report}<br>"
                                               f"{html_email}<br>{Modules.handler_variables_email.body_link_sheet}"
                                               f"{self.sheet_url}")

    def monitor_correos(self):
        messages = handler_funtions.list_messages(self.creds, query=f'is:unread from:{self.domain}')
        if messages:
            print("Nuevo correo detectado, se da inicio a la gestion requerida")
            self.gui.update_text("info", "Nuevo correo detectado, se da inicio a la gestion requerida")
            for message in messages:
                msg_id = message['id']
                email_info = handler_funtions.validations_and_get_email(self.creds, msg_id=msg_id)
                if email_info['isCorrect']:
                    handler_funtions.send_reply(self.creds, sender_to=email_info['sender_email'],
                                                reply_subject=f"Re: {email_info['subject']}",
                                                reply_body=Modules.handler_variables_email.body_confirmation_validation)
                    print(f"Validacion exitosa, respuesta enviada de atencion de solicitud a: "
                          f"{email_info['sender_email']}")
                    self.gui.update_text("info", f"Validacion exitosa, respuesta enviada de atencion de solicitud a: {email_info['sender_email']}")
                    if email_info['ticket_action'][2] == "ioc":
                        self.management_ioc_csirt(email_info)
                    elif email_info['ticket_action'][2] == "reporte":
                        self.management_report_csirt(email_info)
                else:
                    handler_funtions.send_reply(self.creds, sender_to=email_info['sender_email'],
                                                reply_subject=f"Re: {email_info['subject']}",
                                                reply_body=f"{Modules.handler_variables_email.body_confirmation_invalidation} {email_info['subject']}")
                    print(f"correo fallido: {email_info['subject']}")
                    self.gui.update_text("warning", f"correo fallido: {email_info['subject']}")
                # Se podria dejar un Log con la falla de validacion
                self.gui.update_text("info", "Se marca el correo como leido!")
                print("Se marca el correo como leido!")
                handler_funtions.mark_as_read(self.creds, msg_id=msg_id)
        else:
            self.gui.update_text("info", f"No hay correos nuevos que gestionar, se volverá a revisar en {self.time_wait} seg.")
            print(f"No hay correos nuevos que gestionar, se volverá a revisar en {self.time_wait} seg.")

    def authentication_gmail(self, token_file='Keys\\token.json', key_file=''):
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
            self.gui.update_text("warning", "Se requiere autorización del usuario. Abriendo ventana de autorización...")
            flow = InstalledAppFlow.from_client_secrets_file(key_file, scopes)
            credentials = flow.run_local_server(port=0)
            # Guardar las credenciales en el archivo
            with open(token_file, 'w') as token:
                token.write(credentials.to_json())
            print("Autorización exitosa. Credenciales guardadas.")
            self.gui.update_text("info", "Autorización exitosa. Credenciales guardadas.")

        return credentials
