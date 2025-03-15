import tkinter as tk
from tkinter import ttk

# Crear ventana
ventana = tk.Tk()
ventana.title("Tabla con desplazamiento horizontal")

# Configurar ventana para que se expanda
ventana.geometry("800x400")  # Puedes ajustar el tamaño según tus necesidades

etiqueta_titulo_historial_de_detecciones = tk.Label(ventana, text="Historial de \ndetecciones", font=("Inter", 20, "bold", "italic"), bg="#ECECEC", fg="#000000")
etiqueta_titulo_historial_de_detecciones.pack(pady=10)
# Crear un Frame para contener el Treeview y la scrollbar
frame = tk.Frame(ventana)
frame.pack(fill=tk.BOTH, expand=True)

# Crear Treeview con varias columnas
tree = ttk.Treeview(frame, columns=("Fecha", "Hora", "Amenaza", "Detalle", "IP"), show="headings", height=8)
tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

# Configurar encabezados de columna
tree.heading("Fecha", text="Fecha")
tree.heading("Hora", text="Hora")
tree.heading("Amenaza", text="Amenaza")
tree.heading("Detalle", text="Detalle")
tree.heading("IP", text="IP")

# Ajustar ancho de columnas
tree.column("Fecha", width=150)
tree.column("Hora", width=150)
tree.column("Amenaza", width=200)
tree.column("Detalle", width=200)
tree.column("IP", width=200)

# Insertar datos de ejemplo
datos = [
    ["05-11-2024", "18-37-06", "No Phishing", "Todo bien", "192.168.0.1"],
    ["06-11-2024", "10-11-16", "Phishing", "Intento de fraude", "192.168.0.2"],
    ["07-11-2024", "10-43-14", "No Phishing", "Todo normal", "192.168.0.3"]
]

for fila in datos:
    tree.insert("", tk.END, values=fila)

# Crear barra de desplazamiento horizontal
scrollbar_horizontal = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
scrollbar_horizontal.pack(side=tk.TOP, fill=tk.X)

# Configurar el Treeview para que use la scrollbar horizontal
tree.configure(xscrollcommand=scrollbar_horizontal.set)

ventana.mainloop()
