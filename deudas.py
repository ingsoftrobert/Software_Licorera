from tkinter import *
import tkinter as tk
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from tkinter import ttk, messagebox, filedialog
import database
from datetime import datetime

class Deudas(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack()
        self.widgets()

    def widgets(self):
        # Configuración del frame superior
        frame1 = tk.Frame(self, bg="#F44336", highlightthickness=1, highlightbackground="black")
        frame1.pack()
        frame1.place(x=0, y=0, width=1100, height=30)

        # Título de la ventana
        titulo = tk.Label(
            self,
            text="DEUDAS",
            font=("Arial", 16, "bold"),
            bg="#F44336",  # Color rojo del botón Deudas
            fg="#0A0A0A",  # Color negro para el texto
            anchor="center"
        )
        titulo.pack()
        titulo.place(x=0, y=0, width=1100, height=30)

        # Configuración del frame para la tabla
        treFrame = tk.Frame(self, bg="#E6D9E3", highlightbackground="black")
        treFrame.place(x=10, y=30, width=1000, height=400)

        # Scrollbars y tabla
        scrol_y = ttk.Scrollbar(treFrame, orient=tk.VERTICAL)
        scrol_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrol_x = ttk.Scrollbar(treFrame, orient=tk.HORIZONTAL)
        scrol_x.pack(side=tk.BOTTOM, fill=tk.X)

        self.tree = ttk.Treeview(
            treFrame,
            columns=("num_factura", "cliente", "producto", "cantidad", "subtotal", "fecha", "hora", "pago"),
            show="headings",
            height=20,
            yscrollcommand=scrol_y.set,
            xscrollcommand=scrol_x.set
        )
        scrol_y.config(command=self.tree.yview)
        scrol_x.config(command=self.tree.xview)

        # Configurar columnas
        columnas = [
            ("N° Factura", 80), ("Cliente", 150), ("Producto", 150),
            ("Cantidad", 80), ("Subtotal", 100), ("Fecha", 100),
            ("Hora", 80), ("¿Pagó?", 80)
        ]
        for idx, (text, width) in enumerate(columnas, start=1):
            self.tree.heading(f"#{idx}", text=text)
            self.tree.column(f"#{idx}", width=width, anchor=tk.CENTER)

        self.tree.pack(expand=True, fill=tk.BOTH)

        # Frame para botones
        lblframe1 = tk.LabelFrame(self, text="Opciones", font=("Helvetica", 10, "bold"), bg="#E6D9E3", fg="#010A13")
        lblframe1.place(x=250, y=440, width=350, height=70)

        # Botones
        fontbotones = ("Helvetica", 12, "bold")

        self.btn_eliminar = tk.Button(
            lblframe1,
            text="Eliminar",
            command=self.eliminar_deuda,
            font=fontbotones,
            bg="#f44336",
            fg="white"
        )
        self.btn_eliminar.place(x=10, y=5, width=100)

        self.btn_generar_factura = tk.Button(
            lblframe1,
            text="Generar Factura",
            command=self.generar_factura,
            font=fontbotones,
            bg="#4CAF50",
            fg="white"
        )
        self.btn_generar_factura.place(x=120, y=5, width=150)

        # Evento para editar el campo de pago al hacer doble clic
        self.tree.bind("<Double-1>", self.editar_pago)

        # Cargar las deudas desde la base de datos
        self.cargar_deudas()

    def cargar_deudas(self):
        self.tree.delete(*self.tree.get_children())
        try:
            deudas = database.ejecutar_consulta("""
                SELECT factura, cliente, producto, cantidad, subtotal, fecha, hora, pago
                FROM deudas
                ORDER BY factura ASC
            """)
            for deuda in deudas:
                self.mostrar_deuda(deuda)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar las deudas: {e}")

    def mostrar_deuda(self, deuda):
        valores = list(deuda)
        valores[4] = valores[4]  # Subtotal
        self.tree.insert("", tk.END, values=valores)

    def eliminar_deuda(self):
        seleccionado = self.tree.selection()
        if not seleccionado:
            messagebox.showwarning("Advertencia", "Seleccione una deuda para eliminar")
            return

        if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar la deuda seleccionada?"):
            try:
                for item in seleccionado:
                    factura = self.tree.item(item)["values"][0]
                    database.ejecutar_consulta("DELETE FROM deudas WHERE factura = ?", (factura,))
                    self.tree.delete(item)
                messagebox.showinfo("Éxito", "Deuda eliminada correctamente")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar la deuda: {e}")

    def generar_factura(self):
        seleccionado = self.tree.selection()
        if not seleccionado:
            messagebox.showwarning("Advertencia", "Seleccione una deuda para generar la factura")
            return

        try:
            for item in seleccionado:
                valores = self.tree.item(item)["values"]
                factura, cliente, producto, cantidad, subtotal, fecha, hora, pago = valores

                # Solicitar al usuario que seleccione dónde guardar el archivo
                archivo_pdf = filedialog.asksaveasfilename(
                    defaultextension=".pdf",
                    initialfile=f"Deuda_{factura}.pdf",
                    title="Guardar factura de deuda como",
                    filetypes=[("Archivos PDF", "*.pdf")]
                )

                if archivo_pdf:
                    c = canvas.Canvas(archivo_pdf, pagesize=letter)

                    # Configurar el estilo del PDF
                    c.setFont("Helvetica-Bold", 24)
                    c.drawString(50, 750, "Factura de Deuda")

                    c.setFont("Helvetica-Bold", 12)
                    c.drawString(50, 700, "Información de la Deuda")

                    c.setFont("Helvetica", 12)
                    c.drawString(50, 670, f"N° Factura: {factura}")
                    c.drawString(50, 650, f"Cliente: {cliente}")
                    c.drawString(50, 630, f"Fecha: {fecha}")
                    c.drawString(50, 610, f"Hora: {hora}")

                    # Detalles del producto
                    c.setFont("Helvetica-Bold", 12)
                    c.drawString(50, 570, "Detalles del Producto:")

                    c.setFont("Helvetica", 12)
                    c.drawString(70, 550, f"Producto: {producto}")
                    c.drawString(70, 530, f"Cantidad: {cantidad}")
                    c.drawString(70, 510, f"Subtotal: {(subtotal)}")

                    # Estado de la deuda
                    c.setFont("Helvetica-Bold", 14)
                    c.drawString(50, 470, "ESTADO: PENDIENTE DE PAGO")

                    c.save()
                    messagebox.showinfo("Éxito", f"Factura de deuda generada correctamente en:\n{archivo_pdf}")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar la factura: {e}")

    def editar_pago(self, event):
        item = self.tree.selection()
        if not item:
            return

        if messagebox.askyesno("Confirmar Pago", "¿Desea marcar esta deuda como pagada?"):
            try:
                valores = self.tree.item(item[0], "values")
                factura = valores[0]

                # Mover la deuda a ventas
                database.ejecutar_consulta("""
                    INSERT INTO ventas
                    SELECT id, factura, cliente, producto, cantidad, subtotal, fecha, hora, 'Sí'
                    FROM deudas WHERE factura = ?
                """, (factura,))

                # Eliminar de deudas
                database.ejecutar_consulta("DELETE FROM deudas WHERE factura = ?", (factura,))

                self.cargar_deudas()
                messagebox.showinfo("Éxito", "Deuda pagada correctamente")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo actualizar el pago: {e}")
