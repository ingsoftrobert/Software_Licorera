from tkinter import *
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from config import guardar_usuario, cargar_usuario  # Importar las funciones de config.py
from container import Container  # Importar la clase Container

class Login(tk.Frame):
    def __init__(self, padre, controlador):
        super().__init__(padre)
        self.controlador = controlador
        self.pack(fill=BOTH, expand=True)
        self.widgets()
        self.cargar_usuario()  # Cargar el usuario y la pista al iniciar
        self.bind('<Return>', lambda event: self.login())  # Vincular la tecla Enter al método login

    def widgets(self):
        # Frame izquierdo para la imagen
        frame1 = tk.Frame(self, bg="#E6D9E3", highlightthickness=1, highlightbackground="black")
        frame1.pack(side=LEFT, fill=BOTH, expand=True)

        # Aquí puedes agregar un widget para mostrar una imagen en frame1
        # Por ejemplo: self.imagen = tk.Label(frame1, image=imagen)
        # self.imagen.pack()

        # Frame derecho para los campos de login
        frame2 = tk.Frame(self, bg="#E6D9E3", highlightthickness=1, highlightbackground="black")
        frame2.pack(side=RIGHT, fill=BOTH, expand=True)

        # Título del login
        titulo = tk.Label(frame2, text="LOGIN", font=("Arial", 16, "bold"), bg="#5B5A56", fg="#F0E6D2", anchor="center")
        titulo.pack(pady=20)

        # Campo para Usuario
        label_usuario = tk.Label(frame2, text="Usuario", font=("Helvetica", 12, "bold"), bg="#E6D9E3", fg="#010A13")
        label_usuario.pack(pady=10)
        self.entry_usuario = ttk.Entry(frame2, font=("Helvetica", 12))
        self.entry_usuario.pack(pady=10)

        # Campo para Contraseña
        label_contrasena = tk.Label(frame2, text="Contraseña", font=("Helvetica", 12, "bold"), bg="#E6D9E3", fg="#010A13")
        label_contrasena.pack(pady=10)
        self.entry_contrasena = ttk.Entry(frame2, font=("Helvetica", 12), show="*")
        self.entry_contrasena.pack(pady=10)

        # Checkbox para recordar contraseña
        self.recordar_var = tk.IntVar()
        self.checkbox_recordar = tk.Checkbutton(frame2, text="Recordar contraseña", variable=self.recordar_var, bg="#E6D9E3", font=("Helvetica", 10))
        self.checkbox_recordar.pack(pady=10)

        # Campo para la pista de la contraseña
        label_pista = tk.Label(frame2, text="Pista para recordar la contraseña", font=("Helvetica", 12, "bold"), bg="#E6D9E3", fg="#010A13")
        label_pista.pack(pady=10)
        self.entry_pista = ttk.Entry(frame2, font=("Helvetica", 12))
        self.entry_pista.pack(pady=10)

        # Botón de login
        self.btn_login = tk.Button(frame2, text="Login", command=self.login, font=("Helvetica", 12, "bold"))
        self.btn_login.pack(pady=20)

    def login(self):
        usuario = self.entry_usuario.get()
        contrasena = self.entry_contrasena.get()
        recordar = self.recordar_var.get()
        pista = self.entry_pista.get()

        # Conectar a la base de datos
        conn = sqlite3.connect('licoreria.db')
        cursor = conn.cursor()

        # Verificar las credenciales
        cursor.execute("SELECT * FROM usuarios WHERE usuario=? AND contrasena=?", (usuario, contrasena))
        resultado = cursor.fetchone()

        if resultado:
            messagebox.showinfo("Login exitoso", "Bienvenido")
            if recordar:
                # Guardar el usuario y la pista en un archivo de configuración
                guardar_usuario(usuario, pista)
            self.controlador.show_frame(Container)
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos")

        # Cerrar la conexión
        conn.close()

    def cargar_usuario(self):
        # Cargar el usuario y la pista desde un archivo de configuración
        usuario, pista = cargar_usuario()
        self.entry_usuario.insert(0, usuario)
        self.entry_pista.insert(0, pista)
