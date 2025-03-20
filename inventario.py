from tkinter import *
import tkinter as tk
from tkinter import ttk, messagebox
import database  # Importar el módulo database
import locale

# Configurar el formato de moneda para pesos colombianos
locale.setlocale(locale.LC_ALL, 'es_CO.UTF-8')


class Inventario(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.config(bg="#E6D9E3")
        database.crear_tablas()  # Crear tablas si no existen
        self.widgets()
        self.cargar_datos()

    def widgets(self):
        # Frame superior con título
        frame_titulo = tk.Frame(self, bg="#4CAF50", height=30)  # Color verde del botón Inventario
        frame_titulo.pack(fill=X)
        tk.Label(
            frame_titulo,
            text="INVENTARIO",
            font=("Arial", 16, "bold"),
            bg="#4CAF50",  # Color verde del botón Inventario
            fg="#0A0A0A"   # Color negro para el texto
        ).pack(pady=5)

        # Frame de formulario
        frame_form = tk.Frame(self, bg="#E6D9E3", padx=10, pady=10)
        frame_form.pack(side=LEFT, fill=Y)

        campos = [
            ("Producto", "entry_producto"),
            ("Precio por Unidad", "entry_precio"),
            ("Cantidad", "entry_cantidad")
        ]

        self.entries = {}
        for idx, (text, key) in enumerate(campos):
            tk.Label(frame_form, text=text, bg="#E6D9E3", font=("Helvetica", 10)).grid(row=idx, column=0, sticky=W, pady=5)
            entry = ttk.Entry(frame_form, font=("Helvetica", 10), width=25)
            entry.grid(row=idx, column=1, padx=5, pady=5)
            self.entries[key] = entry

        # Frame de botones
        frame_botones = tk.Frame(frame_form, bg="#E6D9E3")
        frame_botones.grid(row=3, columnspan=2, pady=10)

        botones = [
            ("Agregar", "#4CAF50", self.agregar_producto),
            ("Eliminar", "#f44336", self.eliminar_producto),
            ("Limpiar", "#9E9E9E", self.limpiar_campos)
        ]

        for text, color, command in botones:
            tk.Button(frame_botones, text=text, bg=color, fg="white",
                      font=("Helvetica", 10, "bold"), command=command).pack(side=LEFT, padx=5)

        # Frame para mostrar el valor total
        frame_total = tk.Frame(frame_form, bg="#E6D9E3")
        frame_total.grid(row=5, columnspan=2, pady=10)

        tk.Label(frame_total, text="Valor Total de Productos:", bg="#E6D9E3", font=("Helvetica", 10, "bold")).pack(side=LEFT, padx=5)
        self.label_total = tk.Label(frame_total, text="0", bg="#E6D9E3", font=("Helvetica", 10, "bold"), fg="green")
        self.label_total.pack(side=LEFT, padx=5)

        # Frame de tabla
        frame_tabla = tk.Frame(self, bg="#E6D9E3")
        frame_tabla.pack(side=RIGHT, fill=BOTH, expand=True, padx=15, pady=10)

        # Configurar grid en el frame_tabla
        frame_tabla.grid_rowconfigure(0, weight=1)
        frame_tabla.grid_columnconfigure(0, weight=1)

        # Treeview
        self.tree = ttk.Treeview(frame_tabla, columns=("id", "producto", "precio", "cantidad", "total"),
                                 show="headings", selectmode="browse")
        self.tree.grid(row=0, column=0, sticky="nsew")

        # Configurar encabezados
        encabezados = [
            ("ID", 50),
            ("Producto", 200),
            ("Precio por Unidad", 150),
            ("Cantidad", 100),
            ("Total", 150)
        ]

        for idx, (texto, ancho) in enumerate(encabezados, start=1):
            self.tree.heading(f"#{idx}", text=texto, anchor=tk.CENTER)
            self.tree.column(f"#{idx}", width=ancho, minwidth=ancho, anchor=tk.CENTER)

        self.tree.heading("precio", text="Precio Unitario")
        self.tree.heading("total", text="Valor Total")

        # Scrollbars
        scrol_y = ttk.Scrollbar(frame_tabla, orient=tk.VERTICAL, command=self.tree.yview)
        scrol_y.grid(row=0, column=1, sticky="ns")

        scrol_x = ttk.Scrollbar(frame_tabla, orient=tk.HORIZONTAL, command=self.tree.xview)
        scrol_x.grid(row=1, column=0, sticky="ew")

        self.tree.configure(yscrollcommand=scrol_y.set, xscrollcommand=scrol_x.set)

        # Evento para editar celdas
        self.tree.bind("<Double-1>", self.editar_celda)

        # Modificar la forma en que se muestran los valores
        def mostrar_producto(producto):
            return self.tree.insert("", tk.END, values=(
                producto[0],
                producto[1],
                (producto[2]),  # Precio
                producto[3],
                (producto[4])   # Total
            ))

        # Actualizar el valor total del inventario
        def actualizar_total_inventario():
            total = database.obtener_valor_total_inventario()
            self.lbl_total_inventario.config(
                text=f"Valor Total del Inventario: {(total)}"
            )

    def cargar_datos(self):
        self.tree.delete(*self.tree.get_children())
        try:
            productos = database.obtener_inventario()
            for producto in productos:
                self.tree.insert("", tk.END, values=producto)
            self.actualizar_valor_total()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los datos: {e}")

    def agregar_producto(self):
        datos = [entry.get().strip() for entry in self.entries.values()]

        if not all(datos):
            messagebox.showwarning("Campos vacíos", "Todos los campos son obligatorios")
            return

        try:
            # Validar y convertir los datos
            producto = datos[0]
            precio = int(datos[1].replace(".", ""))  # Eliminar puntos y convertir a entero
            cantidad = int(datos[2])  # Convertir a entero
            total = precio * cantidad

            # Insertar el producto en la base de datos
            database.insertar_producto(producto, precio, cantidad, total)

            # Reasignar IDs en caso de que sea necesario
            database.reasignar_ids_inventario()

            # Recargar los datos en la tabla
            self.cargar_datos()

            # Limpiar los campos del formulario
            self.limpiar_campos()

            # Mostrar mensaje de éxito
            messagebox.showinfo("Éxito", "Producto agregado correctamente")
        except ValueError:
            messagebox.showwarning("Datos inválidos", "Precio y Cantidad deben ser números enteros")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo agregar el producto: {e}")

    def eliminar_producto(self):
        seleccionado = self.tree.selection()
        if not seleccionado:
            messagebox.showwarning("Advertencia", "Seleccione un registro para eliminar")
            return

        id_producto = self.tree.item(seleccionado)['values'][0]

        if messagebox.askyesno("Confirmar eliminación", "¿Está seguro de eliminar este producto?"):
            try:
                database.eliminar_producto_por_id(id_producto)
                database.reasignar_ids_inventario()
                self.cargar_datos()
                self.limpiar_campos()
                messagebox.showinfo("Éxito", "Producto eliminado correctamente")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar el producto: {e}")

    def editar_celda(self, event):
        item = self.tree.selection()[0]
        valores = self.tree.item(item, 'values')

        # Cargar los valores en el formulario
        self.entries['entry_producto'].delete(0, tk.END)
        self.entries['entry_producto'].insert(0, valores[1])
        self.entries['entry_precio'].delete(0, tk.END)
        self.entries['entry_precio'].insert(0, valores[2].strip("$").replace(".", "").replace(",", ""))
        self.entries['entry_cantidad'].delete(0, tk.END)
        self.entries['entry_cantidad'].insert(0, valores[3].replace(".", ""))

        # Crear ventana emergente para editar
        columna = self.tree.identify_column(event.x)
        columna_texto = self.tree.heading(columna)['text']

        if columna_texto in ["ID", "Total"]:  # No permitir editar ID ni Total
            return

        columnas_db = {
            "Producto": "producto",
            "Cantidad": "cantidad",
            "Precio por Unidad": "precio"
        }

        columna_db = columnas_db.get(columna_texto)
        if not columna_db:
            return

        valor_actual = self.tree.item(item, 'values')[int(columna[1:]) - 1]

        # Crear ventana emergente
        popup = tk.Toplevel()
        popup.title(f"Editar {columna_texto}")
        popup.geometry("300x100")

        tk.Label(popup, text=f"Nuevo valor para {columna_texto}:").pack(pady=5)
        nuevo_valor = ttk.Entry(popup, width=25)
        nuevo_valor.pack(pady=5)
        nuevo_valor.insert(0, valor_actual.strip("$").replace(".", "").replace(",", ""))

        def guardar_cambios():
            try:
                nuevo_valor_texto = nuevo_valor.get().strip()

                # Validar si es un número solo para cantidad y precio
                if columna_texto in ["Cantidad", "Precio por Unidad"]:
                    valor_numerico = int(nuevo_valor_texto)  # Validar como entero
                else:
                    valor_numerico = nuevo_valor_texto  # Permitir texto para el nombre del producto

                id_producto = self.tree.item(item, 'values')[0]
                # Actualizar solo el campo editado
                database.actualizar_producto(id_producto, columna_db, valor_numerico)

                # Recalcular total si es cantidad o precio
                if columna_texto in ["Cantidad", "Precio por Unidad"]:
                    datos_actuales = database.obtener_producto_por_id(id_producto)
                    nueva_cantidad = valor_numerico if columna_texto == "Cantidad" else datos_actuales[3]
                    nuevo_precio = valor_numerico if columna_texto == "Precio por Unidad" else datos_actuales[2]
                    nuevo_total = nueva_cantidad * nuevo_precio
                    database.actualizar_producto(id_producto, "total", nuevo_total)

                self.cargar_datos()
                popup.destroy()
                messagebox.showinfo("Éxito", "Actualización exitosa")
            except ValueError:
                if columna_texto in ["Cantidad", "Precio por Unidad"]:
                    messagebox.showerror("Error", "Debe ingresar un número entero válido")
                else:
                    messagebox.showerror("Error", "Debe ingresar un valor válido")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo actualizar el producto: {e}")

        tk.Button(popup, text="Guardar", command=guardar_cambios, bg="#4CAF50", fg="white").pack(pady=10)

    def actualizar_valor_total(self):
        try:
            total = database.obtener_valor_total_inventario()
            self.label_total.config(text=f"${total:,.0f}".replace(",", "."))  # Formato entero
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo calcular el valor total: {e}")

    def limpiar_campos(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)

    def cargar_formulario_desde_tabla(self, event):
        item_seleccionado = self.tree.selection()
        if item_seleccionado:
            valores = self.tree.item(item_seleccionado)['values']
            self.entries['entry_producto'].delete(0, tk.END)
            self.entries['entry_producto'].insert(0, valores[1])
            self.entries['entry_precio'].delete(0, tk.END)
            self.entries['entry_precio'].insert(0, valores[2].strip("$").replace(".", "").replace(",", ""))
            self.entries['entry_cantidad'].delete(0, tk.END)
            self.entries['entry_cantidad'].insert(0, valores[3].replace(".", ""))

    def buscar_producto(self):
        criterio = self.entry_busqueda.get().strip()
        if not criterio:
            messagebox.showwarning("Campo vacío", "Ingrese un criterio de búsqueda")
            return

        try:
            resultados = database.buscar_producto(criterio)

            # Limpiar tabla
            self.tree.delete(*self.tree.get_children())

            # Insertar resultados en la tabla
            for producto in resultados:
                self.tree.insert("", tk.END, values=producto)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo realizar la búsqueda: {e}")

    def actualizar_sugerencias(self, event):
        criterio = self.entry_busqueda.get().strip()
        if not criterio:
            self.entry_busqueda['values'] = []
            return

        query = "SELECT producto || ' - ' || precio || ' - ' || cantidad FROM inventario WHERE producto LIKE ? OR precio LIKE ? OR cantidad LIKE ?"
        parametros = (f"%{criterio}%", f"%{criterio}%", f"%{criterio}%")
        resultados = self.ejecutar_consulta(query, parametros).fetchall()

        sugerencias = [resultado[0] for resultado in resultados]
        self.entry_busqueda['values'] = sugerencias
        if sugerencias:
            self.entry_busqueda.event_generate('<Down>')

    def seleccionar_producto(self, event):
        seleccion = self.entry_busqueda.get()
        if not seleccion:
            return

        partes = seleccion.split(' - ')
        producto = partes[0]

        query = "SELECT * FROM inventario WHERE producto = ?"
        producto = self.ejecutar_consulta(query, (producto,)).fetchone()

        if producto:
            for item in self.tree.get_children():
                if self.tree.item(item, 'values')[1] == producto[1]:
                    self.tree.selection_set(item)
                    self.tree.focus(item)
                    self.tree.see(item)
                    self.cargar_formulario_desde_tabla(None)
                    break

    def mostrar_producto(self, producto):
        return self.tree.insert("", tk.END, values=(
            producto[0],
            producto[1],
            producto[2],  # Precio
            producto[3],
            producto[4]   # Total
        ))

    def actualizar_total_inventario(self):
        total = database.obtener_valor_total_inventario()
        self.lbl_total_inventario.config(
            text=f"Valor Total del Inventario: {(total)}"
        )

    def cargar_productos(self):
        # Limpiar la tabla
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            productos = database.obtener_inventario()
            for producto in productos:
                self.tree.insert("", tk.END, values=(
                    producto[0],  # id
                    producto[1],  # producto
                    producto[2],  # precio (sin formato)
                    producto[3],  # cantidad
                    producto[4]   # total (sin formato)
                ))

            # Actualizar el total sin formato
            total = database.obtener_valor_total_inventario()
            self.lbl_total_inventario.config(text=f"Valor Total del Inventario: ${total}")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los productos: {e}")
