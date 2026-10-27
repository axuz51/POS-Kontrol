import sqlite3
import hashlib
import os

class ModeloUsuario:
    def __init__(self):
        # Ruta de la base de datos de POS-Kontrol
        self.db_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "Database",
            "pos_kontrol.db",
        )

    def verificar_credenciales(self, usuario, password):
        # Método para validar el usuario y contraseña en la base de datos (Seguridad del sistema)
        try:
            conexion = sqlite3.connect(self.db_path)
            cursor = conexion.cursor()
            
            # Buscamos el usuario por su nombre de usuario
            cursor.execute("SELECT id, nombre, usuario, clave_hash, rol FROM usuarios WHERE usuario = ?", (usuario,))
            resultado = cursor.fetchone()
            conexion.close()

            if resultado:
                # El usuario existe, ahora verificamos la contraseña (aquí puedes validar texto plano o hash)
                id_usu, nombre, nick, clave_almacenada, rol = resultado
                if clave_almacenada == password:  # Validación directa por ahora
                    return True, {"id": id_usu, "nombre": nombre, "rol": rol}
            
            return False, "Usuario o contraseña incorrectos."
            
        except Exception as e:
            return False, f"Error de conexión: {e}"

    def crear_usuario_inicial(self):
        # Crea un usuario administrador por defecto si la tabla está vacía
        conexion = sqlite3.connect(self.db_path)
        cursor = conexion.cursor()
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        count = cursor.fetchone()[0]
        
        if count == 0:
            # Creamos un admin por defecto (admin / 1234)
            cursor.execute('''
                INSERT INTO usuarios (nombre, usuario, clave_hash, rol)
                VALUES (?, ?, ?, ?)
            ''', ("Néstor López", "admin", "1234", "Administrador"))
            conexion.commit()
            print("Usuario administrador creado por defecto: admin / 1234")
            
        conexion.close()