import tkinter as tk
from tkinter import ttk, messagebox
import datetime
from models.Modelo import ModeloInventario

class VentanaPOS:
    def __init__(self, root, usuario_actual="Néstor López"):
        self.root = root
        self.root.title("POS-Kontrol - Punto de Venta")
        self.root.geometry("1280x720")
        self.root.configure(bg="#0B0F12")
        
        self.usuario_actual = usuario_actual
        self.modelo_inv = ModeloInventario()
        self.modelo_inv.cargar_datos_prueba()
        
        self.carrito = []
        self.total_pagar = 0.0

        self.crear_header()
        self.crear_cuerpo()
        self.crear_footer()
        self.actualizar_reloj()

    def crear_header(self):
        header_frame = tk.Frame(self.root, bg="#161B22", height=60)
        header_frame.pack(fill="x", side="top")
        
        lbl_logo = tk.Label(header_frame, text="❖ POS-Kontrol", font=("Arial", 16, "bold"), fg="#00E599", bg="#161B22")
        lbl_logo.pack(side="left", padx=20, pady=15)
        
        lbl_sede = tk.Label(header_frame, text="🏪 La Cumbre (Caja 01 - Turno Abierto)", font=("Arial", 10), fg="#8A99AD", bg="#161B22")
        lbl_sede.pack(side="left", padx=10)

        btn_salir = tk.Button(header_frame, text="🚪 Salir", font=("Arial", 10, "bold"), bg="#1E242B", fg="#FFFFFF", relief="flat", cursor="hand2", command=self.root.quit)
        btn_salir.pack(side="right", padx=20)

        lbl_usuario = tk.Label(header_frame, text=f"👤 {self.usuario_actual} (Cajero)", font=("Arial", 10, "bold"), fg="#FFFFFF", bg="#161B22")
        lbl_usuario.pack(side="right", padx=15)

        self.lbl_reloj = tk.Label(header_frame, text="", font=("Arial", 10), fg="#00E599", bg="#161B22")
        self.lbl_reloj.pack(side="right", padx=15)

    def crear_cuerpo(self):
        cuerpo_frame = tk.Frame(self.root, bg="#0B0F12")
        cuerpo_frame.pack(fill="both", expand=True, padx=20, pady=15)

        # PANEL IZQUIERDO: BUSCADOR Y CARRITO
        panel_izq = tk.Frame(cuerpo_frame, bg="#0B0F12")
        panel_izq.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # Buscador y contenedor de autocompletado
        frame_busqueda = tk.Frame(panel_izq, bg="#161B22", padx=15, pady=10)
        frame_busqueda.pack(fill="x", pady=(0, 10))

        lbl_buscar = tk.Label(frame_busqueda, text="🔍 Escribe el nombre o código del producto:", font=("Arial", 10), fg="#8A99AD", bg="#161B22")
        lbl_buscar.pack(anchor="w")

        entry_container = tk.Frame(frame_busqueda, bg="#161B22")
        entry_container.pack(fill="x", pady=(5, 0))

        self.entry_busqueda = tk.Entry(entry_container, font=("Arial", 12), bg="#0B0F12", fg="#FFFFFF", insertbackground="white", relief="flat")
        self.entry_busqueda.pack(fill="x", ipady=6)
        self.entry_busqueda.bind("<KeyRelease>", self.actualizar_sugerencias)
        self.entry_busqueda.bind("<Return>", self.seleccionar_primer_resultado)

        # Lista desplegable de sugerencias
        self.lista_sugerencias = tk.Listbox(frame_busqueda, font=("Arial", 11), bg="#1E242B", fg="#FFFFFF", selectbackground="#00E599", selectforeground="#0B0F12", relief="flat", height=4)
        self.lista_sugerencias.bind("<<ListboxSelect>>", self.seleccionar_desde_lista)

        # Tabla del Carrito de Compras
        frame_tabla = tk.Frame(panel_izq, bg="#161B22", padx=10, pady=10)
        frame_tabla.pack(fill="both", expand=True)

        lbl_carrito_titulo = tk.Label(frame_tabla, text="🛒 Carrito Actual", font=("Arial", 12, "bold"), fg="#FFFFFF", bg="#161B22")
        lbl_carrito_titulo.pack(anchor="w", pady=(0, 10))

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#0B0F12", foreground="#FFFFFF", fieldbackground="#0B0F12", rowheight=30)
        style.configure("Treeview.Heading", background="#1E242B", foreground="#00E599", font=("Arial", 10, "bold"))
        style.map("Treeview", background=[("selected", "#00E599")], foreground=[("selected", "#0B0F12")])

        columnas = ("codigo", "nombre", "cantidad", "precio", "subtotal")
        self.tabla = ttk.Treeview(frame_tabla, columns=columnas, show="headings", style="Treeview")

        self.tabla.heading("codigo", text="CÓDIGO")
        self.tabla.heading("nombre", text="NOMBRE DEL PRODUCTO")
        self.tabla.heading("cantidad", text="CANTIDAD")
        self.tabla.heading("precio", text="PRECIO UNITARIO")
        self.tabla.heading("subtotal", text="SUBTOTAL")

        self.tabla.column("codigo", width=80, anchor="center")
        self.tabla.column("nombre", width=280, anchor="w")
        self.tabla.column("cantidad", width=80, anchor="center")
        self.tabla.column("precio", width=110, anchor="e")
        self.tabla.column("subtotal", width=110, anchor="e")

        self.tabla.pack(fill="both", expand=True)

        # PANEL DERECHO: DETALLE DE COBRO
        panel_der = tk.Frame(cuerpo_frame, bg="#161B22", width=380, padx=20, pady=20)
        panel_der.pack(side="right", fill="y")
        panel_der.pack_propagate(False)

        lbl_total_titulo = tk.Label(panel_der, text="TOTAL A PAGAR", font=("Arial", 11, "bold"), fg="#8A99AD", bg="#161B22")
        lbl_total_titulo.pack(anchor="w")

        self.lbl_total_monto = tk.Label(panel_der, text="$ 0", font=("Arial", 30, "bold"), fg="#FFFFFF", bg="#161B22")
        self.lbl_total_monto.pack(anchor="w", pady=(0, 15))

        lbl_metodo = tk.Label(panel_der, text="Método de Pago", font=("Arial", 10, "bold"), fg="#FFFFFF", bg="#161B22")
        lbl_metodo.pack(anchor="w", pady=(10, 5))

        frame_metodos = tk.Frame(panel_der, bg="#161B22")
        frame_metodos.pack(fill="x", pady=5)

        self.btn_efectivo = tk.Button(frame_metodos, text="💵 Efectivo", font=("Arial", 9, "bold"), bg="#00E599", fg="#0B0F12", relief="flat", cursor="hand2")
        self.btn_efectivo.pack(side="left", fill="x", expand=True, padx=2)

        self.btn_qr = tk.Button(frame_metodos, text="📱 QR", font=("Arial", 9, "bold"), bg="#0B0F12", fg="#FFFFFF", relief="flat", cursor="hand2")
        self.btn_qr.pack(side="left", fill="x", expand=True, padx=2)

        self.btn_bold = tk.Button(frame_metodos, text="💳 Bold", font=("Arial", 9, "bold"), bg="#0B0F12", fg="#FFFFFF", relief="flat", cursor="hand2")
        self.btn_bold.pack(side="left", fill="x", expand=True, padx=2)

        lbl_recibido = tk.Label(panel_der, text="Efectivo Recibido ($ COP)", font=("Arial", 10, "bold"), fg="#FFFFFF", bg="#161B22")
        lbl_recibido.pack(anchor="w", pady=(20, 5))

        self.entry_recibido = tk.Entry(panel_der, font=("Arial", 16, "bold"), bg="#0B0F12", fg="#00E599", insertbackground="white", relief="flat", justify="right")
        self.entry_recibido.pack(fill="x", ipady=8)
        self.entry_recibido.bind("<KeyRelease>", self.calcular_cambio)

        frame_cambio = tk.Frame(panel_der, bg="#0B0F12", padx=15, pady=10)
        frame_cambio.pack(fill="x", pady=15)

        lbl_cambio_tit = tk.Label(frame_cambio, text="Cambio / Devuelta", font=("Arial", 9), fg="#8A99AD", bg="#0B0F12")
        lbl_cambio_tit.pack(anchor="w")

        self.lbl_cambio_monto = tk.Label(frame_cambio, text="$ 0", font=("Arial", 18, "bold"), fg="#00E599", bg="#0B0F12")
        self.lbl_cambio_monto.pack(anchor="w")

        btn_procesar = tk.Button(
            panel_der, text="✔ PROCESAR VENTA (F12)", font=("Arial", 12, "bold"),
            bg="#00E599", fg="#0B0F12", activebackground="#00B377", relief="flat",
            cursor="hand2", command=self.procesar_venta
        )
        btn_procesar.pack(fill="x", ipady=12, side="bottom")

    def crear_footer(self):
        footer_frame = tk.Frame(self.root, bg="#161B22", height=30)
        footer_frame.pack(fill="x", side="bottom")

        lbl_estado = tk.Label(footer_frame, text="🟢 Búsqueda inteligente activada | Terminal 01", font=("Arial", 8), fg="#00E599", bg="#161B22")
        lbl_estado.pack(side="left", padx=15, pady=5)

        lbl_atajos = tk.Label(footer_frame, text="[Flechas/Click] Seleccionar Producto  |  [F12] Procesar Venta", font=("Arial", 8), fg="#8A99AD", bg="#161B22")
        lbl_atajos.pack(side="right", padx=15, pady=5)

    def actualizar_reloj(self):
        ahora = datetime.datetime.now().strftime("%I:%M:%S %p | %d %b %Y")
        self.lbl_reloj.config(text=ahora)
        self.root.after(1000, self.actualizar_reloj)

    def actualizar_sugerencias(self, event):
        texto = self.entry_busqueda.get().strip()
        self.lista_sugerencias.delete(0, tk.END)

        if not texto:
            self.lista_sugerencias.pack_forget()
            return

        resultados = self.modelo_inv.buscar_productos(texto)
        if resultados:
            for prod in resultados:
                display_text = f"[{prod['id']}] {prod['nombre']} - $ {prod['precio_venta']:,.0f} (Stock: {prod['stock']})"
                self.lista_sugerencias.insert(tk.END, display_text)
            
            self.resultados_actuales = resultados
            self.lista_sugerencias.pack(fill="x", pady=(2, 0))
        else:
            self.lista_sugerencias.pack_forget()

    def seleccionar_desde_lista(self, event):
        seleccion = self.lista_sugerencias.curselection()
        if not seleccion:
            return
        
        index = seleccion[0]
        prod = self.resultados_actuales[index]
        self.agregar_al_carrito(prod)

    def seleccionar_primer_resultado(self, event):
        if hasattr(self, 'resultados_actuales') and self.resultados_actuales:
            self.agregar_al_carrito(self.resultados_actuales[0])

    def agregar_al_carrito(self, prod):
        id_p, nombre, precio, stock = prod['id'], prod['nombre'], prod['precio_venta'], prod['stock']

        if stock <= 0:
            messagebox.showerror("Stock Agotado", f"El producto '{nombre}' no tiene existencias disponibles.")
            return

        encontrado = False
        for item in self.carrito:
            if item['id'] == id_p:
                item['cantidad'] += 1
                item['subtotal'] = item['cantidad'] * item['precio']
                encontrado = True
                break

        if not encontrado:
            self.carrito.append({
                'id': id_p,
                'nombre': nombre,
                'cantidad': 1,
                'precio': precio,
                'subtotal': precio
            })

        self.entry_busqueda.delete(0, tk.END)
        self.lista_sugerencias.pack_forget()
        self.actualizar_tabla_y_totales()

    def actualizar_tabla_y_totales(self):
        for row in self.tabla.get_children():
            self.tabla.delete(row)

        self.total_pagar = 0.0
        for item in self.carrito:
            self.tabla.insert("", "end", values=(
                f"PRD-{item['id']:03d}",
                item['nombre'],
                item['cantidad'],
                f"$ {item['precio']:,.0f}",
                f"$ {item['subtotal']:,.0f}"
            ))
            self.total_pagar += item['subtotal']

        self.lbl_total_monto.config(text=f"$ {self.total_pagar:,.0f}")
        self.calcular_cambio()

    def calcular_cambio(self, event=None):
        recibido_str = self.entry_recibido.get().strip()
        if not recibido_str:
            self.lbl_cambio_monto.config(text="$ 0")
            return

        try:
            recibido = float(recibido_str)
            cambio = recibido - self.total_pagar
            if cambio >= 0:
                self.lbl_cambio_monto.config(text=f"$ {cambio:,.0f}", fg="#00E599")
            else:
                self.lbl_cambio_monto.config(text="Falta dinero", fg="#FF5555")
        except ValueError:
            self.lbl_cambio_monto.config(text="Monto inválido", fg="#FF5555")

    def procesar_venta(self):
        if not self.carrito:
            messagebox.showwarning("Carrito vacío", "Agregue al menos un producto antes de procesar la venta.")
            return

        messagebox.showinfo("¡Venta Registrada!", f"Venta procesada con éxito por un total de: $ {self.total_pagar:,.0f}")
        self.carrito.clear()
        self.entry_recibido.delete(0, tk.END)
        self.actualizar_tabla_y_totales()