from tkinter import *
import tkinter as tk
from tkinter import ttk, messagebox
import database
import sqlite3

class Clientes(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.config(bg="#E6D9E3")
        self.widgets()
        self.cargar_datos()

    def widgets(self):
        # Frame superior con título
        frame_titulo = tk.Frame(self, bg="#FF9800", height=30)  # Color naranja del botón Clientes
        frame_titulo.pack(fill=X)
        tk.Label(
            frame_titulo,
            text="GESTIÓN DE CLIENTES",
            font=("Arial", 16, "bold"),
            bg="#FF9800",  # Color naranja del botón Clientes
            fg="#0A0A0A"   # Color negro para el texto
        ).pack(pady=5)

        # Frame de formulario
        frame_form = tk.Frame(self, bg="#E6D9E3", padx=10, pady=10)
        frame_form.pack(side=LEFT, fill=Y)

        campos = [
            ("Nombres", "entry_nombres"),
            ("Apellidos", "entry_apellidos"),
            ("Cédula", "entry_cedula"),
            ("Celular", "entry_celular"),
            ("Zona", "entry_zona")
        ]

        self.entries = {}
        for idx, (text, key) in enumerate(campos):
            tk.Label(frame_form, text=text, bg="#E6D9E3", font=("Helvetica", 10)).grid(row=idx, column=0, sticky=W, pady=5)
            entry = ttk.Entry(frame_form, font=("Helvetica", 10), width=25)
            entry.grid(row=idx, column=1, padx=5, pady=5)
            self.entries[key] = entry

        # Frame de botones
        frame_botones = tk.Frame(frame_form, bg="#E6D9E3")
        frame_botones.grid(row=5, columnspan=2, pady=10)

        botones = [
            ("Agregar", "#4CAF50", self.agregar_cliente),
            ("Eliminar", "#f44336", self.eliminar_cliente),
            ("Limpiar", "#9E9E9E", self.limpiar_campos)
        ]

        for text, color, command in botones:
            tk.Button(frame_botones, text=text, bg=color, fg="white",
                      font=("Helvetica", 10, "bold"), command=command).pack(side=LEFT, padx=5)

        # Frame de búsqueda
        frame_busqueda = tk.Frame(frame_form, bg="#E6D9E3")
        frame_busqueda.grid(row=6, columnspan=2, pady=10)

        tk.Label(frame_busqueda, text="Buscar:", bg="#E6D9E3", font=("Helvetica", 10)).pack(side=LEFT, padx=5)
        self.entry_busqueda = ttk.Combobox(frame_busqueda, font=("Helvetica", 10), width=20)
        self.entry_busqueda.pack(side=LEFT, padx=5)
        self.entry_busqueda.bind('<KeyRelease>', self.actualizar_sugerencias)
        self.entry_busqueda.bind('<<ComboboxSelected>>', self.seleccionar_cliente)

        tk.Button(frame_busqueda, text="Buscar", bg="#2196F3", fg="white",
                  font=("Helvetica", 10, "bold"), command=self.buscar_cliente).pack(side=LEFT, padx=5)

        # Tabla de clientes
        frame_tabla = tk.Frame(self, bg="#E6D9E3")
        frame_tabla.pack(side=RIGHT, fill=BOTH, expand=True, padx=5, pady=5)

        self.tree = ttk.Treeview(frame_tabla, columns=("id", "nombres", "apellidos", "cedula", "celular", "zona"),
                                 show="headings", selectmode="browse")

        # Definir las columnas con sus identificadores y anchos
        columnas = [
            ("id", "ID", 50),
            ("nombres", "Nombres", 150),
            ("apellidos", "Apellidos", 150),
            ("cedula", "Cédula", 100),
            ("celular", "Celular", 100),
            ("zona", "Zona", 100)
        ]

        # Configurar encabezados y columnas
        for col_id, col_text, width in columnas:
            self.tree.heading(col_id, text=col_text)  # Usar el identificador correcto
            self.tree.column(col_id, width=width, anchor=CENTER)

        scroll = ttk.Scrollbar(frame_tabla, orient=VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scroll.set)
        scroll.pack(side=RIGHT, fill=Y)
        self.tree.pack(fill=BOTH, expand=True)

        # Eventos
        self.tree.bind("<<TreeviewSelect>>", self.cargar_formulario_desde_tabla)
        self.tree.bind("<Double-1>", self.editar_celda)

    # --------------------------
    # Funciones de base de datos
    # --------------------------
    def cargar_datos(self):
        # Limpiar tabla
        self.tree.delete(*self.tree.get_children())

        try:
            # Obtener datos de los clientes
            clientes = database.obtener_clientes()

            # Insertar en tabla
            for cliente in clientes:
                self.tree.insert("", END, values=cliente)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los datos: {e}")

    # --------------------------
    # Funciones CRUD
    # --------------------------
    def agregar_cliente(self):
        datos = [entry.get().strip() for entry in self.entries.values()]

        if not all(datos):
            messagebox.showwarning("Campos vacíos", "Todos los campos son obligatorios")
            return

        if not datos[2].isdigit() or not datos[3].isdigit():
            messagebox.showwarning("Datos inválidos", "Cédula y celular deben ser numéricos")
            return

        try:
            database.insertar_cliente(*datos)
            database.reasignar_ids_clientes()
            self.cargar_datos()
            self.limpiar_campos()
            messagebox.showinfo("Éxito", "Cliente agregado correctamente")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo agregar el cliente: {e}")

    def eliminar_cliente(self):
        item_seleccionado = self.tree.selection()
        if not item_seleccionado:
            messagebox.showwarning("Selección requerida", "Seleccione un cliente de la tabla")
            return

        id_cliente = self.tree.item(item_seleccionado)['values'][0]

        if messagebox.askyesno("Confirmar eliminación", "¿Está seguro de eliminar este cliente?"):
            try:
                database.eliminar_cliente_por_id(id_cliente)
                database.reasignar_ids_clientes()
                self.cargar_datos()
                self.limpiar_campos()
                messagebox.showinfo("Éxito", "Cliente eliminado correctamente")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar el cliente: {e}")

    def editar_celda(self, event):
        columna = self.tree.identify_column(event.x)
        item = self.tree.selection()[0]
        columna_texto = self.tree.heading(columna)['text']

        if columna_texto == "ID":  # No permitir editar ID
            return

        # Mapeo de nombres de columnas visuales a nombres de columnas en la base de datos
        columnas_db = {
            "Nombres": "nombres",
            "Apellidos": "apellidos",
            "Cédula": "cedula",
            "Celular": "celular",
            "Zona": "zona"
        }

        columna_db = columnas_db.get(columna_texto)
        if not columna_db:
            messagebox.showerror("Error", "No se puede editar esta columna")
            return

        valor_actual = self.tree.item(item, 'values')[int(columna[1:]) - 1]

        # Crear ventana emergente
        popup = tk.Toplevel()
        popup.title("Editar valor")
        popup.geometry("300x100")

        tk.Label(popup, text=f"Nuevo valor para {columna_texto}:").pack(pady=5)
        nuevo_valor = ttk.Entry(popup, width=25)
        nuevo_valor.pack(pady=5)
        nuevo_valor.insert(0, valor_actual)

        def guardar_cambios():
            nuevo_valor_texto = nuevo_valor.get().strip()

            if not nuevo_valor_texto:
                messagebox.showwarning("Valor vacío", "El nuevo valor no puede estar vacío")
                return

            try:
                id_cliente = self.tree.item(item, 'values')[0]
                database.actualizar_cliente(id_cliente, columna_db, nuevo_valor_texto)

                # Actualizar en la tabla
                valores = list(self.tree.item(item, 'values'))
                valores[int(columna[1:]) - 1] = nuevo_valor_texto
                self.tree.item(item, values=valores)

                popup.destroy()
                messagebox.showinfo("Éxito", f"El valor de {columna_texto} se actualizó correctamente")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo actualizar el valor: {e}")

        # Botón para guardar cambios
        tk.Button(popup, text="Guardar", command=guardar_cambios, bg="#4CAF50", fg="white").pack(pady=15)

    def buscar_cliente(self):
        criterio = self.entry_busqueda.get().strip()
        if not criterio:
            messagebox.showwarning("Campo vacío", "Ingrese un criterio de búsqueda")
            return

        try:
            resultados = database.buscar_cliente(criterio)

            # Limpiar tabla
            self.tree.delete(*self.tree.get_children())

            # Insertar resultados en la tabla
            for cliente in resultados:
                self.tree.insert("", END, values=cliente)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo realizar la búsqueda: {e}")

    def actualizar_sugerencias(self, event):
        criterio = self.entry_busqueda.get().strip()
        if not criterio:
            self.entry_busqueda['values'] = []
            return

        query = "SELECT nombres || ' ' || apellidos || ' - ' || cedula FROM clientes WHERE nombres LIKE ? OR apellidos LIKE ? OR cedula LIKE ?"
        parametros = (f"%{criterio}%", f"%{criterio}%", f"%{criterio}%")
        resultados = database.ejecutar_consulta(query, parametros)

        sugerencias = [resultado[0] for resultado in resultados]
        self.entry_busqueda['values'] = sugerencias
        if sugerencias:
            self.entry_busqueda.event_generate('<Down>')

    def seleccionar_cliente(self, event):
        seleccion = self.entry_busqueda.get()
        if not seleccion:
            return

        partes = seleccion.split(' - ')
        cedula = partes[-1]

        query = "SELECT * FROM clientes WHERE cedula = ?"
        cliente = database.ejecutar_consulta(query, (cedula,))

        if cliente:
            for item in self.tree.get_children():
                if self.tree.item(item, 'values')[2] == cedula:
                    self.tree.selection_set(item)
                    self.tree.focus(item)
                    self.tree.see(item)
                    self.cargar_formulario_desde_tabla(None)
                    break

    def limpiar_campos(self):
        for entry in self.entries.values():
            entry.delete(0, END)

    def cargar_formulario_desde_tabla(self, event):
        item_seleccionado = self.tree.selection()
        if item_seleccionado:
            valores = self.tree.item(item_seleccionado)['values']
            for entry, valor in zip(self.entries.values(), valores[1:]):
                entry.delete(0, END)
                entry.insert(0, valor)
