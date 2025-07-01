import configparser
import locale
import os
import re
import requests
import json
import time
from datetime import datetime

from bs4 import BeautifulSoup

"""root_path = os.path.dirname(os.path.abspath(__file__))

config = configparser.ConfigParser()

ruta_archivo_cfg = os.path.join(root_path, 'Config', "configuration_backup.cfg")

config.read(ruta_archivo_cfg)

def search_csirt(list_csirt, csirt_name, responsable='', ticket=''):
    max_attempts = 5
    url = "https://www.csirt.gob.cl/"

    url_list = {i: [] for i in csirt_name}

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
                #gui.update_text("error", f"Error al obtener la página {page}: {e}")
                print(f"Intento {attempts}/{max_attempts}. Esperando 10 segundos antes de volver a intentar...")
                time.sleep(10)  # Esperar 10 segundos antes de intentar nuevamente
                attempts += 1
        else:
            # Si se alcanza el máximo de intentos sin éxito, mostrar un mensaje y continuar con la siguiente página
            #gui.update_text("error", f"No se pudo obtener la página {page} después de {max_attempts} intentos. Pasando a la siguiente página...")
            print(f"No se pudo obtener la página {page} después de {max_attempts} intentos. Pasando a la siguiente página...")
            continue

        soup = BeautifulSoup(data.text, 'html.parser')
        for i in soup.find_all('a', href=lambda x: x and x.startswith('/alertas/')):
            if not i.find('picture'):
                try:
                    link = i.find('h3').get_text().upper()
                    date = convert_date(i.find('time').get_text().replace(" ", ""))
                    print(link.lower())
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
        return None"""



#csirt_name = json.loads(config['configurations']['csirt_names'])
old_csirt = {'8FPH': 'Alerta', '2CMV': 'Alerta', '8FFR': 'Alerta', '4IIA': 'Alerta', '4IIV': 'Alerta', 'ACF': 'acf25-00047', 'AIA': 'aia25-00004'}
new_csirt = {'8FPH': 'Alerta', '2CMV': 'Alerta', '8FFR': 'Alerta', '4IIA': 'Alerta', '4IIV': 'Alerta', 'ACF': 'acf25-00047', 'AIA': 'aia25-00004', 'test': 'test'}

if set(old_csirt.keys()) == set(new_csirt.keys()):
    print("Las claves son iguales")
else:
    print("Las claves son diferentes")


#resultado = search_csirt(last_csirt, csirt_name, "Alexis Aguilera", "RF-000000")

#print(resultado)

"""resultado = {'8FPH': [], '2CMV': [], '8FFR': [], '4IIA': [], '4IIV': [], 'ACF': [{'name': 'ACF25-00001', 'revision': '0', 'responsible': 'Alexis Aguilera', 'date': '23/04/2025', 'Ticket': 'Ticket padre RF-000000', 'Gestionado': ''}, {'name': 'ACF25-00002', 'revision': '0', 'responsible': 'Alexis Aguilera', 'date': '23/04/2025', 'Ticket': 'Ticket padre RF-000000', 'Gestionado': ''}, {'name': 'ACF25-00003', 'revision': '0', 'responsible': 'Alexis Aguilera', 'date': '22/04/2025', 'Ticket': 'Ticket padre RF-000000', 'Gestionado': ''}, {'name': 'ACF25-00005', 'revision': '0', 'responsible': 'Alexis Aguilera', 'date': '23/04/2025', 'Ticket': 'Ticket padre RF-000000', 'Gestionado': ''}, {'name': 'ACF25-00006', 'revision': '0', 'responsible': 'Alexis Aguilera', 'date': '23/04/2025', 'Ticket': 'Ticket padre RF-000000', 'Gestionado': ''}, {'name': 'ACF25-00007', 'revision': '0', 'responsible': 'Alexis Aguilera', 'date': '25/04/2025', 'Ticket': 'Ticket padre RF-000000', 'Gestionado': ''}, {'name': 'ACF25-00008', 'revision': '0', 'responsible': 'Alexis Aguilera', 'date': '29/04/2025', 'Ticket': 'Ticket padre RF-000000', 'Gestionado': ''}, {'name': 'ACF25-00009', 'revision': '0', 'responsible': 'Alexis Aguilera', 'date': '30/04/2025', 'Ticket': 'Ticket padre RF-000000', 'Gestionado': ''}, {'name': 'ACF25-00010', 'revision': '0', 'responsible': 'Alexis Aguilera', 'date': '02/05/2025', 'Ticket': 'Ticket padre RF-000000', 'Gestionado': ''}, {'name': 'ACF25-00011', 'revision': '0', 'responsible': 'Alexis Aguilera', 'date': '02/05/2025', 'Ticket': 'Ticket padre RF-000000', 'Gestionado': ''}, {'name': 'ACF25-00012', 'revision': '0', 'responsible': 'Alexis Aguilera', 'date': '06/05/2025', 'Ticket': 'Ticket padre RF-000000', 'Gestionado': ''}, {'name': 'ACF25-00013', 'revision': '0', 'responsible': 'Alexis Aguilera', 'date': '06/05/2025', 'Ticket': 'Ticket padre RF-000000', 'Gestionado': ''}, {'name': 'ACF25-00014', 'revision': '0', 'responsible': 'Alexis Aguilera', 'date': '07/05/2025', 'Ticket': 'Ticket padre RF-000000', 'Gestionado': ''}, {'name': 'ACF25-00015', 'revision': '0', 'responsible': 'Alexis Aguilera', 'date': '07/05/2025', 'Ticket': 'Ticketpadre RF-000000', 'Gestionado': ''}, {'name': 'ACF25-00016', 'revision': '0', 'responsible': 'Alexis Aguilera', 'date': '07/05/2025', 'Ticket': 'Ticket padre RF-000000', 'Gestionado': ''}, {'name': 'ACF25-00017', 'revision': '0', 'responsible': 'Alexis Aguilera', 'date': '12/05/2025', 'Ticket': 'Ticket padre RF-000000', 'Gestionado': ''}, {'name': 'ACF25-00018', 'revision': '0', 'responsible': 'Alexis Aguilera', 'date': '12/05/2025', 'Ticket': 'Ticket padre RF-000000', 'Gestionado': ''}, {'name': 'ACF25-00019', 'revision': '0', 'responsible': 'Alexis Aguilera', 'date': '12/05/2025', 'Ticket': 'Ticket padre RF-000000', 'Gestionado': ''}, {'name': 'ACF25-00020', 'revision': '0', 'responsible': 'Alexis Aguilera','date': '07/05/2025', 'Ticket': 'Ticket padre RF-000000', 'Gestionado': ''}, {'name': 'ACF25-00021', 'revision': '0', 'responsible': 'Alexis Aguilera', 'date': '12/05/2025', 'Ticket': 'Ticket padre RF-000000', 'Gestionado': ''}, {'name': 'ACF25-00022', 'revision': '0', 'responsible': 'Alexis Aguilera', 'date': '05/05/2025', 'Ticket': 'Ticket padre RF-000000', 'Gestionado': ''}, {'name': 'ACF25-00023', 'revision': '0', 'responsible': 'Alexis Aguilera', 'date': '13/05/2025', 'Ticket': 'Ticket padre RF-000000', 'Gestionado': ''}, {'name': 'ACF25-00024', 'revision': '0', 'responsible': 'Alexis Aguilera', 'date': '19/05/2025', 'Ticket': 'Ticket padre RF-000000', 'Gestionado': ''}, {'name': 'ACF25-00025', 'revision': '0', 'responsible': 'Alexis Aguilera', 'date': '19/05/2025', 'Ticket': 'Ticket padre RF-000000', 'Gestionado': ''}, {'name': 'ACF25-00026', 'revision': '0', 'responsible': 'Alexis Aguilera', 'date': '22/05/2025', 'Ticket': 'Ticket padre RF-000000', 'Gestionado': ''}, {'name': 'ACF25-00027', 'revision': '0', 'responsible': 'Alexis Aguilera', 'date': '22/05/2025', 'Ticket': 'Ticket padre RF-000000', 'Gestionado': ''}, {'name': 'ACF25-00028', 'revision': '0', 'responsible': 'Alexis Aguilera', 'date': '22/05/2025', 'Ticket': 'Ticket padre RF-000000', 'Gestionado': ''}, {'name': 'ACF25-00029', 'revision': '0', 'responsible': 'Alexis Aguilera', 'date': '22/05/2025', 'Ticket': 'Ticket padre RF-000000', 'Gestionado':''}, {'name': 'ACF25-00030', 'revision': '0', 'responsible': 'Alexis Aguilera', 'date': '23/05/2025', 'Ticket': 'Ticket padre RF-000000', 'Gestionado': ''}, {'name': 'ACF25-00031', 'revision': '0', 'responsible': 'Alexis Aguilera', 'date': '26/05/2025', 'Ticket': 'Ticket padre RF-000000', 'Gestionado': ''}, {'name': 'ACF25-00032', 'revision': '0', 'responsible': 'Alexis Aguilera', 'date': '26/05/2025', 'Ticket': 'Ticket padre RF-000000', 'Gestionado': ''}, {'name': 'ACF25-00033', 'revision': '0', 'responsible': 'Alexis Aguilera', 'date': '26/05/2025', 'Ticket': 'Ticket padre RF-000000', 'Gestionado': ''}, {'name': 'ACF25-00034', 'revision': '0', 'responsible': 'Alexis Aguilera', 'date': '26/05/2025', 'Ticket':'Ticket padre RF-000000', 'Gestionado': ''}, {'name': 'ACF25-00035', 'revision': '0', 'responsible': 'Alexis Aguilera', 'date': '30/05/2025', 'Ticket': 'Ticket padre RF-000000', 'Gestionado': ''}, {'name': 'ACF25-00036', 'revision': '0', 'responsible': 'Alexis Aguilera', 'date': '02/06/2025', 'Ticket': 'Ticket padre RF-000000', 'Gestionado': ''}, {'name': 'ACF25-00037', 'revision': '0', 'responsible': 'Alexis Aguilera', 'date': '02/06/2025', 'Ticket': 'Ticket padre RF-000000', 'Gestionado': ''}, {'name': 'ACF25-00038', 'revision': '0', 'responsible': 'Alexis Aguilera', 'date': '02/06/2025', 'Ticket': 'Ticket padre RF-000000', 'Gestionado': ''}, {'name': 'ACF25-00039', 'revision': '0', 'responsible': 'Alexis Aguilera', 'date': '03/06/2025', 'Ticket': 'Ticket padre RF-000000', 'Gestionado': ''}, {'name': 'ACF25-00040', 'revision': '0', 'responsible': 'Alexis Aguilera', 'date': '03/06/2025', 'Ticket': 'Ticket padre RF-000000', 'Gestionado': ''}, {'name': 'ACF25-00041', 'revision': '0', 'responsible': 'Alexis Aguilera', 'date': '05/06/2025', 'Ticket': 'Ticket padre RF-000000', 'Gestionado': ''}, {'name': 'ACF25-00042', 'revision': '0', 'responsible': 'Alexis Aguilera', 'date': '09/06/2025', 'Ticket': 'Ticket padre RF-000000', 'Gestionado': ''}, {'name': 'ACF25-00043', 'revision': '0', 'responsible': 'Alexis Aguilera', 'date': '10/06/2025', 'Ticket': 'Ticket padre RF-000000', 'Gestionado': ''}, {'name': 'ACF25-00044', 'revision': '0', 'responsible': 'Alexis Aguilera', 'date': '10/06/2025', 'Ticket': 'Ticket padre RF-000000', 'Gestionado': ''}, {'name': 'ACF25-00045', 'revision': '0', 'responsible': 'Alexis Aguilera', 'date': '10/06/2025', 'Ticket': 'Ticket padre RF-000000', 'Gestionado': ''}, {'name': 'ACF25-00046', 'revision': '0', 'responsible': 'Alexis Aguilera', 'date':'18/06/2025', 'Ticket': 'Ticket padre RF-000000', 'Gestionado': ''}, {'name': 'ACF25-00047', 'revision': '0', 'responsible': 'Alexis Aguilera', 'date': '23/06/2025', 'Ticket': 'Ticket padre RF-000000', 'Gestionado': ''}, {'name': 'ACF25-00048', 'revision': '0', 'responsible': 'Alexis Aguilera', 'date': '25/06/2025', 'Ticket': 'Ticket padre RF-000000', 'Gestionado': ''}, {'name': 'ACF25-00049', 'revision': '0', 'responsible': 'Alexis Aguilera', 'date': '26/06/2025', 'Ticket': 'Ticket padre RF-000000', 'Gestionado': ''}, {'name': 'ACF25-00050', 'revision': '0', 'responsible': 'Alexis Aguilera', 'date': '26/06/2025', 'Ticket': 'Ticket padre RF-000000', 'Gestionado': ''}], 'AIA': [{'name': 'AIA25-00002', 'revision': '0', 'responsible': 'Alexis Aguilera', 'date': '21/04/2025', 'Ticket': 'Ticket padre RF-000000', 'Gestionado': ''}, {'name': 'AIA25-00003', 'revision': '0', 'responsible': 'Alexis Aguilera', 'date': '24/04/2025', 'Ticket': 'Ticket padre RF-000000', 'Gestionado': ''}, {'name': 'AIA25-00004', 'revision': '0', 'responsible': 'Alexis Aguilera', 'date': '30/05/2025', 'Ticket': 'Ticket padre RF-000000', 'Gestionado': ''}, {'name': 'AIA25-00005', 'revision': '0', 'responsible': 'Alexis Aguilera', 'date': '09/06/2025', 'Ticket': 'Ticket padre RF-000000', 'Gestionado': ''}, {'name': 'AIA25-00006', 'revision': '0', 'responsible': 'Alexis Aguilera', 'date': '12/06/2025', 'Ticket': 'Ticket padre RF-000000', 'Gestionado': ''}, {'name': 'AIA25-00007', 'revision': '0', 'responsible': 'Alexis Aguilera', 'date': '27/06/2025', 'Ticket': 'Ticket padre RF-000000', 'Gestionado': ''}]}

for i in resultado[('AIA')]:
    print(i)"""


print(new_csirt.keys())
