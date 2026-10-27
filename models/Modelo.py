import sqlite3

class ModeloInventario:
    def __init__(self):
        # Ruta de la base de datos SQLite para nuestro sistema POS-Kontrol
        self.db_path = "database/pos_kontrol.db"

    def conectar(self):
        # Función para abrir la conexión y permitir leer los datos por nombre de columna
        conexion = sqlite3.connect(self.db_path)
        conexion.row_factory = sqlite3.Row  
        return conexion

    def agregar_producto(self, nombre, categoria_id, precio_compra, precio_venta, stock, stock_minimo):
        # Método encargado de insertar un nuevo producto al inventario (Cumple con RF-01)
        try:
            conexion = self.conectar()
            cursor = conexion.cursor()
            
            # Ejecutamos la sentencia SQL de inserción con parámetros seguros (?)
            cursor.execute('''
                INSERT INTO productos (nombre, categoria_id, precio_compra, precio_venta, stock, stock_minimo)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (nombre, categoria_id, precio_compra, precio_venta, stock, stock_minimo))
            
            conexion.commit()
            conexion.close()
            return True, "¡Producto registrado con éxito!"
            
        except Exception as e:
            return False, f"Error al registrar producto: {e}"

    def obtener_productos(self):
        # Consulta para listar los productos y mostrarlos en la interfaz gráfica
        conexion = self.conectar()
        cursor = conexion.cursor()
        
        cursor.execute("SELECT id, nombre, precio_venta, stock FROM productos")
        productos = cursor.fetchall()
        
        conexion.close()
        return productos

    def buscar_productos(self, termino):
        # Busca productos por nombre o SKU/ID corto en la base de datos
        try:
            conexion = self.conectar()
            cursor = conexion.cursor()
            query = "SELECT id, nombre, precio_venta, stock FROM productos WHERE nombre LIKE ? OR id LIKE ?"
            cursor.execute(query, (f"%{termino}%", f"%{termino}%"))
            productos = cursor.fetchall()
            conexion.close()
            return productos
        except Exception as e:
            print(f"Error al buscar productos: {e}")
            return []

    def cargar_datos_prueba(self):
        # Inserta productos iniciales si la tabla de productos está vacía
        try:
            conexion = self.conectar()
            cursor = conexion.cursor()
            cursor.execute("SELECT COUNT(*) FROM productos")
            if cursor.fetchone()[0] == 0:
                productos_demo = [
                    ("Estuche transparente iPhone 14", 1, 8900, 12900, 48, 5),
                    ("Estuche rígido Samsung S23", 1, 10500, 16900, 36, 5),
                    ("Cable USB-C a USB-C 1m", 2, 4200, 7900, 24, 5),
                    ("Cargador USB-C 20W", 3, 9500, 14900, 60, 10),
                    ("Audífonos inalámbricos TWS", 4, 1800, 29900, 18, 5)
                ]
                cursor.executemany('''
                    INSERT INTO productos (nombre, categoria_id, precio_compra, precio_venta, stock, stock_minimo)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', productos_demo)
                conexion.commit()
                print("Productos de prueba creados exitosamente.")
            conexion.close()
        except Exception as e:
            print(f"Error al cargar productos demo: {e}")