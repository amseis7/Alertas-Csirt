URL_SHEET = (
    'https://docs.google.com/spreadsheets/d/1yqrywMnuFSQDuT45dATTspwEHHa9IkTZqtjbtg6rhqs/edit?pli=1#gid=111678972'
)
URL_SHARE_FOLDER = "https://drive.google.com/drive/folders/1MavZZCLtgeaLWsJ2x7LCD8vPM2cXpkT5?usp=sharing"
body_confirmation_validation = (
    "Se ha comenzado a gestionar las nuevas alertas CSIRT, una vez finalizada se mandará correo con las nuevas alertas."
)
body_confirmation_invalidation = (
    "No se ha podido atender tu consulta 'Asunto enviado incorrectamente EJ: [RF-0000000] ioc csirt o [RF-0000000] "
    "reporte csirt, asunto enviado: "
)
body_not_new_alerts = (
    f"No hay nuevas alertas CSIRT.<br>"
)
body_send_alert = "Se ha concluido gestion de alertas CSIRT: <br>"
body_link_sheet = f"Para ver la planilla con las alertas gestionadas, puedes acceder al siguiente link:<br>"
body_ioc = (f"<br><br><h3>IoC:</h3>Para ver los IoC de las ultimas alertas gestionadas, ingresar al siguiente link y "
            f"buscar el archivo con el mismo nombre del numero de ticket ingresado:<br>")
body_send_report = ("Hago entrega de las alertas CSIRT procesadas en la última semana. Gestión realizada por Sonda al "
                    "día de hoy.")
style_html = """
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
"""

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
