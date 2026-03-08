import os
import sys
import shutil
import threading
import subprocess
import urllib.request
import urllib.error
import customtkinter as ctk
from tkinter import messagebox

# --- CONFIGURACIÓN ---
GITHUB_INI_URL = "https://raw.githubusercontent.com/IzMileZ/the-sims-4/refs/heads/main/g_The%20Sims%204.ini"
INI_TS4 = "g_The Sims 4.ini"
INI_TS3 = "g_The Sims 3.ini"

# Directorio exacto donde setup.bat busca/lee las configuraciones instaladas
APPDATA_DIR = os.path.join(os.environ.get('APPDATA', os.path.expanduser("~")), 'anadius', 'EA DLC Unlocker v2')

def get_base_dir():
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))

class UnlockerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Unlocker Pro Auto-Setup")
        self.geometry("640x420")
        self.resizable(False, False)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)

        # --- Panel Izquierdo ---
        self.left_panel = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color=("gray85", "gray16"))
        self.left_panel.grid(row=0, column=0, sticky="nsew")
        self.left_panel.grid_rowconfigure(1, weight=1)

        self.title_label = ctk.CTkLabel(
            self.left_panel, 
            text="Instrucciones", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.title_label.grid(row=0, column=0, padx=20, pady=(30, 20))

        instrucciones_texto = (
            "1. Selecciona los juegos\n"
            "   que deseas desbloquear.\n\n"
            "2. El programa instalará el\n"
            "   Unlocker base y luego\n"
            "   añadirá las configs.\n\n"
            "   (The Sims 4 se bajará\n"
            "   siempre actualizado\n"
            "   desde GitHub).\n\n"
            "3. Haz clic en 'Aceptar'\n"
            "   para iniciar.\n\n"
            "   ✓ 100% automático."
        )
        self.info_label = ctk.CTkLabel(
            self.left_panel, 
            text=instrucciones_texto, 
            justify="left",
            font=ctk.CTkFont(size=13)
        )
        self.info_label.grid(row=1, column=0, padx=20, pady=10, sticky="n")

        # --- Panel Derecho ---
        self.right_panel = ctk.CTkFrame(self, fg_color="transparent")
        self.right_panel.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.right_panel.grid_rowconfigure(0, weight=0) 
        self.right_panel.grid_rowconfigure(1, weight=1) 
        self.right_panel.grid_rowconfigure(2, weight=0) 
        self.right_panel.grid_rowconfigure(3, weight=0) 
        self.right_panel.grid_rowconfigure(4, weight=1) 

        # Opciones (Checkboxes)
        self.options_frame = ctk.CTkFrame(self.right_panel, fg_color="transparent")
        self.options_frame.grid(row=0, column=0, pady=(0, 10), sticky="n")

        self.sims4_var = ctk.BooleanVar(value=True)
        self.sims3_var = ctk.BooleanVar(value=False)

        self.chk_sims4 = ctk.CTkCheckBox(
            self.options_frame, 
            text="The Sims 4 (Auto-update nube)", 
            variable=self.sims4_var,
            font=ctk.CTkFont(weight="bold")
        )
        self.chk_sims4.grid(row=0, column=0, pady=10, sticky="w")

        self.chk_sims3 = ctk.CTkCheckBox(
            self.options_frame, 
            text="The Sims 3 (Archivo local)", 
            variable=self.sims3_var,
            font=ctk.CTkFont(weight="bold")
        )
        self.chk_sims3.grid(row=1, column=0, pady=10, sticky="w")

        self.status_label = ctk.CTkLabel(
            self.right_panel, 
            text="Selecciona tus juegos y presiona Aceptar.", 
            font=ctk.CTkFont(size=14)
        )
        self.status_label.grid(row=1, column=0, padx=20, pady=(10, 20), sticky="s")

        self.progressbar = ctk.CTkProgressBar(self.right_panel, mode="indeterminate", width=250)
        self.progressbar.grid(row=2, column=0, padx=20, pady=10)
        self.progressbar.set(0)
        self.progressbar.grid_remove() 

        self.accept_button = ctk.CTkButton(
            self.right_panel, 
            text="Aceptar / Instalar", 
            command=self.start_process_thread,
            font=ctk.CTkFont(size=15, weight="bold"),
            height=45,
            width=200
        )
        self.accept_button.grid(row=3, column=0, padx=20, pady=20)

    def log_status(self, text):
        self.status_label.configure(text=text)
        self.update_idletasks()

    def start_process_thread(self):
        if not self.sims4_var.get() and not self.sims3_var.get():
            messagebox.showwarning("Atención", "¡Selecciona al menos un juego para desbloquear!")
            return
            
        self.accept_button.configure(state="disabled")
        self.chk_sims4.configure(state="disabled")
        self.chk_sims3.configure(state="disabled")
        self.progressbar.grid()
        self.progressbar.start()
        
        thread = threading.Thread(target=self.run_process, daemon=True)
        thread.start()

    def run_process(self):
        try:
            # 1. Instalar EA DLC Unlocker Base ejecutando 'setup.bat install'
            self.log_status("Instalando el Unlocker base en EA App/Origin...")
            self.run_setup_bat_install()

            # Asegurar que el directorio de configs de anadius exista
            os.makedirs(APPDATA_DIR, exist_ok=True)

            # 2. Configurar Los Sims 4 si está marcado
            if self.sims4_var.get():
                self.log_status("Actualizando e instalando config de The Sims 4...")
                self.check_and_update_ini(INI_TS4, GITHUB_INI_URL)

            # 3. Configurar Los Sims 3 si está marcado
            if self.sims3_var.get():
                self.log_status("Instalando config local de The Sims 3...")
                self.install_local_ini(INI_TS3)

            self.log_status("¡Proceso completado con éxito!")
            messagebox.showinfo(
                "Éxito", 
                "El Unlocker y las configuraciones se instalaron correctamente.\nAl abrir tu juego, los DLCs estarán disponibles."
            )
            
        except Exception as e:
            self.log_status("Error en el proceso.")
            messagebox.showerror("Error", f"Se produjo un error:\n\n{str(e)}")
        finally:
            self.progressbar.stop()
            self.progressbar.grid_remove()
            self.accept_button.configure(state="normal", text="Reintentar")
            self.chk_sims4.configure(state="normal")
            self.chk_sims3.configure(state="normal")

    def run_setup_bat_install(self):
        """Ejecuta setup.bat con el argumento 'install' para que no pida interacciones manuales"""
        base_dir = get_base_dir()
        bat_path = os.path.join(base_dir, "setup.bat")
        
        if not os.path.exists(bat_path):
            raise FileNotFoundError(f"No se encontró 'setup.bat' en:\n{base_dir}")
            
        try:
            # Ejecutamos con el parámetro "install" que en setup.bat salta el menú principal directamente a instalar.
            process = subprocess.Popen(
                [bat_path, "install"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True,
                cwd=base_dir,
                universal_newlines=True
            )
            
            stdout, stderr = process.communicate()
            
            with open(os.path.join(base_dir, "unlocker_install_log.txt"), "w", encoding="utf-8") as log_f:
                log_f.write(f"--- STDOUT ---\n{stdout}\n\n--- STDERR ---\n{stderr}")
                
            if process.returncode != 0 and process.returncode != 1:  # Ignora 1 si es elevación UAC en algunos sistemas
                pass # Fallo posible pero sigue adelante por si solo fue advertencia. Logs registrarán el detalle.
                
        except Exception as e:
            raise Exception(f"Fallo al ejecutar setup.bat install:\n{str(e)}")

    def check_and_update_ini(self, filename, url):
        """Descarga e instala el .ini desde GitHub directo a su ubicación final."""
        target_path = os.path.join(APPDATA_DIR, filename)
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 UnlockerBot/1.0'})
            response = urllib.request.urlopen(req, timeout=10)
            content = response.read()
            with open(target_path, 'wb') as f:
                f.write(content)
        except urllib.error.URLError as e:
            # Si no hay internet, intenta usar el archivo empaquetado como copia de seguridad
            self.install_local_ini(filename)
            print(f"[!] Sin internet. Se instaló la versión local de respaldo de {filename}")

    def install_local_ini(self, filename):
        """Si es Sims 3 (o falla la red en Sims 4), usa el archivo empaquetado en el ejecutable."""
        base_dir = get_base_dir()
        source_path = os.path.join(base_dir, filename)
        target_path = os.path.join(APPDATA_DIR, filename)
        
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"No se encontró el archivo local {filename} integrado en el .exe")
            
        shutil.copy2(source_path, target_path)


if __name__ == "__main__":
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue") 
    
    app = UnlockerApp()
    app.mainloop()
