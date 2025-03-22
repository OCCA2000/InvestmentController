import tkinter as tk
import subprocess
import threading
import time

def execute_scripts():
    scripts = [
        "AccionesDiario.py",
        "BonosDiario.py",
        "Dividendos.py",
        "FacturasDiario.py",
        "GenericosDiario.py",
        "ObligacionesDiario.py",
        "PapelesDiario.py",
        "TitularizacionesDiario.py"
    ]
    
    for script in scripts:
        output_label.config(text=output_label.cget("text") + f"\nIniciando: {script}")
        try:
            subprocess.run(["python", script], check=True)
            output_label.config(text=output_label.cget("text") + f"\nFinalizado: {script}")
        except subprocess.CalledProcessError as e:
            output_label.config(text=output_label.cget("text") + f"\nError al ejecutar {script}: {e}")
        time.sleep(5)  # Espera 20 segundos entre cada ejecución

def start_execution():
    threading.Thread(target=execute_scripts, daemon=True).start()

# Crear la ventana principal
root = tk.Tk()
root.title("Ejecutor de Scripts")
root.geometry("400x400")

# Botón para ejecutar los scripts
execute_button = tk.Button(root, text="Ejecutar Scripts", command=start_execution, font=("Arial", 12))
execute_button.pack(pady=20)

# Etiqueta para mostrar el estado de ejecución
output_label = tk.Label(root, text="", font=("Arial", 10), justify="left", anchor="w")
output_label.pack()

# Iniciar la interfaz gráfica
root.mainloop()
