import tkinter as tk
from tkinter import messagebox
from views.interfaz_pos import VentanaPOS

class VentanaMenuPrincipal:
    def __init__(self, root, usuario_actual):
        self.root = root
        self.root.title("POS-Kontrol - Menú Principal")
        self.root.geometry("1024x600")
        self.root.configure(bg="#0B0F12")
        self.root.resizable(False, False)
        
        self.usuario_actual = usuario_actual  # Diccionario con id, nombre, rol, etc.

        self.crear_header()
        self.crear_dashboard()

    def crear_header(self):
        # Barra superior informativa
        header_frame = tk.Frame(self.root, bg="#161B22", height=70)
        header_frame.pack(fill="x")
        
        lbl_logo = tk.Label(header_frame, text="❖ POS-Kontrol", font=("Arial", 18, "bold"), fg="#00E599", bg="#161B22")
        lbl_logo.pack(side="left", padx=25, pady=20)
        
        # Información del usuario conectado
        rol_texto = "Administrador" if self.usuario_actual.get('rol_id') == 1 else "Cajero"
        lbl_user = tk.Label(header_frame, text=f"👤 {self.usuario_actual['nombre']} ({rol_texto})", font=("Arial", 11, "bold"), fg="#FFFFFF", bg="#161B22")
        lbl_user.pack(side="right", padx=25)

        btn_salir = tk.Button(header_frame, text="🚪 Cerrar Sesión", font=("Arial", 9, "bold"), bg="#1E242B", fg="#FFFFFF", relief="flat", cursor="hand2", command=self.root.quit)
        btn_salir.pack(side="right", padx=10)

    def crear_dashboard(self):
        # Contenedor central de opciones
        cuerpo_frame = tk.Frame(self.root, bg="#0B0F12")
        cuerpo_frame.pack(fill="both", expand=True, padx=40, pady=40)

        lbl_titulo = tk.Label(cuerpo_frame, text="Panel Principal de Control", font=("Arial", 16, "bold"), fg="#FFFFFF", bg="#0B0F12")
        lbl_titulo.pack(anchor="w", pady=(0, 25))

        # Tarjetas de navegación (Grid de módulos)
        cards_frame = tk.Frame(cuerpo_frame, bg="#0B0F12")
        cards_frame.pack(fill="both", expand=True)

        # Módulo 1: Punto de Venta
        self.crear_tarjeta(
            cards_frame, 
            "🛒 Punto de Venta (POS)", 
            "Realizar ventas rápidas, manejo de carrito y cobro en efectivo o medios digitales.", 
            self.abrir_pos, 0, 0
        )

        # Módulo 2: Inventario
        self.crear_tarjeta(
            cards_frame, 
            "📦 Gestión de Inventario", 
            "Control de stock, precios de compra/venta y alertas de stock mínimo.", 
            self.abrir_inventario, 0, 1
        )

        # Módulo 3: Arqueo y Reportes
        self.crear_tarjeta(
            cards_frame, 
            "📊 Arqueo y Reportes", 
            "Consulta de cierres de caja, ingresos diarios y control financiero.", 
            self.abrir_arqueo, 1, 0
        )

    def crear_tarjeta(self, parent, titulo, descripcion, comando, row, col):
        card = tk.Frame(parent, bg="#161B22", padx=20, pady=20)
        card.grid(row=row, column=col, padx=15, pady=15, sticky="nsew")
        
        # Forzar un tamaño consistente para las tarjetas
        card.config(width=420, height=150)
        card.pack_propagate(False)

        lbl_t = tk.Label(card, text=titulo, font=("Arial", 13, "bold"), fg="#00E599", bg="#161B22")
        lbl_t.pack(anchor="w", pady=(0, 8))

        lbl_d = tk.Label(card, text=descripcion, font=("Arial", 9), fg="#8A99AD", bg="#161B22", wraplength=380, justify="left")
        lbl_d.pack(anchor="w", pady=(0, 15))

        btn = tk.Button(
            card, text="Acceder al Módulo", font=("Arial", 9, "bold"),
            bg="#00E599", fg="#0B0F12", activebackground="#00B377", relief="flat",
            cursor="hand2", command=comando
        )
        btn.pack(anchor="w", ipadx=10, ipady=4)

    def abrir_pos(self):
        self.root.destroy()
        root_pos = tk.Tk()
        VentanaPOS(root_pos, usuario_actual=self.usuario_actual['nombre'])
        root_pos.mainloop()

    def abrir_inventario(self):
        messagebox.showinfo("POS-Kontrol", "Módulo de Inventario disponible en la siguiente iteración.")

    def abrir_arqueo(self):
        messagebox.showinfo("POS-Kontrol", "Módulo de Arqueo y Reportes disponible próximamente.")