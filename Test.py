import configparser
import os
import json

root_path = os.path.dirname(os.path.abspath(__file__))

def crear_configuracion(root_path, config_cfg):
    ruta_archivo_cfg = os.path.join(root_path, 'Config', "configuration_test.cfg")
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
                                            'csirt_names': json.dumps(csirt_mapping, ensure_ascii=False)
                                            }

            with open(ruta_archivo_cfg, "w") as configfile:
                config_cfg.write(configfile)

            print(f"Archivo '{ruta_archivo_cfg}' creado correctamente.")

            return ruta_archivo_cfg
        else:
            print(f"El archivo '{ruta_archivo_cfg}' ya existe.")
            return ruta_archivo_cfg

    except Exception as e:
        print(f"Error al crear el archivo .cfg: {e}")

def prueba_google_sheet(sheet_name, config_cfg):
    spreadsheet_body = {
        'properties': {'title': sheet_name},
        'sheets': [
            {'properties': {'title': name}} for name in config_cfg.keys()
        ]
    }

    print(spreadsheet_body)

config = configparser.ConfigParser()

ruta_archivo_cfg = os.path.join(root_path, 'Config', "configuration_test.cfg")

#crear_configuracion(root_path, config)

config.read(ruta_archivo_cfg)

csirt_name = json.loads(config['configurations']['csirt_names'])

#prueba_google_sheet('test', csirt_name)

lista = ['8FPH', '2CMV', '8FFR', '4IIA', '4IIV', 'ACF', 'AIA']

for i in lista:
    print(csirt_name[i])



