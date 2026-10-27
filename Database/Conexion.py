import sqlite3
import os

def inicializar_base_datos():
    # Conxion base de datos
    ruta_base_datos = os.path.join(os.path.dirname(__file__), "pos_kontrol.db")
    conexion = sqlite3.connect(ruta_base_datos)
    cursor = conexion.cursor()

    # Habilitar claves foráneas en SQLite
    cursor.execute("PRAGMA foreign_keys = ON;")

    # Tabla USUARIOS
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            usuario TEXT UNIQUE NOT NULL,
            clave_hash TEXT NOT NULL,
            rol TEXT NOT NULL
        )
    ''')

    # Tabla CATEGORIAS
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE
        )
    ''')

    # Tabla PRODUCTOS
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            categoria_id INTEGER,
            precio_compra REAL NOT NULL,
            precio_venta REAL NOT NULL,
            stock INTEGER NOT NULL,
            stock_minimo INTEGER DEFAULT 5,
            activo INTEGER DEFAULT 1,
            FOREIGN KEY (categoria_id) REFERENCES categorias(id)
        )
    ''')

    # Tabla VENTAS
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha_hora TEXT NOT NULL,
            total REAL NOT NULL,
            monto_efectivo REAL DEFAULT 0,
            monto_qr REAL DEFAULT 0,
            monto_bold REAL DEFAULT 0,
            estado TEXT DEFAULT 'COMPLETADA',
            usuario_id INTEGER,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        )
    ''')

    # Tabla DETALLE_VENTAS
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS detalle_ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            venta_id INTEGER NOT NULL,
            producto_id INTEGER NOT NULL,
            cantidad INTEGER NOT NULL,
            precio_compra_unitario REAL NOT NULL,
            precio_venta_unitario REAL NOT NULL,
            FOREIGN KEY (venta_id) REFERENCES ventas(id),
            FOREIGN KEY (producto_id) REFERENCES productos(id)
        )
    ''')

    # Tabla EGRESOS_CAJA_MENOR
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS egresos_caja_menor (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha_hora TEXT NOT NULL,
            monto REAL NOT NULL,
            categoria TEXT NOT NULL,
            descripcion TEXT,
            usuario_id INTEGER,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        )
    ''')

    # Tabla CIERRES_CAJA
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cierres_caja (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha_cierre TEXT NOT NULL,
            base_caja_inicial REAL NOT NULL,
            total_ingresos REAL NOT NULL,
            total_costo_mercancia REAL NOT NULL,
            ganancia_bruta REAL NOT NULL,
            total_egresos REAL NOT NULL,
            ganancia_neta REAL NOT NULL,
            monto_efectivo_esperado REAL NOT NULL,
            monto_qr_total REAL NOT NULL,
            monto_bold_total REAL NOT NULL,
            efectivo_real_contado REAL NOT NULL,
            diferencia REAL NOT NULL,
            usuario_id INTEGER,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        )
    ''')

    conexion.commit()
    conexion.close()
    print("¡Base de datos inicializada con éxito!")

if __name__ == "__main__":
    inicializar_base_datos()