import os
from Modules.handler_funtions import authentication_gmail
from Modules.handler_variables_email import format_sheets_csirt
from Modules.gestioncsirt import GestionIoc
from googleapiclient.discovery import build
from tkinter import ttk, filedialog, messagebox
import tkinter as tk
import configparser
import threading
import datetime
import logging
import json

LABELS = {
    "title": "Configuracion",
    "cred_path": "Ruta credenciales:",
    "select_file": "Seleccionar Archivo",
    "domain": "Dominio:",
    "wait_time": "Tiempo de espera (s):",
    "folder_name": "Nombre de la carpeta:",
    "sheet_name": "Nombre de la hoja:"
}


class ConfiguracionVentana(tk.Toplevel):
    def __init__(self, master, configuracion):
        super().__init__(master)
        self.title(LABELS["title"])
        self.resizable(False, False)
        self.attributes('-topmost', 1)

        self.configuracion = configuracion
        self.is_modify = False
        self.change_name_folder = False
        self.change_name_sheet = False

        self.cred_path = None
        self.domain_entry = None
        self.time_wait_entry = None
        self.folder_var = None
        self.folder_name_entry = None
        self.sheet_var = None
        self.sheet_name_entry = None

        self.canvas_csirt = None
        self.scrollable_frame_csirt = None
        self.csirt_entries = {}
        self.csirt_dict = {}
        self.row_csirt = 0

        self.creds = authentication_gmail(key_file=self.configuracion.get('credentials', 'path_key'))

        # Logger
        import logging
        import os
        log_path = os.path.join("Logs", "configuracion.log")
        self.logger = logging.getLogger("configuracion_logger")
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            file_handler = logging.FileHandler(log_path, encoding='utf-8')
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

        self.crear_frame_credenciales()
        self.crear_frame_configuracion_general()
        self.crear_frame_csirt()
        self.crear_botones_accion()
        self.configurar_validaciones()

        self.protocol("WM_DELETE_WINDOW", self.cerrar_ventana)

    def crear_frame_credenciales(self):
        frame = ttk.LabelFrame(self, text="Credenciales")
        frame.grid(row=0, column=0, columnspan=3, padx=10, pady=5, sticky="ew")

        ttk.Label(frame, text=LABELS["cred_path"]).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.cred_path = ttk.Entry(frame, width=50)
        self.cred_path.insert(0, self.configuracion.get('credentials', 'path_key'))
        self.cred_path.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        ttk.Button(frame, text=LABELS["select_file"], command=self.seleccionar_archivo).grid(row=0, column=2, padx=5, pady=5)

        frame.columnconfigure(1, weight=1)

    def crear_frame_configuracion_general(self):
        frame = ttk.LabelFrame(self, text="Parámetros de configuración")
        frame.grid(row=1, column=0, columnspan=3, padx=10, pady=5, sticky="ew")

        ttk.Label(frame, text=LABELS["domain"]).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.domain_entry = ttk.Entry(frame)
        self.domain_entry.insert(0, self.configuracion.get('configurations', 'domain'))
        self.domain_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(frame, text=LABELS["wait_time"]).grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.time_wait_entry = ttk.Spinbox(frame, from_=1, to=9999, increment=1)
        self.time_wait_entry.insert(0, self.configuracion.get('configurations', 'time_wait'))
        self.time_wait_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(frame, text=LABELS["folder_name"]).grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.folder_var = tk.StringVar()
        self.folder_var.set(self.configuracion.get('configurations', 'folder_name'))
        self.folder_var.trace_add("write", lambda *args: self.set_folder_changed())
        self.folder_name_entry = ttk.Entry(frame, textvariable=self.folder_var)
        self.folder_name_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(frame, text=LABELS["sheet_name"]).grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.sheet_var = tk.StringVar()
        self.sheet_var.set(self.configuracion.get('configurations', 'sheet_name'))
        self.sheet_var.trace_add("write", lambda *args: self.set_sheet_changed())
        self.sheet_name_entry = ttk.Entry(frame, textvariable=self.sheet_var)
        self.sheet_name_entry.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

        frame.columnconfigure(1, weight=1)

    def crear_frame_csirt(self):
        import json
        self.labelFrame_csirt_name = ttk.LabelFrame(self, text="Categorías CSIRT")
        self.labelFrame_csirt_name.grid(row=2, column=0, columnspan=3, padx=10, pady=5, sticky="ew")

        self.canvas_csirt = tk.Canvas(self.labelFrame_csirt_name, height=150)
        scrollbar = ttk.Scrollbar(self.labelFrame_csirt_name, orient="vertical", command=self.canvas_csirt.yview)
        self.scrollable_frame_csirt = tk.Frame(self.canvas_csirt)

        self.scrollable_frame_csirt.bind(
            "<Configure>",
            lambda e: self.canvas_csirt.configure(scrollregion=self.canvas_csirt.bbox("all"))
        )

        self.canvas_csirt.create_window((0, 0), window=self.scrollable_frame_csirt, anchor="nw")
        self.canvas_csirt.configure(yscrollcommand=scrollbar.set)
        self.bind_mousewheel_to_canvas(self.canvas_csirt)

        self.canvas_csirt.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')

        self.csirt_entries = {}
        self.csirt_dict = json.loads(self.configuracion.get('configurations', 'csirt_names'))
        self.row_csirt = 0
        self.agregar_campos_csirt_iniciales()

        tk.Button(self.labelFrame_csirt_name, text="+ Agregar categoría", command=self.agregar_campo_csirt)\
            .grid(row=1, column=0, columnspan=2, pady=5)

    def crear_botones_accion(self):
        ttk.Button(self, text="Guardar", command=self.guardar_configuracion).grid(row=3, column=0, pady=10, padx=25)
        ttk.Button(self, text="Cancelar", command=self.cancelar_configuracion).grid(row=3, column=1, pady=10, padx=25)

    def configurar_validaciones(self):
        self.domain_entry.bind("<FocusOut>", self.validate_entry_out)
        self.time_wait_entry.bind("<FocusOut>", self.validate_entry_out)
        self.domain_entry.bind("<FocusIn>", self.validate_entry_in)
        self.time_wait_entry.bind("<FocusIn>", self.validate_entry_in)
        self.folder_name_entry.bind("<FocusIn>", self.validate_entry_in)
        self.sheet_name_entry.bind("<FocusIn>", self.validate_entry_in)

    def bind_mousewheel_to_canvas(self, canvas):
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def _on_mousewheel_linux(event):  # Para sistemas X11 (Linux)
            canvas.yview_scroll(-1 if event.num == 4 else 1, "units")

        if self.tk.call("tk", "windowingsystem") == "win32":
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
        elif self.tk.call("tk", "windowingsystem") == "aqua":  # macOS
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
        else:  # Linux (usa <Button-4> y <Button-5>)
            canvas.bind_all("<Button-4>", _on_mousewheel_linux)
            canvas.bind_all("<Button-5>", _on_mousewheel_linux)

    def agregar_campos_csirt_iniciales(self):
        for key, values in self.csirt_dict.items():
            self.agregar_campo_csirt(key, values)

    def agregar_campo_csirt(self, key="", value=""):
        key_var = tk.StringVar(value=key)
        value_var = tk.StringVar(value=value)

        key_entry = tk.Entry(self.scrollable_frame_csirt, textvariable=key_var, width=7)
        key_entry.grid(row=self.row_csirt, column=0, padx=5, pady=2)

        value_entry = tk.Entry(self.scrollable_frame_csirt, textvariable=value_var, width=30)
        value_entry.grid(row=self.row_csirt, column=1, padx=5, pady=2)

        delete_button = tk.Button(
            self.scrollable_frame_csirt,
            text="❌",
            command=lambda r=self.row_csirt: self.eliminar_campo_csirt(r),
            relief="flat",
            fg="red"
        )

        delete_button.grid(row=self.row_csirt, column=2, padx=5, pady=2)

        self.csirt_entries[self.row_csirt] = {
            'key_var': key_var,
            'value_var': value_var,
            'widgets': [key_entry, value_entry, delete_button]
        }
        self.row_csirt += 1

    def eliminar_campo_csirt(self, row_id):
        entry_data = self.csirt_entries.pop(row_id, None)
        if entry_data:
            for widget in entry_data['widgets']:
                widget.destroy()

    def cerrar_ventana(self):
        self.attributes('-topmost', 0)  # Restablecer el valor para permitir que la ventana principal quede por encima
        self.destroy()

    def guardar_configuracion(self):
        # try:
        import json

        self.logger.info("Se inició el guardado de la configuración.")

        if self.change_name_folder:
            self.logger.info(f"Cambio de nombre de carpeta detectado: {self.folder_var.get()}")
            self.change_name_file_folder(self.folder_var.get(),
                                         self.configuracion.get('configurations', 'folder_id'))
        if self.change_name_sheet:
            self.logger.info(f"Cambio de nombre de hoja detectado: {self.sheet_var.get()}")
            self.change_name_file_folder(self.sheet_var.get(),
                                         self.configuracion.get('configurations', 'sheet_id'))

        # Guarda los cambios en la configuración
        self.configuracion.set('credentials', 'path_key', self.cred_path.get())
        self.logger.info(f"Ruta de credenciales actualizada: {self.cred_path.get()}")
        self.configuracion.set('configurations', 'domain', self.domain_entry.get())
        self.logger.info(f"Dominio actualizado: {self.domain_entry.get()}")
        self.configuracion.set('configurations', 'time_wait', self.time_wait_entry.get())
        self.logger.info(f"Tiempo de espera actualizado: {self.time_wait_entry.get()}")
        self.configuracion.set('configurations', 'folder_name', self.folder_name_entry.get())
        self.logger.info(f"Nombre de la carpeta actualizado: {self.folder_name_entry.get()}")
        self.configuracion.set('configurations', 'sheet_name', self.sheet_name_entry.get())
        self.logger.info(f"Nombre de la hoja actualizado: {self.sheet_name_entry.get()}")


        # === Armar nuevo diccionario csirt_names ===
        nuevo_csirt = dict()
        for entry in self.csirt_entries.values():
            key = entry['key_var'].get().strip()
            value = entry['value_var'].get().strip()
            if key and value:
                nuevo_csirt[key] = value
        if set(self.csirt_dict.keys()) != set(nuevo_csirt.keys()):
            self.logger.info("Cambios en CSIRT detectados. Sincronizando hojas...")
            sheet_id = self.configuracion.get('configurations', 'sheet_id')
            self.sincronizar_hojas(self.csirt_dict, nuevo_csirt, sheet_id)
            # Guardar diccionario como string JSON en el archivo cfg
            self.configuracion.set('configurations', 'csirt_names', json.dumps(nuevo_csirt, ensure_ascii=False))


        # Guarda la configuración en el archivo
        with open('Config\\configuration.cfg', 'w') as config_file:
            self.configuracion.write(config_file)
        self.logger.info("Configuración guardada correctamente en 'configuration.cfg'.")

        # Cierra la ventana
        self.cerrar_ventana()

    def sincronizar_hojas(self, old_csirt, new_csirt, sheet_id):
        hojas_actuales = self.obtener_nombres_hojas(sheet_id)

        claves_antiguas = set(old_csirt.keys())
        claves_nuevas = set(new_csirt.keys())

        claves_eliminadas = claves_antiguas - claves_nuevas
        claves_agregadas = claves_nuevas - claves_antiguas

        # === Eliminar hojas ===
        requests_eliminar = []
        for clave in claves_eliminadas:
            if clave in hojas_actuales:
                sheet_id_to_delete = hojas_actuales[clave]
                requests_eliminar.append({'deleteSheet': {'sheetId': sheet_id_to_delete}})

        sheet_service = build('sheets', 'v4', credentials=self.creds)

        if requests_eliminar:
            sheet_service.spreadsheets().batchUpdate(
                spreadsheetId=sheet_id,
                body={'requests': requests_eliminar}
            ).execute()
            print(f"🗑️ Hojas eliminadas: {', '.join(claves_eliminadas)}")

        # === Agregar hojas con formato ===
        for clave in claves_agregadas:
            valor = new_csirt[clave]
            self.agregar_hoja_y_formato(sheet_service, sheet_id, clave, valor)

    def agregar_hoja_y_formato(self, sheet_service, spreadsheet_id, clave, valor):
        # Paso 1: Crear hoja
        add_sheet_body = {
            'requests': [
                {'addSheet': {'properties': {'title': clave}}}
            ]
        }

        result = sheet_service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body=add_sheet_body
        ).execute()

        sheet_id = result['replies'][0]['addSheet']['properties']['sheetId']

        # Paso 2: Aplicar formato con el valor correspondiente
        format_requests = format_sheets_csirt(sheet_id, valor)
        sheet_service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={'requests': format_requests}
        ).execute()

        print(f"✅ Hoja '{clave}' creada y formateada.")

    def obtener_nombres_hojas(self, sheet_id):
        sheet_service = build('sheets', 'v4', credentials=self.creds)
        sheet_metadata = sheet_service.spreadsheets().get(spreadsheetId=sheet_id).execute()
        sheets = sheet_metadata.get('sheets', [])
        return {sheet['properties']['title']: sheet['properties']['sheetId'] for sheet in sheets}

    def cancelar_configuracion(self):
        if self.is_modify:
            response = messagebox.askyesno("Cancelar Cambios", "¿Desea salir sin guardar los cambios?", parent=self)
            if response:
                self.logger.info("Cambios cancelados por el usuario.")
                self.cerrar_ventana()
        else:
            self.logger.info("Ventana de configuración cerrada sin cambios.")
            self.cerrar_ventana()

    def seleccionar_archivo(self):
        self.attributes('-topmost', 0)
        ruta_archivo = filedialog.askopenfilename(title="Seleccionar archivo")
        self.attributes('-topmost', 1)
        if not ruta_archivo:
            return
        if self.cred_path.get() != ruta_archivo:
            self.is_modify = True
        self.cred_path.delete(0, tk.END)
        self.cred_path.insert(0, ruta_archivo)

    def validate_entry_out(self, event):
        if self.copy_entry != event.widget.get():
            self.is_modify = True
        if event.widget.winfo_name() == "!spinbox":
            if int(event.widget.get()) > 9999:
                self.time_wait_entry.delete(0, tk.END)
                self.time_wait_entry.insert(0, "9999")

    def set_folder_changed(self):
        self.change_name_folder = True

    def set_sheet_changed(self):
        self.change_name_sheet = True

    def validate_entry_in(self, event):
        self.copy_entry = event.widget.get()

    def change_name_file_folder(self, name, fileid):
        drive_service = build('drive', 'v3', credentials=self.creds)
        drive_service.files().get(fileId=fileid).execute()
        drive_service.files().update(fileId=fileid, body={'name': name}).execute()


class MiApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Interfaz de Control")
        self.root.resizable(False, False)
        self.threading_csirt = False

        self.logger = None
        self.thread = None
        self.start_service = None
        self.configuracion = None

        # Configuración
        self.cargar_configuracion()

        # Menú en cascada
        self.menu_bar = tk.Menu(root)
        self.root.config(menu=self.menu_bar)

        self.config_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.config_menu.add_command(label="Ver Configuración", command=self.ver_configuracion)
        self.config_menu.add_command(label="Configuración", command=self.abrir_ventana_configuracion)
        self.config_menu.add_separator()
        self.config_menu.add_command(label="Salir", command=self.on_closing)

        self.menu_bar.add_cascade(label="Menú", menu=self.config_menu)

        self.manager_logging()

        titulo = ttk.Label(self.root, text="Gestion Alerta Csirt", font=("Helvetica", 20))
        titulo.pack(side=tk.TOP, anchor="n", padx=5, pady=5)

        # Frame para organizar los LabelFrame
        frame_general_top = ttk.Frame(self.root)
        frame_general_top.pack(fill="both")
        frame_general_bottom = ttk.Frame(self.root)
        frame_general_bottom.pack(fill="both")

        labelframe_top = ttk.LabelFrame(frame_general_top, text="Service Manager")
        labelframe_bottom = ttk.LabelFrame(frame_general_bottom, text="Logs")

        # Botones
        self.btn_iniciar = ttk.Button(labelframe_top, text="Start Service", padding="10 8 10 8",
                                      command=self.iniciar_script)
        self.btn_iniciar.pack(side='left', pady=5, padx=50)

        self.btn_detener = ttk.Button(labelframe_top, text="Stop Service", padding="10 8 10 8", state="disabled",
                                      command=self.detener_script)
        self.btn_detener.pack(side='left', pady=5, padx=50)

        # Caja de texto para logs
        self.log_text = tk.Text(labelframe_bottom, state='disabled', height=10, width=50)
        self.log_text.pack(padx=10, pady=10)

        labelframe_top.pack(fill="both", expand=True, padx=5, ipady=3)
        labelframe_bottom.pack(fill="both", expand=True, padx=5, ipady=3)

    def cargar_configuracion(self):
        config_path = os.path.join("Config", "configuration.cfg")
        if not os.path.exists(config_path):
            messagebox.showerror("Error", f"No se encontró el archivo de configuración en:\n{config_path}")
            self.root.destroy()
            return
        self.configuracion = configparser.ConfigParser()
        self.configuracion.read(config_path)

    def obtener_configuracion_formateada(self):
        output = []
        for section in sorted(self.configuracion.sections()):
            output.append("=" * 50)
            output.append(f"📂 Sección: [{section.upper()}]")
            output.append("-" * 50)
            for key in sorted(self.configuracion[section]):
                value = self.configuracion.get(section, key)
                # Mostrar csirt_names como lista legible si es JSON válido
                if key == "csirt_names":
                    try:
                        csirt_dict = json.loads(value)
                        output.append(f"{key} :")
                        for k, v in csirt_dict.items():
                            output.append(f"   • {k} → {v}")
                    except json.JSONDecodeError:
                        output.append(f"{key:<15} : {value}")
                else:
                    output.append(f"{key:<15} : {value}")
            output.append("")  # Línea vacía entre secciones
        return "\n".join(output)

    def ver_configuracion(self):
        # Muestra la configuración actual en una ventana de mensaje
        messagebox.showinfo("Configuración", self.obtener_configuracion_formateada())

    def abrir_ventana_configuracion(self):
        # Abre la ventana de configuración
        ConfiguracionVentana(self.root, self.configuracion)

    def iniciar_script(self):
        """Inicia el servicio de gestión de IoC en un hilo separado."""
        self.update_text("info", "Iniciando el script...")
        self.start_service = threading.Thread(target=self.script_paralelo)
        self.start_service.start()

    def detener_script(self):
        """Detiene el servicio de gestión de IoC."""
        self.update_text("info", "Deteniendo el script")
        self.threading_csirt = False
        try:
            self.thread.stop()
            self.thread.join()
        except Exception as e:
            self.logger.warning(f"No se pudo detener el hilo: {e}")

        self.btn_iniciar.config(state='normal')
        self.btn_detener.config(state='disabled')
        self.config_menu.entryconfig("Configuración", state="normal")

    def script_paralelo(self):
        # Simulación de un script en ejecución
        self.btn_iniciar.config(state="disabled")
        self.btn_detener.config(state="normal")
        self.config_menu.entryconfig("Configuración", state="disabled")

        # Crear e iniciar el hilo
        self.thread = GestionIoc(self.configuracion, self)
        self.thread.start()
        self.threading_csirt = True

    def _update_text(self, level_log, message, is_error):
        self.log_text.config(state='normal')
        datetime_current = datetime.datetime.now()
        self.log_text.insert(tk.END, f"{datetime_current.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")
        self.log_text.yview(tk.END)  # Desplazar la caja de texto para mostrar el último registro
        self.log_text.config(state='disabled')

        try:
            if level_log.lower() == "info":
                self.logger.info(message)
            elif level_log.lower() == "warning":
                self.logger.warning(message)
            elif level_log.lower() == "error":
                self.logger.error(message)
        except Exception as e:
            print(f"Error al escribir en el log: {e}")

        if is_error:
            self.detener_script()

    def update_text(self, level_log, message, is_error=False):
        # Esta función utiliza after() para ejecutar la actualización en el hilo principal
        self.root.after(0, self._update_text, level_log, message, is_error)

    def manager_logging(self):
        # Configuración del logger principal
        self.logger = logging.getLogger('main')
        self.logger.setLevel(logging.INFO)

        # Crear formateador para los registros
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        # Crear manejador para el archivo de registros de nivel DEBUG
        info_handler = logging.FileHandler(os.path.join('Logs', 'main.log'))
        info_handler.setLevel(logging.INFO)
        info_handler.setFormatter(formatter)
        self.logger.addHandler(info_handler)

    def on_closing(self):
        if self.threading_csirt:
            messagebox.showwarning("Aviso", "Detén el servicio antes de cerrar la aplicación.")
            return
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = MiApp(root)
    root.mainloop()
