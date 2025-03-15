import tkinter as tk
from tkinter import ttk
import subprocess
import sys
import os

# Función para abrir una URL en Google Chrome
def abrir_url(event):
    # Obtener el ítem seleccionado en el Treeview
    item = tree.selection()
    if item:
        url = tree.item(item, "values")[2]  # Suponiendo que la URL está en la columna 2 (col2)
        if url.startswith("http"):  # Verificar que la URL comienza con http:// o https://
            try:
                # Rutas posibles para Google Chrome
                chrome_paths = [
                    "C:/Program Files/Google/Chrome/Application/chrome.exe",  # Ruta predeterminada en Windows
                    "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe",  # Ruta alternativa
                ]
                
                chrome_path = None
                for path in chrome_paths:
                    if os.path.exists(path):  # Comprobar si el archivo existe
                        chrome_path = path
                        break
                
                if chrome_path is None:
                    raise FileNotFoundError("No se encontró Google Chrome en el sistema.")
                
                # Ejecutar Google Chrome con la URL
                subprocess.run([chrome_path, url], check=True)
            except Exception as e:
                print("Error al abrir Google Chrome:", e)

# Crear la ventana principal
root = tk.Tk()

# Crear el Treeview
tree = ttk.Treeview(root, columns=("col1", "col2", "col3"))
tree.heading("#0", text="ID")
tree.heading("col1", text="Descripción")
tree.heading("col2", text="Descripción")
tree.heading("col3", text="URL")

# Insertar algunos ítems en el Treeview (columna URL contiene la URL clickeable)
tree.insert("", "end", values=("Item 1", "Visitar Google", "https://www.google.com"))
tree.insert("", "end", values=("Item 2", "Visitar YouTube", "https://www.youtube.com"))

# Empaquetar el Treeview en la ventana
tree.pack()

# Asociar el evento de clic en el Treeview a la función abrir_url
tree.bind("<ButtonRelease-1>", abrir_url)

# Ejecutar la aplicación
root.mainloop()
