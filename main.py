import tkinter as tk

from Database.Conexion import inicializar_base_datos
from views.Interfaz_login import VentanaLogin
from views.interfaz_menu import VentanaMenuPrincipal


def maximizar_sin_ocultar_barra(root):
    # Uso el estado maximizado para dejar visible la barra del sistema.
    root.attributes("-fullscreen", False)
    root.after(200, lambda: root.state("zoomed"))


def abrir_menu(usuario_data):
    # Cuando el acceso termina bien, abro la ventana principal del POS.
    root_menu = tk.Tk()
    app_menu = VentanaMenuPrincipal(root_menu, usuario_actual=usuario_data)
    maximizar_sin_ocultar_barra(root_menu)
    root_menu.mainloop()

def main():
    # Primero preparo la base y luego muestro la ventana de acceso.
    inicializar_base_datos()

    root_login = tk.Tk()
    app_login = VentanaLogin(root_login)
    root_login.mainloop()

    # Solo abro el menú si la ventana de acceso guardó un usuario válido.
    if hasattr(app_login, 'usuario_autenticado') and app_login.usuario_autenticado:
        abrir_menu(app_login.usuario_autenticado)


if __name__ == "__main__":
    main()