import configparser
import textwrap
import os


config_path = os.path.join("Config", "configuration.cfg")
configuracion = configparser.ConfigParser()
configuracion.read(config_path)

URL_SHEET = configuracion.get("configurations", "sheet_url")
URL_SHARE_FOLDER = configuracion.get("configurations", "url_folder")

body_messages = {
    "validation": "Se ha comenzado a gestionar las nuevas alertas CSIRT, una vez finalizada se mandará correo con las nuevas alertas.",
    "invalidation": (
        "No se ha podido atender tu consulta 'Asunto enviado incorrectamente EJ: [RF-0000000] ioc csirt o [RF-0000000] "
        "reporte csirt, asunto enviado: "
    ),
    "no_alerts": "No hay nuevas alertas CSIRT.<br>",
    "send_alert": "Se ha concluido gestion de alertas CSIRT: <br>",
    "link_sheet": "Para ver la planilla con las alertas gestionadas, puedes acceder al siguiente link:<br>",
    "ioc": (
        "<br><br><h3>IoC:</h3>Para ver los IoC de las ultimas alertas gestionadas, ingresar al siguiente link y "
        "buscar el archivo con el mismo nombre del numero de ticket ingresado:<br>"
    ),
    "send_report": (
        "Hago entrega de las alertas CSIRT procesadas en la última semana. Gestión realizada por Sonda al día de hoy."
    )
}

style_html = textwrap.dedent("""
    <style>
      table {
        border-collapse: collapse;
        width: 100%;
      }

      th, td {
        border: 1px solid #dddddd;
        text-align: center;
        padding: 8px;
      }

      th {
        background-color: #3498db;
        color: white;
        font-weight: bold;
      }

      tr:nth-child(even) {
        background-color: #f2f2f2;
      }

      tr:hover {
        background-color: #d3d3d3;
      }
    </style>
""")


def format_sheets_csirt(sheet_id, values):
    """
    :param sheet_id: ID de la hoja de google dri
    :param values: Descripcion de la alerta csirt
    :return: Lista de peticiones de formato para Google Sheets API
    """
    def cell_format(bg, fg=(0, 0, 0), size=11, bold=True):
        return {
            'backgroundColor': {'red': bg[0], 'green': bg[1], 'blue': bg[2]},
            'textFormat': {
                'foregroundColor': {'red': fg[0], 'green': fg[1], 'blue': fg[2]},
                'fontFamily': 'Calibri',
                'fontSize': size,
                'bold': bold
            },
            'horizontalAlignment': 'CENTER',
            'borders': {
                side: {'style': 'SOLID', 'width': 2, 'color': {'red': 0, 'green': 0, 'blue': 0}}
                for side in ('bottom', 'top', 'left', 'right')
            }
        }

    merge_and_format_requests = [
        # Merge título
        {'mergeCells': {'mergeType': 'MERGE_ROWS', 'range': {
            'sheetId': sheet_id, 'startRowIndex': 0, 'endRowIndex': 1,
            'startColumnIndex': 0, 'endColumnIndex': 6}}},
        {'updateCells': {
            'rows': [{'values': [{'userEnteredFormat': cell_format((1, 0, 0), (1, 1, 1), 20),
                                  'userEnteredValue': {'stringValue': 'Alertas CSIRT'}}]}],
            'fields': '*',
            'start': {'sheetId': sheet_id, 'rowIndex': 0, 'columnIndex': 0}}},

        # Merge subtítulo
        {'mergeCells': {'mergeType': 'MERGE_ROWS', 'range': {
            'sheetId': sheet_id, 'startRowIndex': 1, 'endRowIndex': 2,
            'startColumnIndex': 0, 'endColumnIndex': 6}}},
        {'updateCells': {
            'rows': [{'values': [{'userEnteredFormat': cell_format((1, 1, 0), (0, 0, 0), 16),
                                  'userEnteredValue': {'stringValue': values}}]}],
            'fields': '*',
            'start': {'sheetId': sheet_id, 'rowIndex': 1, 'columnIndex': 0}}},

        # Encabezados fila 3
        {'updateCells': {
            'rows': [{
                'values': [
                    {'userEnteredFormat': cell_format((0.7176, 0.8824, 0.8039)), 'userEnteredValue': {'stringValue': txt}}
                    for txt in ["Alerta", "Revision", "Responsable", "Fecha de realizacion", "Tickets", "Gestionado"]
                ]}],
            'fields': '*',
            'start': {'sheetId': sheet_id, 'rowIndex': 2, 'columnIndex': 0}}},
    ]

    # Definir anchos de columna
    widths = [120, 60, 230, 130, 85, 80]
    for i, width in enumerate(widths):
        merge_and_format_requests.append({
            'updateDimensionProperties': {
                'range': {'sheetId': sheet_id, 'dimension': 'COLUMNS', 'startIndex': i, 'endIndex': i + 1},
                'properties': {'pixelSize': width},
                'fields': 'pixelSize'
            }
        })

    return merge_and_format_requests
