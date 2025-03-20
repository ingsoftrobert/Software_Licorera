from tkinter import *
import tkinter as tk
from ventas import Ventas
from inventario import Inventario
from clientes import Clientes
from deudas import Deudas

class Container(tk.Frame):
    def __init__(self, padre, controlador):
        # Inicializa la clase base Frame
        super().__init__(padre)
        self.controlador = controlador
        # Configura el frame
        self.pack()
        self.place(x=0, y=0, width=1024, height=576)
        self.configure(bg="#E6D9E3")
        self.widgets()
        self.frames = {}
        self.buttons = []
        for i in (Ventas, Inventario, Clientes, Deudas):
            frame = i(self)
            self.frames[i] = frame
            frame.pack()
            frame.place(x=0, y=30, width=1024, height=576)
        self.show_frames(Ventas)

    def show_frames(self, container):
        frame = self.frames[container]
        frame.tkraise()

    def ventas(self):
        self.show_frames(Ventas)

    def inventario(self):
        self.show_frames(Inventario)

    def clientes(self):
        self.show_frames(Clientes)

    def deudas(self):
        self.show_frames(Deudas)

    def widgets(self):
        frame1 = tk.Frame(self, bg="#C6D9E3")
        frame1.pack()
        frame1.place(x=0, y=0, width=1024, height=576)

        # Configuración de la fuente
        fuente_boton = ("Helvetica", 12, "bold")

        # Ancho de cada botón
        ancho_boton = 1024 // 4

        # Configuración de los botones con texto centrado
        self.btnventas = Button(
            frame1,
            bg="#2196F3",
            fg="#FFFFFF",
            text="Ventas",
            command=self.ventas,
            font=fuente_boton,
            anchor='center',  # Alineación central
            padx=0,           # Sin padding horizontal
            pady=0            # Sin padding vertical
        )
        self.btnventas.place(x=0, y=0, width=ancho_boton, height=30)

        self.btninventario = Button(
            frame1,
            bg="#4CAF50",
            fg="#FFFFFF",
            text="Inventario",
            command=self.inventario,
            font=fuente_boton,
            anchor='center',
            padx=0,
            pady=0
        )
        self.btninventario.place(x=ancho_boton, y=0, width=ancho_boton, height=30)

        self.btnclientes = Button(
            frame1,
            bg="#FF9800",
            fg="#FFFFFF",
            text="Clientes",
            command=self.clientes,
            font=fuente_boton,
            anchor='center',
            padx=0,
            pady=0
        )
        self.btnclientes.place(x=ancho_boton * 2, y=0, width=ancho_boton, height=30)

        self.btndeudas = Button(
            frame1,
            bg="#F44336",
            fg="#FFFFFF",
            text="Deudas",
            command=self.deudas,
            font=fuente_boton,
            anchor='center',
            padx=0,
            pady=0
        )
        self.btndeudas.place(x=ancho_boton * 3, y=0, width=ancho_boton, height=30)
