from Modules.handler_funtions import authentication_gmail
from Modules.gestioncsirt import GestionIoc
from googleapiclient.discovery import build
from tkinter import messagebox
from tkinter import filedialog
from tkinter import ttk
import tkinter as tk
import configparser
import threading
import datetime
import logging


class ConfiguracionVentana(tk.Toplevel):
    def __init__(self, master, configuracion):
        super().__init__(master)
        self.title("Configuración")
        self.resizable(False, False)
        self.is_modify = False
        self.configuracion = configuracion
        self.change_name_folder = False
        self.change_name_sheet = False

        # Etiqueta y entrada para la configuracion de la key de Google
        tk.Label(self, text="Ruta credencial: ").grid(sticky='w', row=0, column=0, padx=10, pady=5)
        self.cred_path = tk.Entry(self)
        self.cred_path.insert(0, self.configuracion.get('credentials', 'path_key'))
        self.cred_path.grid(sticky='ew', row=0, column=1, padx=10, pady=5)
        self.boton_seleccionar = tk.Button(self, text="Seleccionar Archivo", command=self.seleccionar_archivo)
        self.boton_seleccionar.grid(row=0, column=2, padx=10, pady=5)

        # Etiqueta y entrada para la configuración del dominio
        tk.Label(self, text="Dominio:").grid(sticky='w', row=1, column=0, padx=10, pady=5)
        self.domain_entry = ttk.Entry(self)
        self.domain_entry.insert(0, self.configuracion.get('configurations', 'domain'))
        self.domain_entry.grid(sticky='ew', row=1, column=1, padx=10, pady=5)

        # Etiqueta y entrada para el tiempo de espera
        tk.Label(self, text="Tiempo de espera:").grid(sticky='w', row=2, column=0, padx=10, pady=5)
        self.time_wait_entry = ttk.Spinbox(self, from_=0, to=9999, increment=1)
        self.time_wait_entry.insert(0, self.configuracion.get('configurations', 'time_wait'))
        self.time_wait_entry.grid(sticky='ew', row=2, column=1, padx=10, pady=5)

        # Etiqueta y entrada para el nombre de la carpeta
        tk.Label(self, text="Nombre de la carpeta:").grid(sticky='w', row=3, column=0, padx=10, pady=5)
        self.folder_name_entry = tk.Entry(self)
        self.folder_name_entry.insert(0, self.configuracion.get('configurations', 'folder_name'))
        self.folder_name_entry.grid(sticky='ew', row=3, column=1, padx=10, pady=5)

        # Etiqueta y entrada para el nombre de la hoja
        tk.Label(self, text="Nombre de la hoja:").grid(sticky='w', row=4, column=0, padx=10, pady=5)
        self.sheet_name_entry = tk.Entry(self)
        self.sheet_name_entry.insert(0, self.configuracion.get('configurations', 'sheet_name'))
        self.sheet_name_entry.grid(sticky='ew', row=4, column=1, padx=10, pady=5)

        # Botón para guardar la configuración
        ttk.Button(self, text="Guardar", command=self.guardar_configuracion).grid(row=5, column=0, pady=10, padx=25)
        ttk.Button(self, text="Cancelar", command=self.cancelar_configuracion).grid(row=5, column=1, pady=10, padx=25)

        # Logica de validacion bind en entry
        self.domain_entry.bind("<FocusOut>", self.validate_entry_out)
        self.time_wait_entry.bind("<FocusOut>", self.validate_entry_out)
        self.folder_name_entry.bind("<FocusOut>", self.validate_entry_out)
        self.sheet_name_entry.bind("<FocusOut>", self.validate_entry_out)
        self.domain_entry.bind("<FocusIn>", self.validate_entry_in)
        self.time_wait_entry.bind("<FocusIn>", self.validate_entry_in)
        self.folder_name_entry.bind("<FocusIn>", self.validate_entry_in)
        self.sheet_name_entry.bind("<FocusIn>", self.validate_entry_in)

        self.attributes('-topmost', 1)
        self.protocol("WM_DELETE_WINDOW", self.cerrar_ventana)

    def cerrar_ventana(self):
        self.attributes('-topmost', 0)  # Restablecer el valor para permitir que la ventana principal quede por encima
        self.destroy()

    def guardar_configuracion(self):
        # try:
        if self.change_name_folder:
            self.change_name_file_folder(self.folder_name_entry.get(),
                                         self.configuracion.get('configurations', 'folder_id'))
        if self.change_name_sheet:
            self.change_name_file_folder(self.sheet_name_entry.get(),
                                         self.configuracion.get('configurations', 'sheet_id'))

        # Guarda los cambios en la configuración
        self.configuracion.set('credentials', 'path_key', self.cred_path.get())
        self.configuracion.set('configurations', 'domain', self.domain_entry.get())
        self.configuracion.set('configurations', 'time_wait', self.time_wait_entry.get())
        self.configuracion.set('configurations', 'folder_name', self.folder_name_entry.get())
        self.configuracion.set('configurations', 'sheet_name', self.sheet_name_entry.get())

        # Guarda la configuración en el archivo
        with open('Config\\configuration.cfg', 'w') as config_file:
            self.configuracion.write(config_file)

        # Cierra la ventana
        self.cerrar_ventana()

        # except Exception as e:
        #    print(e)

    def cancelar_configuracion(self):
        if self.is_modify:
            response = messagebox.askyesno("Cancelar Cambios", "¿Desea salir sin guardar los cambios?")
            if response:
                self.cerrar_ventana()
        else:
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
        if event.widget.winfo_name() == "!entry3":
            self.change_name_folder = True
        if event.widget.winfo_name() == "!entry4":
            self.change_name_sheet = True

    def validate_entry_in(self, event):
        self.copy_entry = event.widget.get()

    def change_name_file_folder(self, name, fileid):
        creds = authentication_gmail(key_file=self.cred_path.get())
        drive_service = build('drive', 'v3', credentials=creds)
        folder = drive_service.files().get(fileId=fileid).execute()
        updated_folder = drive_service.files().update(fileId=fileid, body={'name': name}).execute()


class MiApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Interfaz de Control")
        self.root.resizable(False, False)
        self.threading_csirt = False

        # Configuración
        self.configuracion = configparser.ConfigParser()
        self.configuracion.read('Config\\configuration.cfg')

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
                                      command=self.script_paralelo)
        self.btn_iniciar.pack(side='left', pady=5, padx=50)

        self.btn_detener = ttk.Button(labelframe_top, text="Stop Service", padding="10 8 10 8", state="disabled",
                                      command=self.detener_script)
        self.btn_detener.pack(side='left', pady=5, padx=50)

        # Caja de texto para logs
        self.log_text = tk.Text(labelframe_bottom, state='disabled', height=10, width=50)
        self.log_text.pack(padx=10, pady=10)

        labelframe_top.pack(fill="both", expand=True, padx=5, ipady=3)
        labelframe_bottom.pack(fill="both", expand=True, padx=5, ipady=3)

    def ver_configuracion(self):
        # Muestra la configuración actual en una ventana de mensaje
        config_str = f"[credentials]\npath_key = {self.configuracion.get('credentials', 'path_key')}\n\n" \
                     f"[configurations]\ndomain = {self.configuracion.get('configurations', 'domain')}\n" \
                     f"time_wait = {self.configuracion.get('configurations', 'time_wait')}\n" \
                     f"folder_name = {self.configuracion.get('configurations', 'folder_name')}\n" \
                     f"sheet_name = {self.configuracion.get('configurations', 'sheet_name')}"

        messagebox.showinfo("Configuración", config_str)

    def abrir_ventana_configuracion(self):
        # Abre la ventana de configuración
        ConfiguracionVentana(self.root, self.configuracion)

    def iniciar_script(self):
        # Inicia el script en un hilo aparte
        self.update_text("info", "Iniciando el script...")
        self.start_service = threading.Thread(target=self.script_paralelo)
        self.start_service.start()

    def detener_script(self):
        # Detiene el script (simulando detener el servicio)
        self.update_text("info", "Deteniendo el script")
        self.threading_csirt = False
        self.thread.stop()
        self.thread.join()
        self.btn_iniciar.config(state='normal')
        self.btn_detener.config(state='disabled')
        self.config_menu.entryconfig("Configuración", state="normal")


    def script_paralelo(self):
        # Simulación de un script en ejecución
        wait_time = int(self.configuracion.get('configurations', 'time_wait'))
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
        # self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.yview(tk.END)  # Desplazar la caja de texto para mostrar el último registro
        self.log_text.config(state='disabled')

        if level_log.lower() == "info":
            self.logger.info(message)
        elif level_log.lower() == "warning":
            self.logger.warning(message)
        elif level_log.lower() == "error":
            self.logger.error(message)

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
        info_handler = logging.FileHandler('Logs\\main.log')
        info_handler.setLevel(logging.INFO)
        info_handler.setFormatter(formatter)
        self.logger.addHandler(info_handler)


    def on_closing(self):
        if self.threading_csirt:
            return
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = MiApp(root)
    root.mainloop()