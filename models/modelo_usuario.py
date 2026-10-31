import sqlite3
import hashlib
import os

class ModeloUsuario:
    def __init__(self):
        # Apunto al archivo de datos que comparte toda la aplicación.
        self.db_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "Database",
            "pos_kontrol.db",
        )

    def verificar_credenciales(self, usuario, password):
        # Busco el usuario y comparo la clave con la que está guardada.
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
        # Creo el administrador inicial solo si aún no hay usuarios registrados.
        conexion = sqlite3.connect(self.db_path)
        cursor = conexion.cursor()
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        count = cursor.fetchone()[0]
        
        if count == 0:
            # Dejo una cuenta inicial para poder entrar por primera vez.
            cursor.execute('''
                INSERT INTO usuarios (nombre, usuario, clave_hash, rol)
                VALUES (?, ?, ?, ?)
            ''', ("Néstor López", "admin", "1234", "Administrador"))
            conexion.commit()
            print("Usuario administrador creado por defecto: admin / 1234")
            
        conexion.close()