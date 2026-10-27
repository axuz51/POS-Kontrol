import tkinter as tk
from Database.Conexion import inicializar_base_datos
from views.Interfaz_login import VentanaLogin
from views.interfaz_menu import VentanaMenuPrincipal

def abrir_menu(usuario_data):
    root_menu = tk.Tk()
    app_menu = VentanaMenuPrincipal(root_menu, usuario_actual=usuario_data)
    root_menu.mainloop()

def main():
    # 1. Aseguramos que la base de datos y tablas estén creadas
    inicializar_base_datos()

    # 2. Iniciamos la ventana de Login
    root_login = tk.Tk()
    app_login = VentanaLogin(root_login)
    root_login.mainloop()

    # 3. Si el login fue exitoso y guardó la sesión, abrimos el Menú Principal
    if hasattr(app_login, 'usuario_autenticado') and app_login.usuario_autenticado:
        abrir_menu(app_login.usuario_autenticado)

if __name__ == "__main__":
    main()