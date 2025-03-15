import pyodbc
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk
import pygetwindow
import pyautogui
import hashlib
from io import BytesIO
import io
import os
import time 
import torch
import cv2
import numpy as np
import pathlib
import math
from datetime import datetime
import subprocess
import winreg
import threading

#Funciones de la aplicacion
def registrar_usuario(entrada_nombre_de_usuario,entrada_contrasena,entrada_repetir_contrasena):
    #Cargar los datos de entrada en variables
    nombre_de_usuario = entrada_nombre_de_usuario.get()
    contrasena = entrada_contrasena.get()
    repetir_contrasena = entrada_repetir_contrasena.get()
    #Condiciones para registrar al usuario
    if not nombre_de_usuario or not contrasena or not repetir_contrasena:
        espacio_mensaje_respuesta_crear_cuenta.config(text="¡¡¡Todos los campos son obligatorios!!!", fg="#B70000")
        return
    if contrasena != repetir_contrasena:
        espacio_mensaje_respuesta_crear_cuenta.config(text="¡¡Las contraseñas no coinciden!!!", fg="#B70000")
        return
    #Interaccion con la BD
    try:
        #Conexion a la BD
        conexion = pyodbc.connect(
        'Driver={ODBC Driver 17 for SQL Server};'
        'Server=tcp:servidordatosusuarios.database.windows.net,1433;'
        'Database=db_usuarios;'
        'Uid=Berl;'
        'Pwd=Trabajo123;'
        'Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'
        )
        #Creacion del cursor para la Query
        cursor = conexion.cursor()
        #Query para validar si ya existe un usuario con ese nombre
        cursor.execute("SELECT COUNT(*) FROM Usuarios WHERE usuario = ?", (nombre_de_usuario))
        resultado = cursor.fetchone()
        #Condicion para validar la existencia del usuario
        if resultado[0] > 0: #Si es mayor a 0, entonces ya existe el usuario
            espacio_mensaje_respuesta_crear_cuenta.config(text="El nombre de usuario ya está en uso", fg="#B70000")
            #Desconexion de la BD
            conexion.close()
            return
        #Registrar al nuevo usuario
        else:
            cursor.execute("INSERT INTO Usuarios (usuario, contrasena) VALUES (?, ?)",
                       (nombre_de_usuario, contrasena))
            #Confirmar cambios realizados a la BD
            conexion.commit()
            espacio_mensaje_respuesta_crear_cuenta.config(text="Usuario registrado con éxito", fg="#00B733")
            #Desconexion de la BD
            conexion.close()
    #De suceder algun error
    except pyodbc.IntegrityError:
        espacio_mensaje_respuesta_crear_cuenta.config(text="El nombre de usuario ya están en uso")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo registrar el usuario: {e}")

def iniciar_sesion(entrada_nombre_de_usuario,entrada_contrasena,parametros_ventana_inicio_de_sesion):
    #Cargar los datos de entrada en variables
    nombre_de_usuario = entrada_nombre_de_usuario.get()
    contrasena = entrada_contrasena.get()
    #Creacion de una variable global id para facilitar en uso de Querys dentro de las demas funciones
    global id_usuario
    id_usuario = ""
    #Condiciones para que el usuario inicie sesion
    if not nombre_de_usuario or not contrasena:
        espacio_mensaje_respuesta_inicio_sesion.config(text="¡¡¡Todos los campos son obligatorios!!!")
        return
    #Interaccion con la BD
    try:
        #Conexion a la BD
        conexion = pyodbc.connect(
        'Driver={ODBC Driver 17 for SQL Server};'
        'Server=tcp:servidordatosusuarios.database.windows.net,1433;'
        'Database=db_usuarios;'
        'Uid=Berl;'
        'Pwd=Trabajo123;'
        'Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'
        )
        #Creacion de los cursores para las Querys
        cursor = conexion.cursor()
        cursor2 = conexion.cursor()
        # Comprobacion si el usuario existe con la contraseña correcta
        #Query para validar si el nombre de usuario y contrasena que ingresan existen
        cursor.execute("SELECT * FROM Usuarios WHERE usuario = ? AND contrasena = ?", (nombre_de_usuario, contrasena))
        resultado = cursor.fetchone()
        #Query para obtener la id de ese usuario
        cursor2.execute("SELECT id FROM Usuarios WHERE usuario = ? AND contrasena = ?", (nombre_de_usuario,contrasena))
        fila = cursor2.fetchone()
        #Condicion si existe el usuario, guarda la id obtenida en la variable id
        if resultado:
            id_usuario = fila[0]
            #Aperturar la ventana de menu
            pantalla_menu(parametros_ventana_inicio_de_sesion)
        else:
            #De no coincidir los datos ingresados con algun usuario de la BD
            #Mensaje devuelto en pantalla al usuario
            espacio_mensaje_respuesta_inicio_sesion.config(text="Nombre de usuario o\n contraseña incorrectos")
        #Desconexion de la BD
        conexion.close()
    #De suceder algun error
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo iniciar sesión: {e}")

def actualizar_usuario(nombre_de_usuario,contrasena, entrada_nombre_de_usuario, entrada_contrasena,etiqueta_nombre_de_usuario_actualizar,ventana_actualizar_datos,parametros_ventana_configuraciones,parametros_ventana_menu,etiqueta_nombre_de_usuario_menu):
    #Cargar los datos de entrada en variables
    validar_nombre_de_usuario = entrada_nombre_de_usuario.get()
    validar_contrasena = entrada_contrasena.get()
    #Condiciones para que el usuario actualice sus datos
    if not validar_nombre_de_usuario or not validar_contrasena:
        espacio_mensaje_respuesta_actualizar_datos.config(text="¡¡¡Todos los campos son obligatorios!!!", fg="#B70000")
        return
    if validar_nombre_de_usuario == nombre_de_usuario and validar_contrasena == contrasena:
        espacio_mensaje_respuesta_actualizar_datos.config(text="Nombre de usuario y\n contraseña son los mismos", fg="#B70000")
        return
    #Interaccion con la BD
    try:
        #Conexion con la BD
        conexion = pyodbc.connect(
        'Driver={ODBC Driver 17 for SQL Server};'
        'Server=tcp:servidordatosusuarios.database.windows.net,1433;'
        'Database=db_usuarios;'
        'Uid=Berl;'
        'Pwd=Trabajo123;'
        'Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'
        )
        #Creacion del cursor para la Query
        cursor = conexion.cursor()
        #Query para validar si ya existe un usuario con el nombre de usuario que se desea cambiar que la id sea diferente a la del usuario que inicio sesion
        cursor.execute("SELECT COUNT(*) FROM Usuarios WHERE usuario = ? and id != ?", (validar_nombre_de_usuario, id_usuario))
        resultado = cursor.fetchone()
        #Condicion si existe un usuario con el nombre de usuario que se desea cambiar 
        if resultado[0] > 0:  # Si es mayor a 0, entonces ya existe el usuario con ese nombre de usuario
            #Mensaje devuelto en pantalla al usuario
            espacio_mensaje_respuesta_actualizar_datos.config(text="El nombre de usuario ya está en uso", fg="#B70000")
            #Desconexion de la BD
            conexion.close()
            return
        else:
            #Query para actualizar los datos del usuario usando de referencia la id del usuario que inicio sesion
            cursor.execute("""
            UPDATE Usuarios 
            SET usuario = ?, contrasena = ?
            WHERE id = ?
            """, (validar_nombre_de_usuario, validar_contrasena, id_usuario))
            #Confirmar cambios realizados a la BD
            conexion.commit()
            #Desconexion de la BD
            conexion.close()
            #Mensaje devuelto en pantalla al usuario
            espacio_mensaje_respuesta_actualizar_datos.config(text="Datos de usuario actualizados con éxito", fg="#00B733")
        etiqueta_nombre_de_usuario_menu.config(text="Nombre de usuario: " + validar_nombre_de_usuario)
        pantalla_configuraciones_cuenta_de_usuario(parametros_ventana_menu,etiqueta_nombre_de_usuario_menu,ventana_actualizar_datos)
        ventana_actualizar_datos.destroy()
    #De suceder algun error
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo actualizar el usuario: {e}")
    
def borrar_cuenta(ventana_borrar_cuenta):
    #Interaccion con la BD
    try:
        #Conexion con la BD
        conexion = pyodbc.connect(
        'Driver={ODBC Driver 17 for SQL Server};'
        'Server=tcp:servidordatosusuarios.database.windows.net,1433;'
        'Database=db_usuarios;'
        'Uid=Berl;'
        'Pwd=Trabajo123;'
        'Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'
        )
        #Creacion del cursor para la Query
        cursor = conexion.cursor()
        #Query para borrar la cuenta de usuario usando de referencia su id del usuario que inicio sesion
        cursor.execute("DELETE FROM Usuarios WHERE id = ?", (id_usuario))
        #Confirmar cambios realizados en la BD
        conexion.commit()
        #Desconexion de la BD
        conexion.close()
        #Regresar a la ventana de inicio
        regresar_a_ventana_inicio(ventana_borrar_cuenta)
    #De suceder algun error
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo eliminar el usuario: {e}")

def minimizar_ventana_app(ventana_deteccion_fase_1):
    #Ocultar la ventana de la fase 1
    ventana_deteccion_fase_1.iconify()

def captura_de_contenido_de_pantalla(espacio_mensaje_respuesta_captura_de_pantalla):
    #Variable global screenshot
    global screenshot
    #Tomar datos de todas las pantallas con "Google Chrome" en el nombre de la ventana
    pantallas = pygetwindow.getWindowsWithTitle('Google Chrome')
    #Condicion si no se encuentra ninguna ventana con "Google Chrome" abierta
    if len(pantallas) == 0:
        espacio_mensaje_respuesta_captura_de_pantalla.config(text="¡No se encontro una pantalla de google chrome abierta!", fg="#B70000")
        return
    #Creacion de una variable que toma la primera "Se asume que solo debe de haber una"
    pantalla_chrome = pantallas[0]
    #Condicion si la ventana no esta activa, la trae al frente
    if not pantalla_chrome.isActive:
        pantalla_chrome.activate()
    #Creacion de las variables para tomar los parametros de la ventana de Google Chrome
    x, y, width, height = pantalla_chrome.left, pantalla_chrome.top, pantalla_chrome.width, pantalla_chrome.height

    #Forma 1: Guardar la imagen capturada de manera local
    screenshot = pyautogui.screenshot(region=(x, y, width, height))
    if not os.path.exists('capturas'):
        os.makedirs('capturas')
    screenshot.save("capturas/captura_chrome.png")

def retornar_ventana_app():
    #Tomar datos de la ventana de la aplicacion
    ventanas_app = pygetwindow.getWindowsWithTitle('WillRo App')
    #Si no existe la ventana detiene la accion
    if len(ventanas_app) == 0:
        return
    #Creacion de una variable que toma la primera "Se asume que solo debe de haber una"
    ventana_app = ventanas_app[0]
    #Condicion si la ventana no esta activa, la trae al frente
    if not ventana_app.isActive:
        ventana_app.activate()

def analisis_de_captura_de_contenido():
    #Variables globales
    global porcentaje_phishing
    global porcentaje_no_phishing
    global mensaje_phishing_no_phishing
    global results

    porcentaje_phishing = 0
    porcentaje_no_phishing = 0
    mensaje_phishing_no_phishing = ""
    #Importante para que Windows sea capaz de emplear PosixPath
    temp = pathlib.PosixPath
    pathlib.PosixPath = pathlib.WindowsPath
    #Carga del modelo
    model = torch.hub.load('ultralytics/yolov5', 'custom', path = 'model/best.pt', force_reload = True)
    #Leer la imagen capturada anteriormente
    image_path = 'capturas/captura_chrome.png'
    image = cv2.imread(image_path)
    #Realizar detecciones
    results = model(image)
    #Extraer etiquetas y probabilidades
    detections = results.pandas().xyxy[0]  # Obtiene el DataFrame con las detecciones
    total_detections = len(detections)
    #Verificar si hay detecciones
    if total_detections > 0:
        phishing_count = detections[detections['name'] == 'Phishing'].shape[0]
        no_phishing_count = detections[detections['name'] == 'No Phishing'].shape[0]

        #Calcular el porcentaje de cada etiqueta
        phishing_percentage = (phishing_count / total_detections) * 100
        no_phishing_percentage = (no_phishing_count / total_detections) * 100
        #Cargar el porcentaje en las variables globales para utilizarlas fuera de la funcion
        porcentaje_phishing = phishing_percentage
        porcentaje_no_phishing = no_phishing_percentage
    else:
        #Mensaje para devolver en pantalla al usuario despues de retornar a la ventana
        mensaje_phishing_no_phishing = "No se encontro una pagina web"
    #Convertir los resultados en formato de imagen
    results_img = np.squeeze(results.render())
    #Guardar la imagen con detecciones en formato PNG
    if not os.path.exists('resultado'):
        os.makedirs('resultado')
    output_path = 'resultado/deteccion_resultado.png'
    cv2.imwrite(output_path, results_img)   

def almacenamiento_de_la_deteccion():
    #Guardar la imagen en una memoria de la app para enviarlo al azure blob storage
    buffer = io.BytesIO()
    screenshot.save(buffer, format='PNG')
    buffer.seek(0)

    ruta_resultado_deteccion = 'resultado/deteccion_resultado.png'
    imagen_resultado = Image.open(ruta_resultado_deteccion)
    buffer2 = io.BytesIO()
    imagen_resultado.save(buffer2, format='PNG')
    buffer2.seek(0)

    fecha_actual = datetime.now()
    fecha_texto = fecha_actual.strftime("%d-%m-%Y")
    hora_texto = fecha_actual.strftime("%H-%M-%S")

    #Interaccion con la BD de imagenes
    try:
        # Conectar con tu cuenta de Azure Blob
        blob_service_client = BlobServiceClient.from_connection_string("DefaultEndpointsProtocol=https;AccountName=alya;AccountKey=VWCHu7+oEHQdotNC9XBhXwoyr1TVFsEpcmYCgSptYd9AhTmTTKmDSF8H4mZNnpVI7LXrCpZsr5lr+AStEsS8Wg==;EndpointSuffix=core.windows.net")
        # Nombre del contenedor y el nombre de los archivos en Azure
        container_name = "imagenes2"
        blob_name = f"{id_usuario}_Captura_{fecha_texto}_{hora_texto}.png" #Modificar con id e fecha / hora
        blob_name2 = f"{id_usuario}_Resultado_{fecha_texto}_{hora_texto}.png" #Modificar con id e fecha / hora
    
        # Acceder al contenedor y darle el nombre del cliente 
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        blob_client2 = blob_service_client.get_blob_client(container=container_name, blob=blob_name2)

        # Subir la imagen desde el buffer BytesIO
        blob_client.upload_blob(buffer, blob_type="BlockBlob", overwrite=True)
        blob_client2.upload_blob(buffer2, blob_type="BlockBlob", overwrite=True)

        #Obtener las URL de guardado de ambas imagenes
        url_captura = blob_client.url
        url_resultado = blob_client2.url
    except Exception as e:
        print(f"Error al subir la captura de pantalla: {e}")
    
    #Interaccion con la BD
    try:
        #Conexion a la BD
        conexion = pyodbc.connect(
        'Driver={ODBC Driver 17 for SQL Server};'
        'Server=tcp:servidordatosusuarios.database.windows.net,1433;'
        'Database=db_usuarios;'
        'Uid=Berl;'
        'Pwd=Trabajo123;'
        'Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'
        )
        #Creacion del cursor para la Query
        cursor = conexion.cursor()
        #Query para guardar la informacion de la deteccion
        cursor.execute("INSERT INTO detecciones (id_usuario, fecha, hora, amenaza, url_captura, url_resultado, recomendaciones_1, recomendaciones_2, recomendaciones_3) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                       (id_usuario, fecha_texto, hora_texto, amenaza, url_captura, url_resultado, texto_recomendacion_1, texto_recomendacion_2, texto_recomendacion_3))
        #Confirmar cambios realizados en la BD
        conexion.commit()
        conexion.close()
    #De suceder algun error
    except pyodbc.IntegrityError:
        messagebox.showerror("Fail", f"No se pudo registrar la deteccion: {e}") 
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo registrar la deteccion: {e}")   

def obtener_detecciones():
    global filas
    #Interaccion con la BD
    try:
        #Conexion a la BD
        conexion = pyodbc.connect(
        'Driver={ODBC Driver 17 for SQL Server};'
        'Server=tcp:servidordatosusuarios.database.windows.net,1433;'
        'Database=db_usuarios;'
        'Uid=Berl;'
        'Pwd=Trabajo123;'
        'Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'
        )
        #Creacion del cursor para la Query
        cursor = conexion.cursor()
        #Query para obtener el id fecha y hora de la deteccion
        cursor.execute("SELECT fecha, hora, amenaza FROM detecciones WHERE id_usuario = ?",(id_usuario))
        filas = cursor.fetchall()
    except pyodbc.IntegrityError:
        messagebox.showerror("Fail", f"No se pudo registrar la deteccion: {e}") 
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo registrar la deteccion: {e}")   

def cerrar_aplicacion():
    #Destruir la ventana principal para permitir que toda la aplicacion se cierre y dejar de ejecutarla
    ventana_inicio.destroy()


#Pantallas de la aplicacion
def pantalla_inicio_de_sesion(parametros_ventana_inicio):
    #Variables globales
    global espacio_mensaje_respuesta_inicio_sesion
    #Ocultar la ventana de Inicio
    ventana_inicio.withdraw()
    #Creacion de la ventana de Inicio de sesion
    posicion_ventana_inicio = parametros_ventana_inicio.winfo_geometry()
    ventana_inicio_de_sesion = tk.Toplevel()
    ventana_inicio_de_sesion.title("WillRo App")
    ventana_inicio_de_sesion.geometry("340x620")
    ventana_inicio_de_sesion.resizable(False, False)
    ventana_inicio_de_sesion.configure(bg="#ECECEC")
    ventana_inicio_de_sesion.protocol("WM_DELETE_WINDOW", cerrar_aplicacion)
    ventana_inicio_de_sesion.geometry(posicion_ventana_inicio) 
    #Encabezado de la aplicacion
    encabezado_frame = tk.Frame(ventana_inicio_de_sesion, bg="#1B8A91", height=60)
    encabezado_frame.pack(fill="x")
    titulo0 = tk.Label(encabezado_frame, text="", font=("Inter", 24, "bold"), bg="#1B8A91", fg="#FFFFFF")
    titulo0.pack(side="left",padx=55)
    titulo1 = tk.Label(encabezado_frame, text="Will", font=("Inter", 24, "bold", "italic"), bg="#1B8A91", fg="#26B1A1")
    titulo1.pack(side="left",padx=0,pady=5)
    titulo2 = tk.Label(encabezado_frame, text="Ro", font=("Inter", 24, "bold", "italic"), bg="#1B8A91", fg="#E3E3E3")
    titulo2.pack(side="left",padx=0,pady=5)
    #Contenido de la ventana de Inicio de sesion
    etiqueta__titulo_inicio_de_sesion = tk.Label(ventana_inicio_de_sesion, text="Inicio de Sesión", font=("Inter", 24, "bold", "italic"), bg="#ECECEC", fg="#000000")
    etiqueta__titulo_inicio_de_sesion.pack(pady=10)
    espacio_mensaje_respuesta_inicio_sesion = tk.Label(ventana_inicio_de_sesion, text="", font=("Inter", 12, "bold"), bg="#ECECEC", fg="#B70000")
    espacio_mensaje_respuesta_inicio_sesion.pack()
    etiqueta_nombre_de_usuario = tk.Label(ventana_inicio_de_sesion, text="Nombre de usuario", font=("Inter", 16, "bold", "italic"), bg="#ECECEC", fg="#000000")
    etiqueta_nombre_de_usuario.pack(pady=5)
    entrada_nombre_de_usuario = tk.Entry(ventana_inicio_de_sesion, font=("Arial", 12), width=30)
    entrada_nombre_de_usuario.pack(pady=5)
    etiqueta_contrasena = tk.Label(ventana_inicio_de_sesion, text="Contraseña", font=("Inter", 16, "bold", "italic"), bg="#ECECEC", fg="#000000")
    etiqueta_contrasena.pack(pady=5)
    entrada_contrasena = tk.Entry(ventana_inicio_de_sesion, show='*', font=("Arial", 12), width=30)
    entrada_contrasena.pack(pady=10)
    #Botones de acciones "Iniciar Sesion" y "Regresar"
    boton_iniciar_sesion_validar = tk.Button(ventana_inicio_de_sesion, text="Iniciar Sesión", font=("Inter", 18, "bold", "italic"),bg="#15D1C5", fg="#000000", bd=0.25 ,activebackground="#00cccc", width=12, height=1, command=lambda: iniciar_sesion(entrada_nombre_de_usuario,entrada_contrasena,ventana_inicio_de_sesion))
    boton_iniciar_sesion_validar.pack(pady=0)
    espacio3 = tk.Label(ventana_inicio_de_sesion, text="", font=("Inter", 14, "bold"), bg="#ECECEC", fg="#ECECEC")
    espacio3.pack()
    boton_regresar = tk.Button(ventana_inicio_de_sesion, text="Regresar", font=("Inter", 18, "bold", "italic"),bg="#1B8A91", fg="#000000", bd=0.25 ,activebackground="#00cccc", width=12, height=1, command=lambda: regresar_a_ventana_inicio(ventana_inicio_de_sesion))
    boton_regresar.pack(pady=0)

def pantalla_crear_cuenta(parametros_ventana_inicio):
    #Variables globales
    global espacio_mensaje_respuesta_crear_cuenta
    #Ocultar la ventana de Inicio
    ventana_inicio.withdraw()
    #Creacion de la ventana de Crear cuenta
    posicion_ventana_inicio = parametros_ventana_inicio.winfo_geometry()
    ventana_crear_cuenta = tk.Toplevel()
    ventana_crear_cuenta.title("WillRo App")
    ventana_crear_cuenta.geometry("340x620")
    ventana_crear_cuenta.resizable(False, False)
    ventana_crear_cuenta.configure(bg="#ECECEC")
    ventana_crear_cuenta.protocol("WM_DELETE_WINDOW", cerrar_aplicacion)
    ventana_crear_cuenta.geometry(posicion_ventana_inicio)
    #Encabezado de la aplicacion
    encabezado_frame = tk.Frame(ventana_crear_cuenta, bg="#1B8A91", height=60)
    encabezado_frame.pack(fill="x")
    titulo0 = tk.Label(encabezado_frame, text="", font=("Inter", 24, "bold"), bg="#1B8A91", fg="#FFFFFF")
    titulo0.pack(side="left",padx=55)
    titulo1 = tk.Label(encabezado_frame, text="Will", font=("Inter", 24, "bold", "italic"), bg="#1B8A91", fg="#26B1A1")
    titulo1.pack(side="left",padx=0,pady=5)
    titulo2 = tk.Label(encabezado_frame, text="Ro", font=("Inter", 24, "bold", "italic"), bg="#1B8A91", fg="#E3E3E3")
    titulo2.pack(side="left",padx=0,pady=5)
    #Contenido de la ventana de Crear cuenta
    etiqueta_titulo_crear_cuenta = tk.Label(ventana_crear_cuenta, text="Crear Cuenta", font=("Inter", 24, "bold", "italic"), bg="#ECECEC", fg="#000000")
    etiqueta_titulo_crear_cuenta.pack(pady=10)
    espacio_mensaje_respuesta_crear_cuenta = tk.Label(ventana_crear_cuenta, text="", font=("Inter", 10, "bold"), bg="#ECECEC", fg="#B70000")
    espacio_mensaje_respuesta_crear_cuenta.pack()
    etiqueta_nombre_de_usuario = tk.Label(ventana_crear_cuenta, text="Nombre de usuario", font=("Inter", 16, "bold", "italic"), bg="#ECECEC", fg="#000000")
    etiqueta_nombre_de_usuario.pack(pady=5)
    entrada_nombre_de_usuario = tk.Entry(ventana_crear_cuenta, font=("Arial", 12), width=30)
    entrada_nombre_de_usuario.pack(pady=5)
    etiqueta_contrasena = tk.Label(ventana_crear_cuenta, text="Contraseña", font=("Inter", 16, "bold", "italic"), bg="#ECECEC", fg="#000000")
    etiqueta_contrasena.pack(pady=5)
    entrada_contrasena = tk.Entry(ventana_crear_cuenta, show='*', font=("Arial", 12), width=30)
    entrada_contrasena.pack(pady=5)
    etiqueta_repetir_contrasena = tk.Label(ventana_crear_cuenta, text="Repetir Contraseña", font=("Inter", 16, "bold", "italic"), bg="#ECECEC", fg="#000000")
    etiqueta_repetir_contrasena.pack(pady=5)
    entrada_repetir_contrasena = tk.Entry(ventana_crear_cuenta, show='*',  font=("Arial", 12), width=30)
    entrada_repetir_contrasena.pack(pady=10)
    #Botones de acciones "registrar cuenta" y "regresar"
    boton_registrar_cuenta = tk.Button(ventana_crear_cuenta, text="Registrarme", font=("Inter", 18, "bold", "italic"),bg="#15D1C5", fg="#000000", bd=0.25 ,activebackground="#00cccc", width=12, height=1, command=lambda: registrar_usuario(entrada_nombre_de_usuario,entrada_contrasena,entrada_repetir_contrasena))
    boton_registrar_cuenta.pack(pady=0)
    espacio1 = tk.Label(ventana_crear_cuenta, text="", font=("Inter", 14, "bold"), bg="#ECECEC", fg="#ECECEC")
    espacio1.pack()
    boton_regresar = tk.Button(ventana_crear_cuenta, text="Regresar", font=("Inter", 18, "bold", "italic"),bg="#1B8A91", fg="#000000", bd=0.25 ,activebackground="#00cccc", width=12, height=1, command=lambda: regresar_a_ventana_inicio(ventana_crear_cuenta))
    boton_regresar.pack(pady=0)

def pantalla_menu(parametros_ventana_inicio_de_sesion):
    #Ocultar la ventana de Inicio de sesion
    parametros_ventana_inicio_de_sesion.withdraw()
    #Creacion de la ventana de Menu
    posicion_ventana_inicio_de_sesion = parametros_ventana_inicio_de_sesion.winfo_geometry()
    ventana_menu = tk.Toplevel()
    ventana_menu.title("WillRo App")
    ventana_menu.geometry("340x620")
    ventana_menu.resizable(False, False)
    ventana_menu.configure(bg="#ECECEC")
    ventana_menu.protocol("WM_DELETE_WINDOW", cerrar_aplicacion)
    ventana_menu.geometry(posicion_ventana_inicio_de_sesion)
    #Encabezado de la aplicacion
    encabezado_frame = tk.Frame(ventana_menu, bg="#1B8A91", height=60)
    encabezado_frame.pack(fill="x")
    titulo0 = tk.Label(encabezado_frame, text="", font=("Inter", 24, "bold"), bg="#1B8A91", fg="#FFFFFF")
    titulo0.pack(side="left",padx=55)
    titulo1 = tk.Label(encabezado_frame, text="Will", font=("Inter", 24, "bold", "italic"), bg="#1B8A91", fg="#26B1A1")
    titulo1.pack(side="left",padx=0,pady=5)
    titulo2 = tk.Label(encabezado_frame, text="Ro", font=("Inter", 24, "bold", "italic"), bg="#1B8A91", fg="#E3E3E3")
    titulo2.pack(side="left",padx=0,pady=5)
    #Contenido de la ventana de Menu
    etiqueta_titulo_menu = tk.Label(ventana_menu, text="Menu", font=("Inter", 24, "bold", "italic"), bg="#ECECEC", fg="#000000")
    etiqueta_titulo_menu.pack(pady=10)
    etiqueta_nombre_de_usuario_menu = tk.Label(ventana_menu, text="", font=("Inter", 12, "bold", "italic"), bg="#EBEBEB", fg="#000000")
    etiqueta_nombre_de_usuario_menu.pack(pady=10)
    etiqueta_pregunta = tk.Label(ventana_menu, text="¿En que puedo ayudarte?", font=("Inter", 12, "bold", "italic"), bg="#EBEBEB", fg="#000000")
    etiqueta_pregunta.pack(pady=10)
    #Botones de acciones "Deteccion de contenido malicioso", "Historial de detecciones", "configuraciones" y "Cerrar Sesion"
    boton_deteccion_de_contenido_malicioso = tk.Button(ventana_menu, text="Deteccion de contenido malicioso", font=("Inter", 12, "bold", "italic"),bg="#15D1C5", fg="#000000", bd=0.25 ,activebackground="#00cccc", width=27, height=2, command=lambda: pantalla_deteccion_de_contenido_malicioso(ventana_menu))
    boton_deteccion_de_contenido_malicioso.pack(pady=0)
    espacio2 = tk.Label(ventana_menu, text="", font=("Inter", 14, "bold"), bg="#ECECEC", fg="#ECECEC")
    espacio2.pack()
    boton_historial_de_detecciones = tk.Button(ventana_menu, text="Historial de detecciones", font=("Inter", 12, "bold", "italic"),bg="#15D1C5", fg="#000000", bd=0.25 ,activebackground="#00cccc", width=27, height=2, command=lambda: pantalla_historial_de_detecciones(ventana_menu))
    boton_historial_de_detecciones.pack(pady=0)
    #Cargado de icono de Configuraciones
    imagen = Image.open('img/settings.png')
    imagen_resized = imagen.resize((50, 50))
    icono = ImageTk.PhotoImage(imagen_resized)
    boton_configuraciones = tk.Button(ventana_menu, text="", image=icono, compound="left",command=lambda: pantalla_configuraciones_cuenta_de_usuario(ventana_menu,etiqueta_nombre_de_usuario_menu))
    boton_configuraciones.image = icono
    boton_configuraciones.pack(pady=20)
    boton_cerrar_sesion = tk.Button(ventana_menu, text="Cerrar Sesion", font=("Inter", 12, "bold", "italic"),bg="#1B8A91", fg="#000000", bd=0.25 ,activebackground="#00cccc", width=27, height=2, command=lambda: regresar_a_ventana_inicio(ventana_menu))
    boton_cerrar_sesion.pack(pady=5)
    #Interaccion con la BD
    try:
        #Conexion a la BD
        conexion = pyodbc.connect(
        'Driver={ODBC Driver 17 for SQL Server};'
        'Server=tcp:servidordatosusuarios.database.windows.net,1433;'
        'Database=db_usuarios;'
        'Uid=Berl;'
        'Pwd=Trabajo123;'
        'Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'
        )
        #Creacion de un cursor para Querys
        cursor = conexion.cursor()
        #Query para traer el nombre del usuario usando de referencia la id del usuario que inicio sesion
        cursor.execute("SELECT usuario FROM Usuarios WHERE id = ?",(id_usuario))
        fila = cursor.fetchone()
        #Mostrar en pantalla al usuario su nombre de usuario
        etiqueta_nombre_de_usuario_menu.config(text="Hola de nuevo, "+fila[0])
        #Desconexion de la BD
        conexion.close()
    #De suceder cualquier error
    except pyodbc.IntegrityError:
        messagebox.showerror("Error", f"No se pudo encontrar el usuario con id: {e}")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo encontrar el usuario con id: {e}")

def pantalla_deteccion_de_contenido_malicioso(parametros_ventana_menu):
    #Ocultar la ventana de Menu
    parametros_ventana_menu.withdraw()
    #Creacion de la ventana de Deteccion de contenido malicioso
    posicion_ventana_menu = parametros_ventana_menu.winfo_geometry()
    ventana_deteccion_de_contenido_malicioso = tk.Toplevel()
    ventana_deteccion_de_contenido_malicioso.title("WillRo App")
    ventana_deteccion_de_contenido_malicioso.geometry("340x620")
    ventana_deteccion_de_contenido_malicioso.resizable(False, False)
    ventana_deteccion_de_contenido_malicioso.configure(bg="#ECECEC")
    ventana_deteccion_de_contenido_malicioso.protocol("WM_DELETE_WINDOW", cerrar_aplicacion)
    ventana_deteccion_de_contenido_malicioso.geometry(posicion_ventana_menu)
    #Encabezado de la aplicacion
    encabezado_frame = tk.Frame(ventana_deteccion_de_contenido_malicioso, bg="#1B8A91", height=60)
    encabezado_frame.pack(fill="x")
    titulo0 = tk.Label(encabezado_frame, text="", font=("Inter", 24, "bold"), bg="#1B8A91", fg="#FFFFFF")
    titulo0.pack(side="left",padx=55)
    titulo1 = tk.Label(encabezado_frame, text="Will", font=("Inter", 24, "bold", "italic"), bg="#1B8A91", fg="#26B1A1")
    titulo1.pack(side="left",padx=0,pady=5)
    titulo2 = tk.Label(encabezado_frame, text="Ro", font=("Inter", 24, "bold", "italic"), bg="#1B8A91", fg="#E3E3E3")
    titulo2.pack(side="left",padx=0,pady=5)
    #Contenido de la ventana de Deteccion de contenido malicioso
    etiqueta_titulo_deteccion_de_contenido_malicioso = tk.Label(ventana_deteccion_de_contenido_malicioso, text="Deteccion de \ncontenido malicioso", font=("Inter", 20, "bold", "italic"), bg="#ECECEC", fg="#000000")
    etiqueta_titulo_deteccion_de_contenido_malicioso.pack(pady=10)
    espacio_vacio = tk.Label(ventana_deteccion_de_contenido_malicioso, text="", font=("Inter", 12, "bold"), bg="#ECECEC", fg="#B70000")
    espacio_vacio.pack()
    espacio_vacio2 = tk.Label(ventana_deteccion_de_contenido_malicioso, text="", font=("Inter", 12, "bold"), bg="#ECECEC", fg="#B70000")
    espacio_vacio2.pack()
    boton_iniciar_deteccion = tk.Button(ventana_deteccion_de_contenido_malicioso, text="Iniciar Deteccion", font=("Inter", 12, "bold", "italic"),bg="#15D1C5", fg="#000000", bd=0.25 ,activebackground="#00cccc", width=27, height=2, command=lambda: pantalla_deteccion_fase_1(ventana_deteccion_de_contenido_malicioso))
    boton_iniciar_deteccion.pack(pady=0)
    espacio_vacio3 = tk.Label(ventana_deteccion_de_contenido_malicioso, text="", font=("Inter", 12, "bold"), bg="#ECECEC", fg="#ECECEC")
    espacio_vacio3.pack()
    espacio_vacio4 = tk.Label(ventana_deteccion_de_contenido_malicioso, text="", font=("Inter", 12, "bold"), bg="#ECECEC", fg="#ECECEC")
    espacio_vacio4.pack()
    boton_regresar = tk.Button(ventana_deteccion_de_contenido_malicioso, text="Regresar", font=("Inter", 12, "bold", "italic"),bg="#1B8A91", fg="#000000", bd=0.25 ,activebackground="#00cccc", width=27, height=2, command=lambda: regresar_a_ventana_menu(ventana_deteccion_de_contenido_malicioso,parametros_ventana_menu))
    boton_regresar.pack(pady=0)

def pantalla_deteccion_fase_1(parametros_ventana_deteccion_de_contenido_malicioso):
    #Ocultar la ventana de Deteccion de contenido malicioso
    parametros_ventana_deteccion_de_contenido_malicioso.withdraw()
    #Creacion de la ventana de Deteccion fase 1
    posicion_ventana_deteccion_de_contenido_malicioso = parametros_ventana_deteccion_de_contenido_malicioso.winfo_geometry()
    ventana_deteccion_fase_1 = tk.Toplevel()
    ventana_deteccion_fase_1.title("WillRo App")
    ventana_deteccion_fase_1.geometry("340x620")
    ventana_deteccion_fase_1.resizable(False, False)
    ventana_deteccion_fase_1.configure(bg="#ECECEC")
    ventana_deteccion_fase_1.protocol("WM_DELETE_WINDOW", cerrar_aplicacion)
    ventana_deteccion_fase_1.geometry(posicion_ventana_deteccion_de_contenido_malicioso)
    #Encabezado de la aplicacion
    encabezado_frame = tk.Frame(ventana_deteccion_fase_1, bg="#1B8A91", height=60)
    encabezado_frame.pack(fill="x")
    titulo0 = tk.Label(encabezado_frame, text="", font=("Inter", 24, "bold"), bg="#1B8A91", fg="#FFFFFF")
    titulo0.pack(side="left",padx=55)
    titulo1 = tk.Label(encabezado_frame, text="Will", font=("Inter", 24, "bold", "italic"), bg="#1B8A91", fg="#26B1A1")
    titulo1.pack(side="left",padx=0,pady=5)
    titulo2 = tk.Label(encabezado_frame, text="Ro", font=("Inter", 24, "bold", "italic"), bg="#1B8A91", fg="#E3E3E3")
    titulo2.pack(side="left",padx=0,pady=5)
    #Contenido de la ventana de Deteccion fase 1
    etiqueta_titulo_deteccion_de_contenido_malicioso = tk.Label(ventana_deteccion_fase_1, text="Deteccion de \ncontenido malicioso", font=("Inter", 20, "bold", "italic"), bg="#ECECEC", fg="#000000")
    etiqueta_titulo_deteccion_de_contenido_malicioso.pack(pady=10)
    etiqueta_fase_1 = tk.Label(ventana_deteccion_fase_1, text="Fase 1:", font=("Inter", 14, "bold", "italic"), bg="#ECECEC", fg="#000000")
    etiqueta_fase_1.pack(pady=4)
    etiqueta_texto = tk.Label(ventana_deteccion_fase_1, text="Captura de contenido \nde pantalla", font=("Inter", 14, "bold", "italic"), bg="#ECECEC", fg="#000000")
    etiqueta_texto.pack(pady=2)
    #Cargado de icono de Rpa
    imagen = Image.open('img/rpa.png')
    imagen_resized = imagen.resize((50, 50))
    icono = ImageTk.PhotoImage(imagen_resized)
    etiqueta_icono_rpa = tk.Label(ventana_deteccion_fase_1, text="", image=icono, compound="left")
    etiqueta_icono_rpa.image = icono
    etiqueta_icono_rpa.pack(pady=20)
    espacio_mensaje_respuesta_captura_de_pantalla = tk.Label(ventana_deteccion_fase_1, text="", font=("Inter", 8, "bold"), bg="#ECECEC", fg="#ECECEC")
    espacio_mensaje_respuesta_captura_de_pantalla.pack()
    etiqueta_ejecutando = tk.Label(ventana_deteccion_fase_1, text="Ejecutando...", font=("Inter", 16, "bold", "italic"), bg="#ECECEC", fg="#000000")
    etiqueta_ejecutando.pack(pady=2)
    #Funciones ejecutandose en cadena para realizar la captura de contenido y cambiar a la siguiente fase
    ventana_deteccion_fase_1.after(1000,lambda: minimizar_ventana_app(ventana_deteccion_fase_1))
    ventana_deteccion_fase_1.after(1500, lambda: captura_de_contenido_de_pantalla(espacio_mensaje_respuesta_captura_de_pantalla))
    ventana_deteccion_fase_1.after(2000, retornar_ventana_app)
    ventana_deteccion_fase_1.after(3000, lambda: pantalla_deteccion_fase_2(ventana_deteccion_fase_1, parametros_ventana_deteccion_de_contenido_malicioso))

def pantalla_deteccion_fase_2(parametros_ventana_deteccion_fase_1, parametros_ventana_deteccion_de_contenido_malicioso):
    #Ocultar la ventana de Deteccion Fase 1
    parametros_ventana_deteccion_fase_1.withdraw()
    #Creacion de la ventana de Deteccion fase 2
    posicion_ventana_deteccion_fase_1 = parametros_ventana_deteccion_fase_1.winfo_geometry()
    ventana_deteccion_fase_2 = tk.Toplevel()
    ventana_deteccion_fase_2.title("WillRo App")
    ventana_deteccion_fase_2.geometry("340x620")
    ventana_deteccion_fase_2.resizable(False, False)
    ventana_deteccion_fase_2.configure(bg="#ECECEC")
    ventana_deteccion_fase_2.protocol("WM_DELETE_WINDOW", cerrar_aplicacion)
    ventana_deteccion_fase_2.geometry(posicion_ventana_deteccion_fase_1)
    #La ventana de la app aparece minimizada con este comando se la vuelve a traer al frente
    ventana_deteccion_fase_2.after(1000, retornar_ventana_app)
    #Encabezado de la aplicacion
    encabezado_frame = tk.Frame(ventana_deteccion_fase_2, bg="#1B8A91", height=60)
    encabezado_frame.pack(fill="x")
    titulo0 = tk.Label(encabezado_frame, text="", font=("Inter", 24, "bold"), bg="#1B8A91", fg="#FFFFFF")
    titulo0.pack(side="left",padx=55)
    titulo1 = tk.Label(encabezado_frame, text="Will", font=("Inter", 24, "bold", "italic"), bg="#1B8A91", fg="#26B1A1")
    titulo1.pack(side="left",padx=0,pady=5)
    titulo2 = tk.Label(encabezado_frame, text="Ro", font=("Inter", 24, "bold", "italic"), bg="#1B8A91", fg="#E3E3E3")
    titulo2.pack(side="left",padx=0,pady=5)
    #Contenido de la ventana de Deteccion fase 2
    etiqueta_titulo_deteccion_de_contenido_malicioso = tk.Label(ventana_deteccion_fase_2, text="Deteccion de \ncontenido malicioso", font=("Inter", 20, "bold", "italic"), bg="#ECECEC", fg="#000000")
    etiqueta_titulo_deteccion_de_contenido_malicioso.pack(pady=10)
    etiqueta_fase_2 = tk.Label(ventana_deteccion_fase_2, text="Fase 2:", font=("Inter", 14, "bold", "italic"), bg="#ECECEC", fg="#000000")
    etiqueta_fase_2.pack(pady=4)
    etiqueta_texto = tk.Label(ventana_deteccion_fase_2, text="Analisis de la captura \nde contenido", font=("Inter", 14, "bold", "italic"), bg="#ECECEC", fg="#000000")
    etiqueta_texto.pack(pady=2)
    #Cargado de captura de pantalla
    imagen = Image.open('capturas/captura_chrome.png')
    imagen_resized = imagen.resize((340, 200))
    icono = ImageTk.PhotoImage(imagen_resized)
    etiqueta_captura_de_pantalla = tk.Label(ventana_deteccion_fase_2, text="", image=icono, compound="left")
    etiqueta_captura_de_pantalla.image = icono
    etiqueta_captura_de_pantalla.pack(pady=20)
    espacio_mensaje_respuesta_captura_de_pantalla = tk.Label(ventana_deteccion_fase_2, text="", font=("Inter", 8, "bold"), bg="#ECECEC", fg="#ECECEC")
    espacio_mensaje_respuesta_captura_de_pantalla.pack()
    etiqueta_ejecutando = tk.Label(ventana_deteccion_fase_2, text="Analizando...", font=("Inter", 16, "bold", "italic"), bg="#ECECEC", fg="#000000")
    etiqueta_ejecutando.pack(pady=2)
    #Funciones ejecutandose en cadena para realizar el analisis de la captura de contenido y cambiar a la siguiente fase
    ventana_deteccion_fase_2.after(1000, analisis_de_captura_de_contenido)
    ventana_deteccion_fase_2.after(3000, lambda: pantalla_deteccion_fase_3(ventana_deteccion_fase_2, parametros_ventana_deteccion_fase_1, parametros_ventana_deteccion_de_contenido_malicioso))

def pantalla_deteccion_fase_3(parametros_ventana_deteccion_fase_2, parametros_ventana_deteccion_fase_1, parametros_ventana_deteccion_de_contenido_malicioso):
    #Ocultar la ventana de Deteccion Fase 2
    parametros_ventana_deteccion_fase_2.withdraw()
    #Creacion de la ventana de Deteccion fase 3
    posicion_ventana_deteccion_fase_2 = parametros_ventana_deteccion_fase_2.winfo_geometry()
    ventana_deteccion_fase_3 = tk.Toplevel()
    ventana_deteccion_fase_3.title("WillRo App")
    ventana_deteccion_fase_3.geometry("340x620")
    ventana_deteccion_fase_3.resizable(False,False)
    ventana_deteccion_fase_3.configure(bg="#ECECEC")
    ventana_deteccion_fase_3.protocol("WM_DELETE_WINDOW", cerrar_aplicacion)
    ventana_deteccion_fase_3.geometry(posicion_ventana_deteccion_fase_2)
    #Encabezado de la aplicacion
    encabezado_frame = tk.Frame(ventana_deteccion_fase_3, bg="#1B8A91", height=60)
    encabezado_frame.pack(fill="x")
    titulo0 = tk.Label(encabezado_frame, text="", font=("Inter", 24, "bold"), bg="#1B8A91", fg="#FFFFFF")
    titulo0.pack(side="left",padx=55)
    titulo1 = tk.Label(encabezado_frame, text="Will", font=("Inter", 24, "bold", "italic"), bg="#1B8A91", fg="#26B1A1")
    titulo1.pack(side="left",padx=0,pady=5)
    titulo2 = tk.Label(encabezado_frame, text="Ro", font=("Inter", 24, "bold", "italic"), bg="#1B8A91", fg="#E3E3E3")
    titulo2.pack(side="left",padx=0,pady=5)
    #Contenido de la ventana de Deteccion fase 3
    etiqueta_titulo_deteccion_de_contenido_malicioso = tk.Label(ventana_deteccion_fase_3, text="Deteccion de \ncontenido malicioso", font=("Inter", 20, "bold", "italic"), bg="#ECECEC", fg="#000000")
    etiqueta_titulo_deteccion_de_contenido_malicioso.pack(pady=10)
    etiqueta_fase_3 = tk.Label(ventana_deteccion_fase_3, text="Fase 3:", font=("Inter", 14, "bold", "italic"), bg="#ECECEC", fg="#000000")
    etiqueta_fase_3.pack(pady=1)
    etiqueta_texto = tk.Label(ventana_deteccion_fase_3, text="Resultados", font=("Inter", 14, "bold", "italic"), bg="#ECECEC", fg="#000000")
    etiqueta_texto.pack(pady=1)
    #Cargado de captura de pantalla
    imagen = Image.open('resultado/deteccion_resultado.png')
    imagen_resized = imagen.resize((340, 200))
    icono = ImageTk.PhotoImage(imagen_resized)
    etiqueta_captura_de_pantalla = tk.Label(ventana_deteccion_fase_3, text="", image=icono, compound="left")
    etiqueta_captura_de_pantalla.image = icono
    etiqueta_captura_de_pantalla.pack(pady=5)
    #Condicion para cargar los resultados del analisis de la captura de contenido
    if mensaje_phishing_no_phishing == "No se encontro una pagina web":
        etiqueta_mensaje_phishing_no_phishing = tk.Label(ventana_deteccion_fase_3, text="", font=("Inter", 12, "bold", "italic"), bg="#ECECEC", fg="#000000")
        etiqueta_mensaje_phishing_no_phishing.pack(pady=0)
        etiqueta_mensaje_phishing_no_phishing.config(text=mensaje_phishing_no_phishing, fg="#B70000")
        boton_regresar = tk.Button(ventana_deteccion_fase_3, text="Regresar", font=("Inter", 12, "bold", "italic"),bg="#1B8A91", fg="#000000", bd=0.25 ,activebackground="#00cccc", width=27, height=1, command=lambda: regresar_a_ventana_deteccion_de_contenido_malicioso_no_resultados_deteccion(ventana_deteccion_fase_3,parametros_ventana_deteccion_fase_2, parametros_ventana_deteccion_fase_1, parametros_ventana_deteccion_de_contenido_malicioso))
        boton_regresar.pack(pady=5)
    else:
        canvas = tk.Canvas(ventana_deteccion_fase_3, width=220, height=100, bg="white")
        canvas.pack()
        #Valores del analisis
        valores = [porcentaje_phishing, porcentaje_no_phishing]
        etiquetas = ["P", "NP"]
        colores = ["red", "blue"]
        #Verifica si existe un valor 0
        if sum(valores) > 0:
            if valores[0] == 0:
                angulos = [0, 359.9]
                porcentajes = ["0%", "100%"]
            elif valores[1] == 0:
                angulos = [359.9, 0]
                porcentajes = ["100%", "0%"]
            else:
                total = sum(valores)
                angulos = [360 * valor / total for valor in valores]
                porcentajes = [f"{round(100 * valor / total)}%" for valor in valores]
        else:
            angulos = [0, 0]  #En el caso que ambos valores sean 0
            porcentajes = ["0%", "0%"]
        #Parametros de cordenadas del grafico
        x_centro, y_centro = 52, 52
        radio = 45
        #Dibujar el gráfico de pastel
        inicio = 0
        for i, angulo in enumerate(angulos):
            if angulo > 0:
                canvas.create_arc(
                    (x_centro - radio, y_centro - radio, x_centro + radio, y_centro + radio),
                    start=inicio,
                    extent=angulo,
                    fill=colores[i]
                )
                #Calcular posición del texto en el centro del círculo cuando uno de los valores es 100%
                if angulo == 359.9:
                    x, y = x_centro, y_centro
                else:
                    #Posicionar el texto en el centro del sector/segmento
                    angulo_medio = math.radians(inicio + angulo / 2)
                    x = x_centro + 0.6 * radio * math.cos(angulo_medio)
                    y = y_centro - 0.6 * radio * math.sin(angulo_medio)
            
                canvas.create_text(x, y, text=f"{etiquetas[i]} {porcentajes[i]}", fill="white", font=("Arial", 7, "bold"))
            
            inicio += angulo
        #Creacion de la leyenda
        leyenda_x = 110
        leyenda_y = 37
        espacio_vertical = 20
        for i in range(2):
            #Dibujar el cuadro de color
            canvas.create_rectangle(
                leyenda_x, leyenda_y + i * espacio_vertical,
                leyenda_x + 10, leyenda_y + 10 + i * espacio_vertical,
                fill=colores[i]
            )
            #Dibujar el texto de la etiqueta
            canvas.create_text(
                leyenda_x + 20, leyenda_y + 5 + i * espacio_vertical,
                text="Phishing" if i == 0 else "No Phishing",
                anchor="w",
                font=("Arial", 10)
            )
            #Boton para continuar a la siguiente fase
        boton_continuar = tk.Button(ventana_deteccion_fase_3, text="Continuar", font=("Inter", 12, "bold", "italic"),bg="#15D1C5", fg="#000000", bd=0.25 ,activebackground="#00cccc", width=27, height=1, command=lambda: pantalla_deteccion_fase_4(ventana_deteccion_fase_3, parametros_ventana_deteccion_fase_2, parametros_ventana_deteccion_fase_1, parametros_ventana_deteccion_de_contenido_malicioso))
        boton_continuar.pack(pady=5)

def pantalla_deteccion_fase_4(parametros_ventana_deteccion_fase_3, parametros_ventana_deteccion_fase_2, parametros_ventana_deteccion_fase_1, parametros_ventana_deteccion_de_contenido_malicioso):
    #Variable global
    global amenaza
    global texto_recomendacion_1
    global texto_recomendacion_2
    global texto_recomendacion_3
    texto_recomendacion_1 = ""
    texto_recomendacion_2 = ""
    texto_recomendacion_3 = ""
    #Ocultar la ventana de Deteccion Fase 3
    parametros_ventana_deteccion_fase_3.withdraw()
    #Creacion de la ventana de Deteccion fase 4
    posicion_ventana_deteccion_fase_3 = parametros_ventana_deteccion_fase_3.winfo_geometry()
    ventana_deteccion_fase_4 = tk.Toplevel()
    ventana_deteccion_fase_4.title("WillRo App")
    ventana_deteccion_fase_4.geometry("340x620")
    ventana_deteccion_fase_4.resizable(False,False)
    ventana_deteccion_fase_4.configure(bg="#ECECEC")
    ventana_deteccion_fase_4.protocol("WM_DELETE_WINDOW", cerrar_aplicacion)
    ventana_deteccion_fase_4.geometry(posicion_ventana_deteccion_fase_3)
    #Encabezado de la aplicacion
    encabezado_frame = tk.Frame(ventana_deteccion_fase_4, bg="#1B8A91", height=60)
    encabezado_frame.pack(fill="x")
    titulo0 = tk.Label(encabezado_frame, text="", font=("Inter", 24, "bold"), bg="#1B8A91", fg="#FFFFFF")
    titulo0.pack(side="left",padx=55)
    titulo1 = tk.Label(encabezado_frame, text="Will", font=("Inter", 24, "bold", "italic"), bg="#1B8A91", fg="#26B1A1")
    titulo1.pack(side="left",padx=0,pady=5)
    titulo2 = tk.Label(encabezado_frame, text="Ro", font=("Inter", 24, "bold", "italic"), bg="#1B8A91", fg="#E3E3E3")
    titulo2.pack(side="left",padx=0,pady=5)
    #Contenido de la ventana de Deteccion fase 4
    etiqueta_titulo_deteccion_de_contenido_malicioso = tk.Label(ventana_deteccion_fase_4, text="Deteccion de \ncontenido malicioso", font=("Inter", 20, "bold", "italic"), bg="#ECECEC", fg="#000000")
    etiqueta_titulo_deteccion_de_contenido_malicioso.pack(pady=10)
    etiqueta_fase_4 = tk.Label(ventana_deteccion_fase_4, text="Fase 4:", font=("Inter", 14, "bold", "italic"), bg="#ECECEC", fg="#000000")
    etiqueta_fase_4.pack(pady=1)
    etiqueta_texto = tk.Label(ventana_deteccion_fase_4, text="Recomendaciones", font=("Inter", 14, "bold", "italic"), bg="#ECECEC", fg="#000000")
    etiqueta_texto.pack(pady=1)
    if porcentaje_phishing == 0:
        etiqueta_recomendacion_1 = tk.Label(ventana_deteccion_fase_4, text="-Continue navegando \npero con cuidado,\nsiga realizando otras detecciones \nde ser necesario", font=("Inter", 12, "bold", "italic"), bg="#ECECEC", fg="#000000")
        etiqueta_recomendacion_1.pack(pady=2)
        texto_recomendacion_1 = etiqueta_recomendacion_1.cget("text")
        amenaza = "No Phishing"
    if porcentaje_phishing > 0:
        etiqueta_recomendacion_2 = tk.Label(ventana_deteccion_fase_4, text="-Cerrar las cuentas relacionadas \na esa pagina web ", font=("Inter", 12, "bold", "italic"), bg="#ECECEC", fg="#000000")
        etiqueta_recomendacion_2.pack(pady=2)
        etiqueta_recomendacion_3 = tk.Label(ventana_deteccion_fase_4, text="-Revisar si la pagina \ninteractua con otra ", font=("Inter", 12, "bold", "italic"), bg="#ECECEC", fg="#000000")
        etiqueta_recomendacion_3.pack()
        etiqueta_recomendacion_4 = tk.Label(ventana_deteccion_fase_4, text="-Revisar si se ha descargado \nalgun archivo ", font=("Inter", 12, "bold", "italic"), bg="#ECECEC", fg="#000000")
        etiqueta_recomendacion_4.pack()
        texto_recomendacion_1 = etiqueta_recomendacion_2.cget("text")
        texto_recomendacion_2 = etiqueta_recomendacion_2.cget("text")
        texto_recomendacion_3 = etiqueta_recomendacion_2.cget("text")
        amenaza = "Phishing"
    boton_regresar_y_guardar = tk.Button(ventana_deteccion_fase_4, text="Regresar y guardar", font=("Inter", 12, "bold", "italic"),bg="#1B8A91", fg="#000000", bd=0.25 ,activebackground="#00cccc", width=27, height=1, command=lambda: regresar_a_ventana_deteccion_de_contenido_malicioso_y_guardar_deteccion(ventana_deteccion_fase_4,parametros_ventana_deteccion_fase_3 ,parametros_ventana_deteccion_fase_2, parametros_ventana_deteccion_fase_1, parametros_ventana_deteccion_de_contenido_malicioso))
    boton_regresar_y_guardar.pack(pady=5)

def pantalla_historial_de_detecciones(parametros_ventana_menu):
    obtener_detecciones()
    #Variable global
    global tabla_detecciones
    #Ocultar la ventana de Menu
    parametros_ventana_menu.withdraw()
    #Creacion de la ventana de Deteccion de contenido malicioso
    posicion_ventana_menu = parametros_ventana_menu.winfo_geometry()
    ventana_historial_de_detecciones = tk.Toplevel()
    ventana_historial_de_detecciones.title("WillRo App")
    ventana_historial_de_detecciones.geometry("340x620")
    ventana_historial_de_detecciones.resizable(False, False)
    ventana_historial_de_detecciones.configure(bg="#ECECEC")
    ventana_historial_de_detecciones.protocol("WM_DELETE_WINDOW", cerrar_aplicacion)
    ventana_historial_de_detecciones.geometry(posicion_ventana_menu)
    #Encabezado de la aplicacion
    encabezado_frame = tk.Frame(ventana_historial_de_detecciones, bg="#1B8A91", height=60)
    encabezado_frame.pack(fill="x")
    titulo0 = tk.Label(encabezado_frame, text="", font=("Inter", 24, "bold"), bg="#1B8A91", fg="#FFFFFF")
    titulo0.pack(side="left",padx=55)
    titulo1 = tk.Label(encabezado_frame, text="Will", font=("Inter", 24, "bold", "italic"), bg="#1B8A91", fg="#26B1A1")
    titulo1.pack(side="left",padx=0,pady=5)
    titulo2 = tk.Label(encabezado_frame, text="Ro", font=("Inter", 24, "bold", "italic"), bg="#1B8A91", fg="#E3E3E3")
    titulo2.pack(side="left",padx=0,pady=5)
    #Contenido de la ventana de Historial de detecciones
    etiqueta_titulo_historial_de_detecciones = tk.Label(ventana_historial_de_detecciones, text="Historial de \ndetecciones", font=("Inter", 20, "bold", "italic"), bg="#ECECEC", fg="#000000")
    etiqueta_titulo_historial_de_detecciones.pack(pady=10)
    espacio_vacio = tk.Label(ventana_historial_de_detecciones, text="", font=("Inter", 12, "bold"), bg="#ECECEC", fg="#B70000")
    espacio_vacio.pack()
    boton_regresar = tk.Button(ventana_historial_de_detecciones, text="Regresar", font=("Inter", 12, "bold", "italic"),bg="#1B8A91", fg="#000000", bd=0.25 ,activebackground="#00cccc", width=27, height=2, command=lambda: regresar_a_ventana_menu(ventana_historial_de_detecciones,parametros_ventana_menu))
    boton_regresar.pack(pady=5)
    columnas = ("Fecha", "Hora", "Amenaza", "UrlResult", "Recomendacion_1", "Recomendacion_2", "Recomendacion_3")
    frame = tk.Frame(ventana_historial_de_detecciones)
    frame.pack(fill=tk.BOTH, expand=True)
    tabla_detecciones = ttk.Treeview(frame, columns=columnas, show="headings")
    tabla_detecciones.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    def obtener_ruta_chrome():
        try:
            # Acceder a la clave del registro de Google Chrome
            registry_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, registry_path) as key:
                chrome_path, _ = winreg.QueryValueEx(key, None)
                return chrome_path
        except FileNotFoundError:
            print("No se encontró Google Chrome en el registro.")
            return None
    def abrir_url(event):
        # Obtener el ítem seleccionado en el Treeview
        item = tabla_detecciones.selection()
        if item:
            url = tabla_detecciones.item(item, "values")[3]  # Suponiendo que la URL está en la columna 2 (col2)
            if url.startswith("http"):  # Verificar que la URL comienza con http:// o https://
                chrome_path = obtener_ruta_chrome()  # Obtener la ruta de Google Chrome
                if chrome_path:
                    # Ejecutar el proceso en un hilo separado
                    threading.Thread(target=ejecutar_chrome, args=(chrome_path, url)).start()
                else:
                    print("Google Chrome no está instalado o no se encontró la ruta.")
    def ejecutar_chrome(chrome_path, url):
        try:
            subprocess.run([chrome_path, url], check=True)
        except Exception as e:
            print("Error al abrir Google Chrome:", e)
    for columna in columnas:
        tabla_detecciones.heading(columna, text=columna)
    scrollbar_horizontal = ttk.Scrollbar(frame, orient="horizontal", command=tabla_detecciones.xview)
    scrollbar_horizontal.pack(side=tk.TOP, fill=tk.X)
    tabla_detecciones.configure(xscrollcommand=scrollbar_horizontal.set)
    tabla_detecciones.column("Fecha",width=85,stretch=tk.NO)
    tabla_detecciones.column("Hora",width=75,stretch=tk.NO)
    tabla_detecciones.column("Amenaza",width=90,stretch=tk.NO)
    tabla_detecciones.column("UrlResult",width=140,stretch=tk.NO)
    tabla_detecciones.column("Recomendacion_1",width=140,stretch=tk.NO)
    tabla_detecciones.column("Recomendacion_2",width=140,stretch=tk.NO)
    tabla_detecciones.column("Recomendacion_3",width=140,stretch=tk.YES)
    
    #Conexion a la BD
    conexion = pyodbc.connect(
    'Driver={ODBC Driver 17 for SQL Server};'
    'Server=tcp:servidordatosusuarios.database.windows.net,1433;'
    'Database=db_usuarios;'
    'Uid=Berl;'
    'Pwd=Trabajo123;'
    'Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'
    )
    #Creacion del cursor para la Query
    cursor = conexion.cursor()
    #Query para obtener el id fecha y hora de la deteccion
    cursor.execute("SELECT fecha, hora, amenaza, url_resultado, recomendaciones_1, recomendaciones_2, recomendaciones_3 FROM detecciones WHERE id_usuario = ?",(id_usuario))
    filas = cursor.fetchall()
    cursor.close()
    matriz = [list(fila) for fila in filas]
    for fila in matriz:
        tabla_detecciones.insert("", tk.END, values=fila)
    tabla_detecciones.bind("<ButtonRelease-1>", abrir_url)

def pantalla_configuraciones_cuenta_de_usuario(parametros_ventana_menu, etiqueta_nombre_de_usuario_menu, parametros_ventana_actualizar_datos=None):

    #Condicion para validar si el ingreso a la pantalla de configuraciones es desde la ventana de menu o desde la ventana de actualizar datos despues de cambiar algun dato
    if parametros_ventana_actualizar_datos is not None:
        parametros_ventana_menu.withdraw()
        posicion_ventana_adicional = parametros_ventana_actualizar_datos.winfo_geometry()
        ventana_configuraciones = tk.Toplevel()
        ventana_configuraciones.title("WillRo App")
        ventana_configuraciones.geometry("340x620")
        ventana_configuraciones.resizable(False, False) 
        ventana_configuraciones.configure(bg="#ECECEC")
        ventana_configuraciones.protocol("WM_DELETE_WINDOW", cerrar_aplicacion)
        ventana_configuraciones.geometry(posicion_ventana_adicional)
    else:
        #Ocultar la ventana de menu
        parametros_ventana_menu.withdraw()
        #Creacion de la ventana de Configuraciones
        posicion_ventana_menu = parametros_ventana_menu.winfo_geometry()
        ventana_configuraciones = tk.Toplevel()
        ventana_configuraciones.title("WillRo App")
        ventana_configuraciones.geometry("340x520")
        ventana_configuraciones.resizable(False, False) 
        ventana_configuraciones.configure(bg="#ECECEC")
        ventana_configuraciones.protocol("WM_DELETE_WINDOW", cerrar_aplicacion)
        ventana_configuraciones.geometry(posicion_ventana_menu)
    #Encabezado superior del titulo de la aplicacion
    encabezado_frame = tk.Frame(ventana_configuraciones, bg="#1B8A91", height=60)
    encabezado_frame.pack(fill="x")
    titulo0 = tk.Label(encabezado_frame, text="", font=("Inter", 24, "bold"), bg="#1B8A91", fg="#FFFFFF")
    titulo0.pack(side="left",padx=55)
    titulo1 = tk.Label(encabezado_frame, text="Will", font=("Inter", 24, "bold", "italic"), bg="#1B8A91", fg="#26B1A1")
    titulo1.pack(side="left",padx=0,pady=5)
    titulo2 = tk.Label(encabezado_frame, text="Ro", font=("Inter", 24, "bold", "italic"), bg="#1B8A91", fg="#E3E3E3")
    titulo2.pack(side="left",padx=0,pady=5)
    #Contenido de la ventana de configuraciones
    etiqueta_titulo_cuenta_de_usuario = tk.Label(ventana_configuraciones, text="Cuenta de \nusuario", font=("Inter", 24, "bold", "italic"), bg="#ECECEC", fg="#000000")
    etiqueta_titulo_cuenta_de_usuario.pack(pady=10)
    etiqueta_nombre_de_usuario_configuraciones = tk.Label(ventana_configuraciones, text="Nombre de usuario: ", font=("Inter", 12, "bold", "italic"), bg="#EBEBEB", fg="#000000")
    etiqueta_nombre_de_usuario_configuraciones.pack(pady=10)
    espacio = tk.Label(ventana_configuraciones, text="", font=("Inter", 12, "bold"), bg="#ECECEC", fg="#ECECEC")
    espacio.pack()
    boton_actualizar_datos = tk.Button(ventana_configuraciones, text="Actualizar Datos", font=("Inter", 12, "bold", "italic"),bg="#15D1C5", fg="#000000", bd=0.25 ,activebackground="#00cccc", width=27, height=2, command=lambda: pantalla_actualizar_datos(ventana_configuraciones,parametros_ventana_menu,etiqueta_nombre_de_usuario_menu))
    boton_actualizar_datos.pack(pady=5)
    boton_borrar_cuenta = tk.Button(ventana_configuraciones, text="Borrar Cuenta", font=("Inter", 12, "bold", "italic"),bg="#15D1C5", fg="#000000", bd=0.25 ,activebackground="#00cccc", width=27, height=2, command=lambda: pantalla_borrar_cuenta(ventana_configuraciones,parametros_ventana_menu))
    boton_borrar_cuenta.pack(pady=5)
    boton_regresar = tk.Button(ventana_configuraciones, text="Regresar", font=("Inter", 12, "bold", "italic"),bg="#1B8A91", fg="#000000", bd=0.25 ,activebackground="#00cccc", width=27, height=2, command=lambda: regresar_a_ventana_menu(ventana_configuraciones,parametros_ventana_menu))
    boton_regresar.pack(pady=5)
    #Interaccion de la BD
    try:
        #Conexion de BD
        conexion = pyodbc.connect(
        'Driver={ODBC Driver 17 for SQL Server};'
        'Server=tcp:servidordatosusuarios.database.windows.net,1433;'
        'Database=db_usuarios;'
        'Uid=Berl;'
        'Pwd=Trabajo123;'
        'Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'
        )
        #Creacion de un cursor para Querys
        cursor = conexion.cursor()
        #Query para traer el nombre del usuario usando de referencia la id del usuario que inicio sesion
        cursor.execute("SELECT usuario FROM Usuarios WHERE id = ?",(id_usuario))
        fila = cursor.fetchone()
        #Mostrar en pantalla al usuario su nombre de usuario
        etiqueta_nombre_de_usuario_configuraciones.config(text="Nombre de usuario: "+fila[0])
        #Desconexion de la BD
        conexion.close()
    #De suceder cualquier error
    except pyodbc.IntegrityError:
        messagebox.showerror("Error", f"No se pudo encontrar el usuario con id: {e}")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo encontrar el usuario con id: {e}")
        
def pantalla_actualizar_datos(parametros_ventana_configuraciones,parametros_ventana_menu,etiqueta_nombre_de_usuario_menu):
    #Variables globales
    global espacio_mensaje_respuesta_actualizar_datos
    #Ocultar la ventana de configuraciones
    parametros_ventana_configuraciones.withdraw()
    #Creacion de la ventana de actualizar datos
    posicion_ventana_configuraciones = parametros_ventana_configuraciones.winfo_geometry()
    ventana_actualizar_datos = tk.Toplevel()
    ventana_actualizar_datos.title("WillRo App")
    ventana_actualizar_datos.geometry("340x620")
    ventana_actualizar_datos.resizable(False, False)
    ventana_actualizar_datos.configure(bg="#ECECEC")
    ventana_actualizar_datos.protocol("WM_DELETE_WINDOW", cerrar_aplicacion)
    ventana_actualizar_datos.geometry(posicion_ventana_configuraciones)
    #Encabezado superior del titulo de la aplicacion
    encabezado_frame = tk.Frame(ventana_actualizar_datos, bg="#1B8A91", height=60)
    encabezado_frame.pack(fill="x")
    titulo0 = tk.Label(encabezado_frame, text="", font=("Inter", 24, "bold"), bg="#1B8A91", fg="#FFFFFF")
    titulo0.pack(side="left",padx=55)
    titulo1 = tk.Label(encabezado_frame, text="Will", font=("Inter", 24, "bold", "italic"), bg="#1B8A91", fg="#26B1A1")
    titulo1.pack(side="left",padx=0,pady=5)
    titulo2 = tk.Label(encabezado_frame, text="Ro", font=("Inter", 24, "bold", "italic"), bg="#1B8A91", fg="#E3E3E3")
    titulo2.pack(side="left",padx=0,pady=5)
    #Contenido de la ventana de actualizar datos
    etiqueta_titulo_actualizar_datos = tk.Label(ventana_actualizar_datos, text="Actualizar \nDatos", font=("Inter", 24, "bold", "italic"), bg="#ECECEC", fg="#000000")
    etiqueta_titulo_actualizar_datos.pack(pady=10)
    espacio_mensaje_respuesta_actualizar_datos = tk.Label(ventana_actualizar_datos, text="", font=("Inter", 12, "bold"), bg="#ECECEC", fg="#B70000")
    espacio_mensaje_respuesta_actualizar_datos.pack()
    etiqueta_nombre_de_usuario_actualizar = tk.Label(ventana_actualizar_datos, text="Nombre de usuario", font=("Inter", 16, "bold", "italic"), bg="#ECECEC", fg="#000000")
    etiqueta_nombre_de_usuario_actualizar.pack(pady=10)
    entrada_nombre_de_usuario = tk.Entry(ventana_actualizar_datos, font=("Arial", 12), width=30)
    entrada_nombre_de_usuario.pack(pady=10)
    etiqueta_contrasena = tk.Label(ventana_actualizar_datos, text="Contraseña", font=("Inter", 16, "bold", "italic"), bg="#ECECEC", fg="#000000")
    etiqueta_contrasena.pack(pady=10)
    #Parametro alterado para evitar mostrar la contraeña en pantalla directamente
    entrada_contrasena = tk.Entry(ventana_actualizar_datos, show='*', font=("Arial", 12), width=30)
    entrada_contrasena.pack(pady=10)
    #Interaccion con la BD
    try:
        #Conexion de la BD
        conexion = pyodbc.connect(
        'Driver={ODBC Driver 17 for SQL Server};'
        'Server=tcp:servidordatosusuarios.database.windows.net,1433;'
        'Database=db_usuarios;'
        'Uid=Berl;'
        'Pwd=Trabajo123;'
        'Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'
        )
        #Creacion de los cursores para Querys
        cursor = conexion.cursor()
        cursor2 = conexion.cursor()
        #Query para traer el nombre de usuario usando de referencia la id del usuario que inicio sesion
        cursor.execute("SELECT usuario FROM Usuarios WHERE id = ?",(id_usuario))
        fila = cursor.fetchone()
        #Insertar el nombre en la entrada en pantalla correspondiente al nombre de usuario
        entrada_nombre_de_usuario.insert(0,fila[0])
        #Query para traer la contraseña de usuario usando de referencia la id del usuario que inicio sesion
        cursor2.execute("SELECT contrasena FROM Usuarios WHERE id = ?",(id_usuario))
        fila2 = cursor2.fetchone()
        #Insertar el nombre en la entrada en pantalla correspondiente la contraseña
        entrada_contrasena.insert(0,fila2[0])
        conexion.close()
    except pyodbc.IntegrityError:
        messagebox.showerror("Error", f"No se pudo encontrar el usuario con id: {e}")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo encontrar el usuario con id: {e}")
    boton_actualizar = tk.Button(ventana_actualizar_datos, text="Actualizar", font=("Inter", 12, "bold", "italic"),bg="#15D1C5", fg="#000000", bd=0.25 ,activebackground="#00cccc", width=27, height=2, command=lambda: actualizar_usuario(fila[0],fila2[0],entrada_nombre_de_usuario,entrada_contrasena,etiqueta_nombre_de_usuario_actualizar,ventana_actualizar_datos,parametros_ventana_configuraciones,parametros_ventana_menu,etiqueta_nombre_de_usuario_menu))
    boton_actualizar.pack(pady=5)
    boton_regresar = tk.Button(ventana_actualizar_datos, text="Regresar", font=("Inter", 12, "bold", "italic"),bg="#1B8A91", fg="#000000", bd=0.25 ,activebackground="#00cccc", width=27, height=2, command=lambda: regresar_a_ventana_configuraciones(ventana_actualizar_datos,parametros_ventana_configuraciones))
    boton_regresar.pack(pady=5)

def pantalla_borrar_cuenta(parametros_ventana_configuraciones,parametros_ventana_menu):
    #Ocultar la ventana de configuraciones
    parametros_ventana_configuraciones.withdraw()
    #Creacion de la ventana de actualizar datos
    posicion_ventana_configuraciones = parametros_ventana_configuraciones.winfo_geometry()
    ventana_borrar_cuenta = tk.Toplevel()
    ventana_borrar_cuenta.title("WillRo App")
    ventana_borrar_cuenta.geometry("340x620")
    ventana_borrar_cuenta.resizable(False, False)
    ventana_borrar_cuenta.configure(bg="#ECECEC")
    ventana_borrar_cuenta.protocol("WM_DELETE_WINDOW", cerrar_aplicacion)
    ventana_borrar_cuenta.geometry(posicion_ventana_configuraciones)
    #Encabezado superior del titulo de la aplicacion
    encabezado_frame = tk.Frame(ventana_borrar_cuenta, bg="#1B8A91", height=60)
    encabezado_frame.pack(fill="x")
    titulo0 = tk.Label(encabezado_frame, text="", font=("Inter", 24, "bold"), bg="#1B8A91", fg="#FFFFFF")
    titulo0.pack(side="left",padx=55)
    titulo1 = tk.Label(encabezado_frame, text="Will", font=("Inter", 24, "bold", "italic"), bg="#1B8A91", fg="#26B1A1")
    titulo1.pack(side="left",padx=0,pady=5)
    titulo2 = tk.Label(encabezado_frame, text="Ro", font=("Inter", 24, "bold", "italic"), bg="#1B8A91", fg="#E3E3E3")
    titulo2.pack(side="left",padx=0,pady=5)
    #Contenido de la ventana de borrar cuenta
    etiqueta_titulo_borrar_cuenta = tk.Label(ventana_borrar_cuenta, text="Borrar \nCuenta", font=("Inter", 24, "bold", "italic"), bg="#ECECEC", fg="#000000")
    etiqueta_titulo_borrar_cuenta.pack(pady=10)
    espacio_1 = tk.Label(ventana_borrar_cuenta, text="", font=("Inter", 12, "bold"), bg="#ECECEC", fg="#B70000")
    espacio_1.pack()
    espacio_2 = tk.Label(ventana_borrar_cuenta, text="", font=("Inter", 12, "bold"), bg="#ECECEC", fg="#B70000")
    espacio_2.pack()
    etiqueta_confirmacion_borrar_buenta = tk.Label(ventana_borrar_cuenta, text="¿Seguro que quiere borrar \nsu cuenta de usuario?", font=("Inter", 12, "bold"), bg="#ECECEC", fg="#000000")
    etiqueta_confirmacion_borrar_buenta.pack()
    espacio_3 = tk.Label(ventana_borrar_cuenta, text="", font=("Inter", 12, "bold"), bg="#ECECEC", fg="#B70000")
    espacio_3.pack()
    espacio_4 = tk.Label(ventana_borrar_cuenta, text="", font=("Inter", 12, "bold"), bg="#ECECEC", fg="#B70000")
    espacio_4.pack()
    boton_borrar_cuenta = tk.Button(ventana_borrar_cuenta, text="Borrar Cuenta", font=("Inter", 12, "bold", "italic"),bg="#15D1C5", fg="#000000", bd=0.25 ,activebackground="#00cccc", width=27, height=2, command=lambda: borrar_cuenta(ventana_borrar_cuenta))
    boton_borrar_cuenta.pack(pady=5)
    boton_regresar = tk.Button(ventana_borrar_cuenta, text="Regresar", font=("Inter", 12, "bold", "italic"),bg="#1B8A91", fg="#000000", bd=0.25 ,activebackground="#00cccc", width=27, height=2, command=lambda: regresar_a_ventana_configuraciones(ventana_borrar_cuenta,parametros_ventana_configuraciones))
    boton_regresar.pack(pady=5)


#Retornos de pantallas de la aplicacion
def regresar_a_ventana_inicio(ventana):
    pos_x = ventana.winfo_x()
    pos_y = ventana.winfo_y()
    ventana.destroy()
    ventana_inicio.geometry(f"+{pos_x}+{pos_y}")
    ventana_inicio.deiconify()

def regresar_a_ventana_menu(ventana,ventana_menu):
    pos_x = ventana.winfo_x()
    pos_y = ventana.winfo_y()
    ventana.destroy()
    ventana_menu.geometry(f"+{pos_x}+{pos_y}")
    ventana_menu.deiconify()

def regresar_a_ventana_configuraciones(ventana,ventana_configuraciones):
    pos_x = ventana.winfo_x()
    pos_y = ventana.winfo_y()
    ventana.destroy()
    ventana_configuraciones.geometry(f"+{pos_x}+{pos_y}")
    ventana_configuraciones.deiconify()

def regresar_a_ventana_deteccion_de_contenido_malicioso_no_resultados_deteccion(ventana, ventana_deteccion_fase_2, ventana_deteccion_fase_1, ventana_deteccion_de_contenido_malicioso):
    pos_x = ventana.winfo_x()
    pos_y = ventana.winfo_y()
    ventana.destroy()
    ventana_deteccion_fase_2.destroy()
    ventana_deteccion_fase_1.destroy()
    ventana_deteccion_de_contenido_malicioso.geometry(f"+{pos_x}+{pos_y}")
    ventana_deteccion_de_contenido_malicioso.deiconify()

def regresar_a_ventana_deteccion_de_contenido_malicioso_y_guardar_deteccion(ventana, ventana_deteccion_fase_3, ventana_deteccion_fase_2, ventana_deteccion_fase_1, ventana_deteccion_de_contenido_malicioso):
    almacenamiento_de_la_deteccion()
    pos_x = ventana.winfo_x()
    pos_y = ventana.winfo_y()
    ventana.destroy()
    ventana_deteccion_fase_3.destroy()
    ventana_deteccion_fase_2.destroy()
    ventana_deteccion_fase_1.destroy()
    ventana_deteccion_de_contenido_malicioso.geometry(f"+{pos_x}+{pos_y}")
    ventana_deteccion_de_contenido_malicioso.deiconify()
    #Aqui Iria el guardar en BD en simultaneo

#Creacion de la ventana de inicio al iniciar la aplicacion
ventana_inicio = tk.Tk()
ventana_inicio.title("WillRo App")
ventana_inicio.geometry("340x620")
ventana_inicio.resizable(False, False)
ventana_inicio.configure(bg="#ECECEC")
ventana_inicio.protocol("WM_DELETE_WINDOW", cerrar_aplicacion)
#Contenido de la ventana de inicio
#Encabezado de la aplicacion
encabezado_frame = tk.Frame(ventana_inicio, bg="#1B8A91", height=60)
encabezado_frame.pack(fill="x")
titulo0 = tk.Label(encabezado_frame, text="", font=("Inter", 24, "bold"), bg="#1B8A91", fg="#FFFFFF")
titulo0.pack(side="left",padx=55)
titulo1 = tk.Label(encabezado_frame, text="Will", font=("Inter", 24, "bold", "italic"), bg="#1B8A91", fg="#26B1A1")
titulo1.pack(side="left",padx=0,pady=5)
titulo2 = tk.Label(encabezado_frame, text="Ro", font=("Inter", 24, "bold", "italic"), bg="#1B8A91", fg="#E3E3E3")
titulo2.pack(side="left",padx=0,pady=5)
#Cuerpo de la ventana de Inicio de la aplicacion
etiqueta_bienvenida = tk.Label(ventana_inicio, text="¡Bienvenido!", font=("Inter", 28, "bold", "italic"), bg="#ECECEC", fg="#000000")
etiqueta_bienvenida.pack(pady=20)
espacio0 = tk.Label(ventana_inicio, text="", font=("Inter", 24, "bold"), bg="#ECECEC", fg="#ECECEC")
espacio0.pack()
#Botones de acciones "Iniciar Sesion" y "Registrarse"
contenido_frame = tk.Frame(ventana_inicio, bg="#1B8A91", height=80)
contenido_frame.pack()
boton_iniciar_sesion = tk.Button(contenido_frame, text="Iniciar Sesion", font=("Inter", 18, "bold", "italic"),bg="#15D1C5", fg="#000000", bd=0.25 ,activebackground="#00cccc", width=12, height=1, command=lambda: pantalla_inicio_de_sesion(ventana_inicio))
boton_iniciar_sesion.pack(pady=0)
espacio = tk.Label(ventana_inicio, text="", font=("Inter", 24, "bold"), bg="#ECECEC", fg="#ECECEC")
espacio.pack()
contenido_frame2 = tk.Frame(ventana_inicio, bg="#1B8A91", height=80)
contenido_frame2.pack()
boton_registrarse = tk.Button(contenido_frame2, text="Registrarse", font=("Inter", 18, "bold", "italic"),bg="#15D1C5", fg="#000000", bd=0.25 ,activebackground="#00cccc", width=12, height=1, command=lambda: pantalla_crear_cuenta(ventana_inicio))
boton_registrarse.pack(pady=0)
#Ejecucion de la ventana de inicio / Ejecucion del bucle de la aplicacion
ventana_inicio.mainloop()