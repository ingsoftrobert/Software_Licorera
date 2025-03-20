import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import database
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import locale
import os
from tkinter import filedialog  # Añadir al inicio del archivo

# Configurar el formato de moneda para pesos colombianos
locale.setlocale(locale.LC_ALL, 'es_CO.UTF-8')

class Ventas(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack()
        self.widgets()

    def widgets(self):
        # Configuración del frame superior
        frame1 = tk.Frame(self, bg="#2196F3", highlightthickness=1, highlightbackground="black")
        frame1.pack()
        frame1.place(x=0, y=0, width=1100, height=30)

        # Título de la ventana
        titulo = tk.Label(
            self,
            text="VENTAS",
            font=("Arial", 16, "bold"),
            bg="#2196F3",  # Color azul del botón Ventas
            fg="#0A0A0A",  # Color negro para el texto
            anchor="center"
        )
        titulo.pack()
        titulo.place(x=0, y=0, width=1100, height=30)

        # Configuración del frame para añadir productos
        frame2 = tk.Frame(self, bg="#E6D9E3", highlightbackground="black")
        frame2.place(x=10, y=30, width=1100, height=530)

        lblframe = tk.LabelFrame(frame2, text="Añadir Productos", font=("Helvetica", 10, "bold"), bg="#E6D9E3", fg="#010A13")
        lblframe.place(x=100, y=10, width=800, height=100)

        # Campo para el número de factura
        label_factura = tk.Label(lblframe, text="N° de Factura", font=("Helvetica", 10, "bold"), bg="#E6D9E3", fg="#010A13")
        label_factura.place(x=10, y=5)
        self.entry_factura = ttk.Entry(lblframe, font=("Helvetica", 10, "bold"), state="disabled")
        self.entry_factura.place(x=10, y=30, width=100)

        # Inicializar el número de factura
        self.cargar_datos()

        # Campo para el cliente
        label_cliente = tk.Label(lblframe, text="Cliente", font=("Helvetica", 10, "bold"), bg="#E6D9E3", fg="#010A13")
        label_cliente.place(x=120, y=5)
        self.entry_cliente = ttk.Combobox(lblframe, font=("Helvetica", 10, "bold"))
        self.entry_cliente.place(x=120, y=30, width=150)

        # Vincular eventos para el campo de cliente
        self.entry_cliente.bind('<KeyRelease>', self.actualizar_sugerencias_cliente)
        self.entry_cliente.bind('<BackSpace>', self.actualizar_sugerencias_cliente)
        self.entry_cliente.bind('<Delete>', self.actualizar_sugerencias_cliente)

        # Campo para el producto
        label_producto = tk.Label(lblframe, text="Producto", font=("Helvetica", 10, "bold"), bg="#E6D9E3", fg="#010A13")
        label_producto.place(x=280, y=5)
        self.entry_producto = ttk.Combobox(lblframe, font=("Helvetica", 10, "bold"))
        self.entry_producto.place(x=280, y=30, width=150)

        # Vincular eventos para el campo de producto
        self.entry_producto.bind('<KeyRelease>', self.actualizar_sugerencias_producto)
        self.entry_producto.bind('<BackSpace>', self.actualizar_sugerencias_producto)
        self.entry_producto.bind('<Delete>', self.actualizar_sugerencias_producto)

        # Campo para la cantidad
        label_cantidad = tk.Label(lblframe, text="Cantidad", font=("Helvetica", 10, "bold"), bg="#E6D9E3", fg="#010A13")
        label_cantidad.place(x=440, y=5)
        self.entry_cantidad = ttk.Entry(lblframe, font=("Helvetica", 10, "bold"))
        self.entry_cantidad.place(x=440, y=30, width=80)

        # Campo para determinar si el cliente pagó
        label_pago = tk.Label(lblframe, text="¿Pagó?", font=("Helvetica", 10, "bold"), bg="#E6D9E3", fg="#010A13")
        label_pago.place(x=540, y=5)
        self.entry_pago = ttk.Combobox(lblframe, font=("Helvetica", 10, "bold"), state="readonly")
        self.entry_pago['values'] = ["Sí", "No"]
        self.entry_pago.place(x=540, y=30, width=80)
        self.entry_pago.current(0)  # Seleccionar "Sí" por defecto

        # Botón para agregar producto
        self.btn_agregar_producto = tk.Button(lblframe, text="Agregar Producto", command=self.agregar_producto_pedido,
                                              font=("Helvetica", 10, "bold"), bg="#4CAF50", fg="white")
        self.btn_agregar_producto.place(x=660, y=5, width=120, height=50)

        # Tabla para los productos del pedido
        lblframe_pedido = tk.LabelFrame(frame2, bg="#E6D9E3", bd=0)  # Sin bordes visibles
        lblframe_pedido.place(x=30, y=120, width=900, height=300)

        # Scrollbar vertical
        scroll_y = ttk.Scrollbar(lblframe_pedido, orient=tk.VERTICAL)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        # Configuración de la tabla
        self.tree_pedido = ttk.Treeview(lblframe_pedido, columns=("producto", "cliente", "cantidad", "subtotal"),
                                        show="headings", height=8, yscrollcommand=scroll_y.set)
        self.tree_pedido.pack(expand=True, fill=tk.BOTH)

        # Configurar el scrollbar para la tabla
        scroll_y.config(command=self.tree_pedido.yview)

        # Configurar columnas
        columnas_pedido = [
            ("Producto", 200), ("Cliente", 150), ("Cantidad", 100), ("Subtotal", 100)
        ]
        for idx, (text, width) in enumerate(columnas_pedido, start=1):
            self.tree_pedido.heading(f"#{idx}", text=text)
            self.tree_pedido.column(f"#{idx}", width=width, anchor=tk.CENTER)

        # Evento para editar la cantidad al hacer doble clic
        self.tree_pedido.bind("<Double-1>", self.editar_cantidad)

        # Frame para botones de opciones
        lblframe_opciones = tk.LabelFrame(frame2, text="Opciones", font=("Helvetica", 12, "bold"), bg="#E6D9E3", fg="#010A13")
        lblframe_opciones.place(x=250, y=430, width=500, height=70)

        # Botones de opciones
        fontbotones = ("Helvetica", 12, "bold")

        self.btn_agregar_venta = tk.Button(lblframe_opciones, text="Agregar Venta", command=self.agregar_venta,
                                           font=fontbotones, bg="#4CAF50", fg="white")
        self.btn_agregar_venta.place(x=10, y=10, width=150)

        self.btn_eliminar_producto = tk.Button(lblframe_opciones, text="Eliminar Producto", command=self.eliminar_producto_pedido,
                                               font=fontbotones, bg="#f44336", fg="white")
        self.btn_eliminar_producto.place(x=170, y=10, width=150)

        self.btn_ver_facturas = tk.Button(lblframe_opciones, text="Ver Facturas", command=self.ver_facturas,
                                          font=fontbotones, bg="#2196F3", fg="white")
        self.btn_ver_facturas.place(x=330, y=10, width=150)

        # Actualizar las sugerencias de clientes al cargar la sección
        self.actualizar_sugerencias_cliente()

    def agregar_producto_pedido(self):
        cliente = self.entry_cliente.get().strip()
        producto = self.entry_producto.get().strip()
        cantidad = self.entry_cantidad.get().strip()

        if not cliente or not producto or not cantidad:
            messagebox.showerror("Error", "Debe completar todos los campos para agregar un producto")
            return

        try:
            cantidad = int(cantidad)
            if cantidad <= 0:
                raise ValueError

            # Obtener el precio unitario y la cantidad disponible del producto desde la base de datos
            resultado = database.ejecutar_consulta("SELECT precio, cantidad FROM inventario WHERE producto = ?", (producto,))
            if not resultado:
                messagebox.showerror("Error", f"El producto '{producto}' no existe en el inventario")
                return

            precio_unitario, cantidad_disponible = resultado[0]

            # Validar que haya suficiente cantidad en el inventario
            if cantidad > cantidad_disponible:
                messagebox.showerror("Error", f"No hay suficiente cantidad de '{producto}' en el inventario. Disponible: {cantidad_disponible}")
                return

            # Calcular el subtotal
            subtotal = precio_unitario * cantidad

            # Agregar el producto al Treeview
            self.tree_pedido.insert("", tk.END, values=(producto, cliente, cantidad, format_currency(subtotal)))

            # Actualizar la cantidad en el inventario
            nueva_cantidad = cantidad_disponible - cantidad
            database.ejecutar_consulta("UPDATE inventario SET cantidad = ? WHERE producto = ?", (nueva_cantidad, producto))

            # Mostrar alerta si el producto está agotado
            if nueva_cantidad == 0:
                messagebox.showwarning("Producto agotado", f"El producto '{producto}' se ha agotado")

            # Fijar el cliente
            self.fijar_cliente()

            # Limpiar los campos después de agregar
            self.entry_producto.set("")
            self.entry_cantidad.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Error", "La cantidad debe ser un número entero positivo")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo agregar el producto: {e}")



    def agregar_venta(self):
        # Obtener todos los productos del pedido desde la tabla
        productos_pedido = self.tree_pedido.get_children()
        if not productos_pedido:
            messagebox.showerror("Error", "Debe agregar al menos un producto antes de registrar la venta")
            return

        try:
            # Obtener el número de factura
            numero_factura = self.entry_factura.get().strip()
            if not numero_factura:
                messagebox.showerror("Error", "El número de factura no está disponible")
                return

            # Obtener si el cliente pagó
            pago = self.entry_pago.get().strip()

            # Obtener la fecha y hora actual
            fecha = datetime.datetime.now().strftime("%Y-%m-%d")
            hora = datetime.datetime.now().strftime("%H:%M:%S")

            # Procesar cada producto en la tabla
            for item in productos_pedido:
                producto, cliente, cantidad, subtotal = self.tree_pedido.item(item, "values")
                cantidad = int(cantidad)

                if pago == "Sí":
                    database.insertar_venta(
                        numero_factura, cliente, producto, cantidad,
                        subtotal, fecha, hora, pago
                    )
                else:
                    database.insertar_deuda(
                        numero_factura, cliente, producto, cantidad,
                        subtotal, fecha, hora, "No"
                    )

            # Limpiar la tabla después de registrar la venta
            self.tree_pedido.delete(*productos_pedido)

            # Limpiar el campo de cliente
            self.entry_cliente.set("")  # Limpiar el combobox de cliente

            # Mostrar mensaje de éxito
            if pago == "Sí":
                messagebox.showinfo("Éxito", "Venta registrada correctamente")
            else:
                messagebox.showwarning("Deuda", "El cliente ha sido enviado a la sección de Deudas")

            # Actualizar el número de factura
            self.cargar_datos()

            # Habilitar el cliente
            self.habilitar_cliente()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo registrar la venta: {e}")

    def eliminar_producto_pedido(self):
        # Obtener el producto seleccionado en la tabla
        seleccionado = self.tree_pedido.selection()
        if not seleccionado:
            messagebox.showwarning("Advertencia", "Seleccione un producto para eliminar")
            return

        for item in seleccionado:
            producto, cliente, cantidad, subtotal = self.tree_pedido.item(item, "values")
            cantidad = int(cantidad)

            # Devolver la cantidad al inventario
            resultado = database.ejecutar_consulta("SELECT cantidad FROM inventario WHERE producto = ?", (producto,))
            if resultado:
                cantidad_disponible = resultado[0][0]
                nueva_cantidad = cantidad_disponible + cantidad
                database.ejecutar_consulta("UPDATE inventario SET cantidad = ? WHERE producto = ?", (nueva_cantidad, producto))

            # Eliminar el producto del Treeview
            self.tree_pedido.delete(item)

        # Habilitar el cliente si no hay productos en la tabla
        self.habilitar_cliente()

        messagebox.showinfo("Éxito", "Producto eliminado correctamente")

    def ver_facturas(self):
        # Verificar si la ventana ya está abierta
        if hasattr(self, "ventana_facturas") and self.ventana_facturas.winfo_exists():
            self.ventana_facturas.lift()  # Traer la ventana al frente si ya está abierta
            return

        # Crear una nueva ventana para mostrar las facturas
        self.ventana_facturas = tk.Toplevel(self)
        self.ventana_facturas.title("Facturas")
        self.ventana_facturas.geometry("900x500")

        # Frame superior para la tabla de facturas
        frame_tabla = tk.Frame(self.ventana_facturas, bg="#E6D9E3")
        frame_tabla.place(x=10, y=10, width=880, height=350)

        # Scrollbars para la tabla
        scroll_y = ttk.Scrollbar(frame_tabla, orient=tk.VERTICAL)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x = ttk.Scrollbar(frame_tabla, orient=tk.HORIZONTAL)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        # Tabla para mostrar las facturas
        tree_facturas = ttk.Treeview(
            frame_tabla,
            columns=("factura", "cliente", "productos", "cantidad", "subtotal", "fecha", "hora", "pago", "total"),
            show="headings",
            height=15,
            yscrollcommand=scroll_y.set,
            xscrollcommand=scroll_x.set
        )
        tree_facturas.pack(expand=True, fill=tk.BOTH)

        # Configurar los scrollbars
        scroll_y.config(command=tree_facturas.yview)
        scroll_x.config(command=tree_facturas.xview)

        # Configurar columnas
        columnas_facturas = [
            ("N° de Factura", 100), ("Cliente", 150), ("Productos", 200),
            ("Cantidad", 100), ("Subtotal", 100), ("Fecha", 100),
            ("Hora", 100), ("¿Pagó?", 80), ("Total", 100)
        ]
        for idx, (text, width) in enumerate(columnas_facturas, start=1):
            tree_facturas.heading(f"#{idx}", text=text)
            tree_facturas.column(f"#{idx}", width=width, anchor=tk.CENTER)

        # Cargar las facturas desde la base de datos
        try:
            facturas = database.ejecutar_consulta("""
                SELECT factura, cliente, GROUP_CONCAT(producto, ', '), SUM(cantidad), SUM(subtotal), fecha, hora, pago, SUM(subtotal)
                FROM ventas
                GROUP BY factura
                ORDER BY factura ASC
            """)
            for factura in facturas:
                factura = list(factura)
                factura[4] = format_currency(factura[4])  # Formatear el subtotal
                factura[8] = format_currency(factura[8])  # Formatear el total
                tree_facturas.insert("", tk.END, values=factura)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar las facturas: {e}")

        # Frame inferior para los botones
        frame_botones = tk.Frame(self.ventana_facturas, bg="#E6D9E3")
        frame_botones.place(x=10, y=370, width=880, height=100)

        # Botón para eliminar una factura
        btn_eliminar_factura = tk.Button(
            frame_botones,
            text="Eliminar Factura",
            command=lambda: self.eliminar_factura(tree_facturas),
            font=("Helvetica", 12, "bold"),
            bg="#f44336",
            fg="white"
        )
        btn_eliminar_factura.place(x=10, y=30, width=150, height=40)

        # Botón para generar una factura en PDF
        btn_generar_factura = tk.Button(
            frame_botones,
            text="Generar Factura",
            command=lambda: self.generar_factura(tree_facturas),
            font=("Helvetica", 12, "bold"),
            bg="#4CAF50",
            fg="white"
        )
        btn_generar_factura.place(x=180, y=30, width=150, height=40)

        # Manejar el cierre de la ventana
        self.ventana_facturas.protocol("WM_DELETE_WINDOW", self.cerrar_ventana_facturas)

    def cerrar_ventana_facturas(self):
        """Cerrar la ventana de facturas y eliminar la referencia."""
        self.ventana_facturas.destroy()
        del self.ventana_facturas

    def actualizar_sugerencias_cliente(self, event=None):
        """Actualiza las sugerencias de clientes mientras el usuario escribe"""
        texto = self.entry_cliente.get().strip().lower()

        try:
            # Consultar los clientes desde la base de datos
            clientes = database.ejecutar_consulta("""
                SELECT DISTINCT nombres || ' ' || apellidos
                FROM clientes
                WHERE LOWER(nombres || ' ' || apellidos) LIKE ?
            """, (f"%{texto}%",))

            # Filtrar y actualizar las sugerencias
            sugerencias = [cliente[0] for cliente in clientes]

            # Mostrar las sugerencias en el Combobox
            self.entry_cliente['values'] = sugerencias

            # Si hay sugerencias y el texto coincide parcialmente con alguna,
            # mostrar la lista desplegable
            if sugerencias and any(texto in s.lower() for s in sugerencias):
                self.entry_cliente.event_generate('<Down>')

        except Exception as e:
            print(f"Error al actualizar sugerencias de clientes: {e}")

    def actualizar_sugerencias_producto(self, event=None):
        """Actualiza las sugerencias de productos mientras el usuario escribe"""
        texto = self.entry_producto.get().strip().lower()

        try:
            # Consultar los productos desde la base de datos
            productos = database.ejecutar_consulta("""
                SELECT DISTINCT producto
                FROM inventario
                WHERE LOWER(producto) LIKE ?
                AND cantidad > 0
            """, (f"%{texto}%",))

            # Filtrar y actualizar las sugerencias
            sugerencias = [producto[0] for producto in productos]

            # Mostrar las sugerencias en el Combobox
            self.entry_producto['values'] = sugerencias

            # Si hay sugerencias y el texto coincide parcialmente con alguna,
            # mostrar la lista desplegable
            if sugerencias and any(texto in s.lower() for s in sugerencias):
                self.entry_producto.event_generate('<Down>')

        except Exception as e:
            print(f"Error al actualizar sugerencias de productos: {e}")

    def fijar_cliente(self):
        # Deshabilitar el campo de cliente después de agregar un producto
        self.entry_cliente.config(state="disabled")

    def habilitar_cliente(self):
        # Habilitar el campo de cliente si no hay productos en la tabla
        if not self.tree_pedido.get_children():
            self.entry_cliente.config(state="normal")

    def editar_cantidad(self, event):
        # Obtener el elemento seleccionado
        item = self.tree_pedido.selection()
        if not item:
            return

        # Obtener los valores actuales
        item_id = item[0]
        valores = self.tree_pedido.item(item_id, "values")
        producto, cliente, cantidad_actual, subtotal = valores

        # Consultar la cantidad disponible en el inventario
        resultado = database.ejecutar_consulta("SELECT cantidad FROM inventario WHERE producto = ?", (producto,))
        if not resultado:
            messagebox.showerror("Error", f"El producto '{producto}' no existe en el inventario")
            return

        cantidad_disponible = resultado[0][0]

        # Crear ventana emergente
        popup = tk.Toplevel(self)
        popup.title("Editar Cantidad")
        popup.geometry("300x150")
        popup.transient(self)  # Hacer que la ventana sea modal
        popup.wait_visibility()  # Esperar a que la ventana sea visible
        popup.grab_set()  # Establecer el foco en la ventana emergente

        # Etiqueta para mostrar el producto y la cantidad disponible
        tk.Label(popup, text=f"Producto: {producto}", font=("Helvetica", 10, "bold")).pack(pady=5)
        tk.Label(popup, text=f"Cantidad disponible: {cantidad_disponible}", font=("Helvetica", 10)).pack(pady=5)

        # Campo para ingresar la nueva cantidad
        tk.Label(popup, text="Nueva cantidad:", font=("Helvetica", 10)).pack(pady=5)
        entry_cantidad = ttk.Entry(popup, font=("Helvetica", 10))
        entry_cantidad.insert(0, cantidad_actual)
        entry_cantidad.pack(pady=5)

        def guardar_cantidad():
            nueva_cantidad = entry_cantidad.get().strip()
            try:
                nueva_cantidad = int(nueva_cantidad)
                if nueva_cantidad <= 0:
                    raise ValueError

                if nueva_cantidad > cantidad_disponible:
                    messagebox.showerror("Error", f"No se puede asignar la cantidad. Solo quedan {cantidad_disponible} unidades de '{producto}'")
                    return

                # Actualizar la cantidad y el subtotal en la tabla
                precio_unitario = float(subtotal) / int(cantidad_actual)
                nuevo_subtotal = precio_unitario * nueva_cantidad
                self.tree_pedido.item(item_id, values=(producto, cliente, nueva_cantidad, format_currency(nuevo_subtotal)))

                # Actualizar la cantidad en el inventario
                diferencia = int(cantidad_actual) - nueva_cantidad
                nueva_cantidad_inventario = cantidad_disponible + diferencia
                database.ejecutar_consulta("UPDATE inventario SET cantidad = ? WHERE producto = ?", (nueva_cantidad_inventario, producto))

                popup.destroy()
                messagebox.showinfo("Éxito", "Cantidad actualizada correctamente")
            except ValueError:
                messagebox.showerror("Error", "La cantidad debe ser un número entero positivo")

        # Botón para guardar cambios
        tk.Button(popup, text="Guardar", command=guardar_cantidad, bg="#4CAF50", fg="white", font=("Helvetica", 10, "bold")).pack(pady=10)

        # Botón para cerrar la ventana
        tk.Button(popup, text="Cancelar", command=popup.destroy, bg="#f44336", fg="white", font=("Helvetica", 10, "bold")).pack()

    def eliminar_factura(self, tree_facturas):
        # Obtener la factura seleccionada
        seleccionado = tree_facturas.selection()
        if not seleccionado:
            messagebox.showwarning("Advertencia", "Seleccione una factura para eliminar")
            return

        for item in seleccionado:
            factura = tree_facturas.item(item, "values")[0]

            # Eliminar la factura de la base de datos
            database.ejecutar_consulta("DELETE FROM ventas WHERE factura = ?", (factura,))

            # Eliminar la factura de la tabla
            tree_facturas.delete(item)

        messagebox.showinfo("Éxito", "Factura eliminada correctamente")

    def generar_factura(self, tree_facturas):
        # Obtener la factura seleccionada
        seleccionado = tree_facturas.selection()
        if not seleccionado:
            messagebox.showwarning("Advertencia", "Seleccione una factura para generar")
            return

        try:
            for item in seleccionado:
                factura, cliente, productos, cantidad, subtotal, fecha, hora, pago, total = tree_facturas.item(item, "values")

                # Solicitar al usuario que seleccione dónde guardar el archivo
                archivo_pdf = filedialog.asksaveasfilename(
                    defaultextension=".pdf",
                    initialfile=f"Factura_{factura}.pdf",
                    title="Guardar factura como",
                    filetypes=[("Archivos PDF", "*.pdf")]
                )

                if archivo_pdf:  # Si el usuario seleccionó una ubicación
                    # Generar el PDF
                    c = canvas.Canvas(archivo_pdf, pagesize=letter)

                    # Configurar el estilo del PDF
                    c.setFont("Helvetica-Bold", 24)
                    c.drawString(50, 750, "Factura de Venta")

                    c.setFont("Helvetica-Bold", 12)
                    c.drawString(50, 700, "Información de la Factura")

                    c.setFont("Helvetica", 12)
                    c.drawString(50, 670, f"N° Factura: {factura}")
                    c.drawString(50, 650, f"Cliente: {cliente}")
                    c.drawString(50, 630, f"Fecha: {fecha}")
                    c.drawString(50, 610, f"Hora: {hora}")

                    # Tabla de productos
                    c.setFont("Helvetica-Bold", 12)
                    c.drawString(50, 570, "Productos:")

                    c.setFont("Helvetica", 12)
                    y = 550
                    for prod in productos.split(", "):
                        c.drawString(50, y, f"- {prod}")
                        y -= 20

                    c.drawString(50, y-20, f"Cantidad total: {cantidad}")
                    c.drawString(50, y-40, f"Subtotal: ${format_currency(subtotal)}")
                    c.drawString(50, y-60, f"Estado de pago: {pago}")

                    c.setFont("Helvetica-Bold", 14)
                    c.drawString(50, y-100, f"Total: ${format_currency(total)}")


                    c.save()
                    messagebox.showinfo("Éxito", f"Factura generada correctamente en:\n{archivo_pdf}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar la factura: {e}")

    def obtener_siguiente_factura(self):
        try:
            # Consultar el último número de factura en la base de datos
            resultado = database.ejecutar_consulta("SELECT MAX(factura) FROM ventas")
            ultimo_numero = resultado[0][0]
            if ultimo_numero is None:
                return 1  # Si no hay facturas, comenzamos en 1
            return int(ultimo_numero) + 1
        except Exception as e:
            # En caso de error, mostrar un mensaje y devolver 1 como valor predeterminado
            messagebox.showerror("Error", f"No se pudo obtener el número de factura: {e}")
            return 1

    def cargar_datos(self):
        # Obtener el siguiente número de factura
        numero_factura = self.obtener_siguiente_factura()

        # Actualizar el campo "N° de Factura"
        self.entry_factura.config(state="normal")  # Habilitar temporalmente para actualizar el valor
        self.entry_factura.delete(0, tk.END)
        self.entry_factura.insert(0, numero_factura)
        self.entry_factura.config(state="disabled")

def format_currency(value):
    """Formatea un valor numérico a una cadena con formato de moneda colombiana."""
    return "{:,.0f}".format(float(value)).replace(",", ".")
