import tkinter as tk
from tkinter import messagebox
from models.modelo_usuario import ModeloUsuario

class VentanaLogin:
    def __init__(self, root):
        self.root = root
        self.root.title("POS-Kontrol - Iniciar Sesión")
        self.root.geometry("450x520")
        self.root.configure(bg="#0B0F12")  # Fondo oscuro elegante del prototipo
        self.root.resizable(False, False)

        self.modelo = ModeloUsuario()
        self.modelo.crear_usuario_inicial()

        self.crear_widgets()

    def crear_widgets(self):
        # Título del Sistema
        titulo = tk.Label(self.root, text="POS-Kontrol", font=("Arial", 24, "bold"), fg="#00E599", bg="#0B0F12")
        titulo.pack(pady=(40, 5))

        subtitulo = tk.Label(self.root, text="Gestión Comercial e Inventarios", font=("Arial", 11), fg="#8A99AD", bg="#0B0F12")
        subtitulo.pack(pady=(0, 30))

        # Marco principal del formulario con bordes y márgenes más estilizados
        frame_form = tk.Frame(self.root, bg="#161B22", padx=25, pady=25)
        frame_form.pack(padx=30, fill="both", expand=True, pady=(0, 30))

        # Campo Usuario
        lbl_user = tk.Label(frame_form, text="Usuario", font=("Arial", 10, "bold"), fg="#FFFFFF", bg="#161B22")
        lbl_user.pack(anchor="w", pady=(5, 5))
        
        # Contenedor estético para el campo de usuario (evita el look cuadrado plano)
        user_container = tk.Frame(frame_form, bg="#0B0F12", padx=2, pady=2)
        user_container.pack(fill="x", pady=(0, 15))
        
        self.entry_user = tk.Entry(user_container, font=("Arial", 12), bg="#0B0F12", fg="#FFFFFF", insertbackground="white", relief="flat")
        self.entry_user.pack(fill="x", ipady=8, padx=5)

        # Campo Contraseña
        lbl_pass = tk.Label(frame_form, text="Contraseña", font=("Arial", 10, "bold"), fg="#FFFFFF", bg="#161B22")
        lbl_pass.pack(anchor="w", pady=(5, 5))
        
        # Contenedor estético para el campo de contraseña
        pass_container = tk.Frame(frame_form, bg="#0B0F12", padx=2, pady=2)
        pass_container.pack(fill="x", pady=(0, 20))
        
        self.entry_pass = tk.Entry(pass_container, font=("Arial", 12), show="*", bg="#0B0F12", fg="#FFFFFF", insertbackground="white", relief="flat")
        self.entry_pass.pack(fill="x", ipady=8, padx=5)

        # Botón de Ingreso con diseño moderno
        btn_ingresar = tk.Button(
            frame_form, text="INGRESAR AL SISTEMA", font=("Arial", 11, "bold"),
            bg="#00E599", fg="#0B0F12", activebackground="#00B377", relief="flat",
            cursor="hand2", command=self.validar_ingreso
        )
        btn_ingresar.pack(fill="x", ipady=12, pady=(10, 10))

        # Pie de página
        footer = tk.Label(self.root, text="SENA - Proyecto de Titulación ADSO", font=("Arial", 8), fg="#4F5D73", bg="#0B0F12")
        footer.pack(pady=10)

    def validar_ingreso(self):
        usuario = self.entry_user.get().strip()
        password = self.entry_pass.get().strip()

        if not usuario or not password:
            messagebox.showerror("Error", "Por favor ingrese usuario y contraseña.")
            return

        exito, resultado = self.modelo.verificar_credenciales(usuario, password)

        if exito:
            self.usuario_autenticado = resultado  # Guardamos los datos del usuario
            messagebox.showinfo("Bienvenido", f"¡Acceso concedido!\nBienvenido, {resultado['nombre']}")
            self.root.destroy()
        else:
            messagebox.showerror("Acceso Denegado", resultado)