import requests
import time
from bs4 import BeautifulSoup
import re
from datetime import datetime
import locale

def search_csirt(list_csirt, responsable='', ticket=''):
    max_attempts = 5
    url = "https://csirt.gob.cl/"
    url_list = {'8FPH': [], '2CMV': [], '8FFR': [], '4IIV': [], '4IIA': []}
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
                print(f"Intento {attempts}/{max_attempts}. Esperando 10 segundos antes de volver a intentar...")
                time.sleep(10)  # Esperar 10 segundos antes de intentar nuevamente
                attempts += 1
        else:
            # Si se alcanza el máximo de intentos sin éxito, mostrar un mensaje y continuar con la siguiente página
            print(f"No se pudo obtener la página {page} después de {max_attempts} intentos. Pasando a la siguiente página...")
            continue

        soup = BeautifulSoup(data.text, 'html.parser')
        for i in soup.find_all('div', {'class': 'bg-gradient-to-r to-slate-100 from-white border-gray-200 print:shadow-none shadow-md rounded-lg'}):
            print("-", i)
            try:
                link = i.find('a', href=True)['href'].replace("/alertas", "").upper()
                link = re.search(r'(\d?\w{3}\d{2}-\d+(?:-\d{2})?)', link).group(1)
                date = convert_date(i.find('time', class_='text-md text-gray-400 mb-5').get_text().replace(" ", ""))

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

lista = ['FPH24-00998', 'CMV24-00483', 'FFR24-01697', '4IIA23-00069', '4IIV22-00060-01']

test = search_csirt(lista, 'Alexis', 'RF-0000000')
