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