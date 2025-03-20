import sqlite3

def conectar():
    return sqlite3.connect("licoreria.db")

def ejecutar_consulta(query, parametros=()):
    conexion = conectar()
    cursor = conexion.cursor()
    try:
        cursor.execute(query, parametros)
        conexion.commit()
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Error en la consulta: {e}")
        raise
    finally:
        conexion.close()

def crear_tablas():
    conexion = conectar()
    cursor = conexion.cursor()
    try:
        # Crear la tabla inventario
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            producto TEXT NOT NULL,
            precio REAL NOT NULL,
            cantidad INTEGER NOT NULL,
            total REAL NOT NULL
        )
        """)

        # Crear la tabla ventas
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            factura TEXT NOT NULL,
            cliente TEXT NOT NULL,
            producto TEXT NOT NULL,
            cantidad INTEGER NOT NULL,
            subtotal REAL NOT NULL,
            fecha TEXT NOT NULL,
            hora TEXT NOT NULL,
            pago TEXT NOT NULL
        )
        """)

        # Crear la tabla clientes
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombres TEXT,
            apellidos TEXT,
            cedula TEXT,
            celular TEXT,
            zona TEXT
        )
        """)

        # Crear la tabla usuarios
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT,
            contrasena TEXT
        )
        """)

        # Crear la tabla de deudas
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS deudas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            factura TEXT NOT NULL,
            cliente TEXT NOT NULL,
            producto TEXT NOT NULL,
            cantidad INTEGER NOT NULL,
            subtotal REAL NOT NULL,
            fecha TEXT NOT NULL,
            hora TEXT NOT NULL,
            pago TEXT NOT NULL
        )
        """)

        # Insertar el usuario admin si no existe
        cursor.execute("""
        INSERT OR IGNORE INTO usuarios (usuario, contrasena) VALUES (?, ?)
        """, ('admin', 'admin'))

        conexion.commit()
    finally:
        conexion.close()

def agregar_columna_si_no_existe(tabla, columna, definicion):
    conexion = conectar()
    cursor = conexion.cursor()
    try:
        cursor.execute(f"PRAGMA table_info({tabla})")
        columnas = [info[1] for info in cursor.fetchall()]
        if columna not in columnas:
            cursor.execute(f"ALTER TABLE {tabla} ADD COLUMN {columna} {definicion}")
            conexion.commit()
    except Exception as e:
        print(f"Error al agregar la columna {columna} a la tabla {tabla}: {e}")
    finally:
        conexion.close()

# Funciones específicas para la tabla inventario
def obtener_inventario():
    query = "SELECT id, producto, precio, cantidad, total FROM inventario"
    return ejecutar_consulta(query)

def insertar_producto(producto, precio, cantidad, total):
    query = """
    INSERT INTO inventario (producto, precio, cantidad, total)
    VALUES (?, ?, ?, ?)
    """
    parametros = (producto, precio, cantidad, total)
    ejecutar_consulta(query, parametros)

def eliminar_producto_por_id(id_producto):
    query = "DELETE FROM inventario WHERE id = ?"
    ejecutar_consulta(query, (id_producto,))

def actualizar_producto(id_producto, columna, nuevo_valor):
    query = f"UPDATE inventario SET {columna} = ? WHERE id = ?"
    ejecutar_consulta(query, (nuevo_valor, id_producto))

def buscar_producto(criterio):
    query = '''
    SELECT * FROM inventario
    WHERE producto LIKE ? OR precio LIKE ? OR cantidad LIKE ?
    '''
    parametros = (f"%{criterio}%", f"%{criterio}%", f"%{criterio}%")
    return ejecutar_consulta(query, parametros)

def obtener_producto_por_id(id_producto):
    query = "SELECT * FROM inventario WHERE id = ?"
    return ejecutar_consulta(query, (id_producto,))[0]

def reasignar_ids_inventario():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM inventario ORDER BY id")
    ids_actuales = [row[0] for row in cursor.fetchall()]

    for nuevo_id, id_actual in enumerate(ids_actuales, start=1):
        if nuevo_id != id_actual:
            cursor.execute("UPDATE inventario SET id = ? WHERE id = ?", (nuevo_id, id_actual))
    conn.commit()
    conn.close()

def obtener_valor_total_inventario():
    query = "SELECT SUM(total) FROM inventario"
    resultado = ejecutar_consulta(query)
    return resultado[0][0] if resultado[0][0] is not None else 0

# Funciones específicas para la tabla clientes
def obtener_clientes():
    query = "SELECT * FROM clientes ORDER BY id ASC"
    return ejecutar_consulta(query)

def insertar_cliente(nombres, apellidos, cedula, celular, zona):
    query = '''
    INSERT INTO clientes (nombres, apellidos, cedula, celular, zona)
    VALUES (?, ?, ?, ?, ?)
    '''
    ejecutar_consulta(query, (nombres, apellidos, cedula, celular, zona))

def eliminar_cliente_por_id(id_cliente):
    query = "DELETE FROM clientes WHERE id = ?"
    ejecutar_consulta(query, (id_cliente,))

def actualizar_cliente(id_cliente, columna, nuevo_valor):
    query = f"UPDATE clientes SET {columna} = ? WHERE id = ?"
    ejecutar_consulta(query, (nuevo_valor, id_cliente))

def buscar_cliente(criterio):
    query = '''
    SELECT * FROM clientes
    WHERE nombres LIKE ? OR apellidos LIKE ? OR cedula LIKE ? OR celular LIKE ? OR zona LIKE ?
    '''
    parametros = (f"%{criterio}%", f"%{criterio}%", f"%{criterio}%", f"%{criterio}%", f"%{criterio}%")
    return ejecutar_consulta(query, parametros)

def reasignar_ids_clientes():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM clientes ORDER BY id")
    ids_actuales = [row[0] for row in cursor.fetchall()]

    for nuevo_id, id_actual in enumerate(ids_actuales, start=1):
        if nuevo_id != id_actual:
            cursor.execute("UPDATE clientes SET id = ? WHERE id = ?", (nuevo_id, id_actual))
    conn.commit()
    conn.close()

def crear_clientes_prueba():
    conn = conectar()
    cursor = conn.cursor()
    conn.commit()
    conn.close()

def crear_productos_prueba():
    productos = [
        ("Producto " + str(i), round(1000 + i * 10, 2), i * 5, round((1000 + i * 10) * (i * 5), 2))
        for i in range(1, 51)
    ]

    conn = conectar()
    cursor = conn.cursor()

# Funciones específicas para la tabla ventas
def obtener_ventas():
    query = "SELECT * FROM ventas ORDER BY id ASC"
    return ejecutar_consulta(query)

def insertar_venta(factura, cliente, producto, cantidad, subtotal, fecha, hora, pago):
    query = """
    INSERT INTO ventas (factura, cliente, producto, cantidad, subtotal, fecha, hora, pago)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """
    ejecutar_consulta(query, (factura, cliente, producto, cantidad, subtotal, fecha, hora, pago))

# Funciones específicas para la tabla deudas
def obtener_deudas():
    query = "SELECT * FROM deudas ORDER BY id ASC"
    return ejecutar_consulta(query)

def insertar_deuda(factura, cliente, producto, cantidad, subtotal):
    query = '''
    INSERT INTO deudas (factura, cliente, producto, cantidad, subtotal)
    VALUES (?, ?, ?, ?, ?)
    '''
    ejecutar_consulta(query, (factura, cliente, producto, cantidad, subtotal))

def insertar_deuda(factura, cliente, producto, cantidad, subtotal, fecha, hora, pago):
    query = '''
    INSERT INTO deudas (factura, cliente, producto, cantidad, subtotal, fecha, hora, pago)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    '''
    ejecutar_consulta(query, (factura, cliente, producto, cantidad, subtotal, fecha, hora, pago))

if __name__ == "__main__":
    crear_tablas()
    # Asegurarse de que todas las columnas necesarias estén presentes
    agregar_columna_si_no_existe("ventas", "factura", "TEXT NOT NULL")
    agregar_columna_si_no_existe("ventas", "cliente", "TEXT NOT NULL")
    agregar_columna_si_no_existe("ventas", "producto", "TEXT NOT NULL")
    agregar_columna_si_no_existe("ventas", "cantidad", "INTEGER NOT NULL")
    agregar_columna_si_no_existe("ventas", "subtotal", "REAL NOT NULL")
    agregar_columna_si_no_existe("ventas", "fecha", "TEXT NOT NULL")
    agregar_columna_si_no_existe("ventas", "hora", "TEXT NOT NULL")
    agregar_columna_si_no_existe("ventas", "pago", "TEXT NOT NULL")
