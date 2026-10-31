import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from models.Modelo import ModeloInventario
from views.exportar_pdf import exportar_inventario_pdf
from views.tema import (
    ACENTO,
    FONDO,
    PANEL,
    PANEL_SECUNDARIO,
    ROJO,
    TEXTO,
    TEXTO_SUAVE,
    configurar_estilos,
    crear_boton,
    crear_etiqueta,
    crear_tarjeta,
)


def formato_pesos(valor):
    # Muestro los montos en pesos sin decimales y con separador de miles.
    return f"$ {valor:,.0f}".replace(",", ".")


class VentanaInventario(tk.Frame):
    def __init__(self, parent, al_cambiar=None):
        # Cargo los filtros y preparo la tabla al abrir el inventario.
        super().__init__(parent, bg=FONDO)
        configurar_estilos(self.winfo_toplevel())
        self.modelo = ModeloInventario()
        self.modelo.cargar_datos_prueba()
        self.al_cambiar = al_cambiar
        self.busqueda = tk.StringVar()
        self.categoria = tk.StringVar(value="Todas")
        self.estado = tk.StringVar(value="Todos")

        self._crear_interfaz()
        self.actualizar_tabla()

    def _crear_interfaz(self):
        # Organizo la pantalla en filtros, indicadores y tabla de productos.
        encabezado = tk.Frame(self, bg=FONDO)
        encabezado.pack(fill="x", pady=(0, 14))
        texto = tk.Frame(encabezado, bg=FONDO)
        texto.pack(side="left", fill="x", expand=True)
        crear_etiqueta(
            texto, "Gestión de Inventario", bg=FONDO, tamano=20, negrita=True
        ).pack(anchor="w")
        crear_etiqueta(
            texto,
            "Consulta tus productos, controla existencias y mantén los precios al día.",
            bg=FONDO,
            color=TEXTO_SUAVE,
            tamano=9,
        ).pack(anchor="w", pady=(4, 0))
        crear_boton(
            encabezado, "+  Nuevo Producto", self._abrir_nuevo,
            principal=True,
        ).pack(side="right", padx=(12, 0))
        crear_boton(
            encabezado, "Exportar Inventario", self.exportar_catalogo,
        ).pack(side="right")

        filtros = crear_tarjeta(self, padx=12, pady=10)
        filtros.pack(fill="x", pady=(0, 12))
        self.entry_busqueda = tk.Entry(
            filtros,
            textvariable=self.busqueda,
            bg=PANEL_SECUNDARIO,
            fg=TEXTO,
            insertbackground=ACENTO,
            relief="flat",
            font=("Segoe UI", 9),
        )
        self.entry_busqueda.insert(0, "Buscar por nombre o código...")
        self.entry_busqueda.pack(side="left", fill="x", expand=True, ipady=8)
        self.entry_busqueda.bind("<FocusIn>", self._limpiar_placeholder)
        self.entry_busqueda.bind("<KeyRelease>", self._filtrar)

        categorias = ["Todas"] + [
            fila["nombre"] for fila in self.modelo.obtener_categorias()
        ]
        self.combo_categoria = ttk.Combobox(
            filtros,
            textvariable=self.categoria,
            values=categorias,
            state="readonly",
            style="POS.TCombobox",
            width=18,
        )
        self.combo_categoria.pack(side="left", padx=(10, 0), ipady=5)
        self.combo_categoria.bind("<<ComboboxSelected>>", self._filtrar)
        self.combo_estado = ttk.Combobox(
            filtros,
            textvariable=self.estado,
            values=("Todos", "En stock", "Stock bajo", "Inactivos"),
            state="readonly",
            style="POS.TCombobox",
            width=14,
        )
        self.combo_estado.pack(side="left", padx=(10, 0), ipady=5)
        self.combo_estado.bind("<<ComboboxSelected>>", self._filtrar)

        kpis = tk.Frame(self, bg=FONDO)
        kpis.pack(fill="x", pady=(0, 12))
        for columna in range(3):
            kpis.grid_columnconfigure(columna, weight=1, uniform="kpi")
        self.kpi_productos = self._crear_kpi(
            kpis, "Total de accesorios", "0", "Referencias activas", 0
        )
        self.kpi_bajo = self._crear_kpi(
            kpis, "Alerta de stock bajo", "0", "Requieren reposición", 1
        )
        self.kpi_valor = self._crear_kpi(
            kpis, "Valor del inventario", "$ 0", "Calculado al precio de costo", 2
        )

        tabla_panel = crear_tarjeta(self, padx=12, pady=12)
        tabla_panel.pack(fill="both", expand=True)
        barra = tk.Frame(tabla_panel, bg=PANEL)
        barra.pack(fill="x", pady=(0, 9))
        crear_etiqueta(
            barra, "Accesorios", tamano=11, negrita=True
        ).pack(side="left")
        self.lbl_resultados = crear_etiqueta(
            barra, "", color=TEXTO_SUAVE, tamano=8
        )
        self.lbl_resultados.pack(side="left", padx=8)
        crear_boton(
            barra, "Editar seleccionado", self._editar_seleccionado,
            compacto=True,
        ).pack(side="right")

        columnas = (
            "codigo", "nombre", "categoria", "stock", "costo", "venta", "estado"
        )
        self.tabla = ttk.Treeview(
            tabla_panel, columns=columnas, show="headings", style="POS.Treeview"
        )
        definiciones = (
            ("codigo", "SKU / CÓDIGO", 100, "center"),
            ("nombre", "NOMBRE DEL ACCESORIO", 240, "w"),
            ("categoria", "CATEGORÍA", 125, "w"),
            ("stock", "EXISTENCIAS", 90, "center"),
            ("costo", "PRECIO DE COSTO", 115, "e"),
            ("venta", "PRECIO DE VENTA", 115, "e"),
            ("estado", "ESTADO", 95, "center"),
        )
        for clave, etiqueta, ancho, ancla in definiciones:
            self.tabla.heading(clave, text=etiqueta)
            self.tabla.column(clave, width=ancho, anchor=ancla)
        self.tabla.tag_configure("bajo", foreground=ROJO)
        self.tabla.pack(fill="both", expand=True)
        self.tabla.bind("<Double-Button-1>", self._editar_seleccionado)

    def _crear_kpi(self, parent, titulo, valor, detalle, columna):
        # Presento una cifra del inventario con su título y una nota breve.
        tarjeta = crear_tarjeta(parent, padx=14, pady=12)
        tarjeta.grid(row=0, column=columna, sticky="ew", padx=(0, 10))
        crear_etiqueta(
            tarjeta, titulo, color=TEXTO_SUAVE, tamano=8
        ).pack(anchor="w")
        numero = crear_etiqueta(
            tarjeta, valor, tamano=20, negrita=True
        )
        numero.pack(anchor="w", pady=(5, 1))
        crear_etiqueta(
            tarjeta, detalle, color=TEXTO_SUAVE, tamano=8
        ).pack(anchor="w")
        return numero

    def _limpiar_placeholder(self, _event=None):
        # Quito el texto de ejemplo cuando se empieza a escribir una búsqueda.
        if self.entry_busqueda.get() == "Buscar por nombre o código...":
            self.entry_busqueda.delete(0, tk.END)

    def _filtrar(self, _event=None):
        # Leo el texto de búsqueda y vuelvo a cargar los resultados.
        termino = self.entry_busqueda.get()
        if termino == "Buscar por nombre o código...":
            termino = ""
        self.actualizar_tabla(termino)

    def actualizar_tabla(self, termino=""):
        # Actualizo los indicadores y las filas según los filtros actuales.
        productos = self.modelo.obtener_productos(
            termino=termino,
            categoria=self.categoria.get(),
            estado=self.estado.get(),
        )
        todos = self.modelo.obtener_productos(estado="Todos")
        activos = [producto for producto in todos if producto["activo"]]
        bajos = [
            producto for producto in activos
            if producto["stock"] <= producto["stock_minimo"]
        ]
        valor = sum(
            producto["stock"] * producto["precio_compra"]
            for producto in activos
        )
        self.kpi_productos.config(text=str(len(activos)))
        self.kpi_bajo.config(text=str(len(bajos)))
        self.kpi_valor.config(text=formato_pesos(valor))

        for item_id in self.tabla.get_children():
            self.tabla.delete(item_id)
        for producto in productos:
            bajo = producto["stock"] <= producto["stock_minimo"]
            activo = bool(producto["activo"])
            estado = "Inactivo" if not activo else ("Stock bajo" if bajo else "En stock")
            valores = (
                f"PRD-{producto['id']:04d}",
                producto["nombre"],
                producto["categoria"],
                f"{producto['stock']} uds.",
                formato_pesos(producto["precio_compra"]),
                formato_pesos(producto["precio_venta"]),
                estado,
            )
            self.tabla.insert(
                "", "end", iid=str(producto["id"]), values=valores,
                tags=("bajo",) if bajo or not activo else (),
            )
        self.lbl_resultados.config(text=f"{len(productos)} resultados")

    def _abrir_nuevo(self):
        # El formulario sin producto seleccionado sirve para crear uno nuevo.
        self._abrir_formulario()

    def _editar_seleccionado(self, _event=None):
        # Busco el producto elegido y abro sus datos para editarlos.
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showinfo(
                "Editar accesorio",
                "Selecciona un accesorio de la tabla.",
                parent=self.winfo_toplevel(),
            )
            return
        producto_id = int(seleccion[0])
        producto = next(
            (
                fila for fila in self.modelo.obtener_productos(estado="Todos")
                if fila["id"] == producto_id
            ),
            None,
        )
        if producto:
            self._abrir_formulario(producto)

    def _abrir_formulario(self, producto=None):
        # Reutilizo el formulario para crear un producto o editarlo.
        categorias = self.modelo.obtener_categorias()
        if not categorias:
            messagebox.showerror(
                "Categorías no disponibles",
                "No hay categorías configuradas en la base de datos.",
                parent=self.winfo_toplevel(),
            )
            return

        ventana = tk.Toplevel(self.winfo_toplevel())
        ventana.title("Editar accesorio" if producto else "Nuevo accesorio")
        ventana.configure(bg=FONDO)
        ventana.transient(self.winfo_toplevel())
        ventana.grab_set()
        ventana.resizable(False, False)
        ventana.geometry("430x520")

        contenedor = tk.Frame(ventana, bg=FONDO, padx=24, pady=20)
        contenedor.pack(fill="both", expand=True)
        crear_etiqueta(
            contenedor,
            "Editar accesorio" if producto else "Nuevo accesorio",
            bg=FONDO,
            tamano=16,
            negrita=True,
        ).pack(anchor="w", pady=(0, 16))

        campos = {}
        definiciones = (
            ("nombre", "Nombre del accesorio"),
            ("categoria", "Categoría"),
            ("costo", "Precio de costo (COP)"),
            ("venta", "Precio de venta (COP)"),
            ("stock", "Existencias"),
            ("minimo", "Stock mínimo"),
        )
        nombres_categoria = [fila["nombre"] for fila in categorias]
        for campo, etiqueta in definiciones:
            crear_etiqueta(
                contenedor, etiqueta, bg=FONDO, color=TEXTO_SUAVE, tamano=9
            ).pack(anchor="w", pady=(7, 4))
            if campo == "categoria":
                combo = ttk.Combobox(
                    contenedor,
                    values=nombres_categoria,
                    state="readonly",
                    style="POS.TCombobox",
                )
                combo.pack(fill="x", ipady=4)
                campos[campo] = combo
            else:
                entrada = tk.Entry(
                    contenedor,
                    bg=PANEL_SECUNDARIO,
                    fg=TEXTO,
                    insertbackground=ACENTO,
                    relief="flat",
                    font=("Segoe UI", 10),
                )
                entrada.pack(fill="x", ipady=7)
                campos[campo] = entrada

        activo = tk.BooleanVar(value=bool(producto["activo"]) if producto else True)
        if producto:
            tk.Checkbutton(
                contenedor,
                text="Accesorio activo",
                variable=activo,
                bg=FONDO,
                fg=TEXTO,
                selectcolor=PANEL_SECUNDARIO,
                activebackground=FONDO,
                activeforeground=TEXTO,
            ).pack(anchor="w", pady=(12, 0))

        if producto:
            valores = {
                "nombre": producto["nombre"],
                "categoria": producto["categoria"],
                "costo": f"{producto['precio_compra']:.0f}",
                "venta": f"{producto['precio_venta']:.0f}",
                "stock": str(producto["stock"]),
                "minimo": str(producto["stock_minimo"]),
            }
            for campo, valor in valores.items():
                widget = campos[campo]
                if campo == "categoria":
                    widget.set(valor if valor in nombres_categoria else nombres_categoria[0])
                else:
                    widget.insert(0, valor)
        else:
            campos["categoria"].current(0)
            campos["stock"].insert(0, "0")
            campos["minimo"].insert(0, "5")

        def guardar():
            # Valido los campos antes de guardar el producto en la base.
            nombre = campos["nombre"].get().strip()
            if not nombre:
                messagebox.showerror(
                    "Datos incompletos",
                    "Escribe el nombre del accesorio.",
                    parent=ventana,
                )
                return
            try:
                costo = self._leer_monto(campos["costo"].get())
                venta = self._leer_monto(campos["venta"].get())
                stock = int(campos["stock"].get().strip())
                minimo = int(campos["minimo"].get().strip())
                if costo < 0 or venta < 0 or stock < 0 or minimo < 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror(
                    "Datos inválidos",
                    "Precios y existencias deben ser números no negativos.",
                    parent=ventana,
                )
                return

            categoria_id = next(
                fila["id"] for fila in categorias
                if fila["nombre"] == campos["categoria"].get()
            )
            if producto:
                resultado = self.modelo.actualizar_producto(
                    producto["id"], nombre, categoria_id, costo, venta,
                    stock, minimo, int(activo.get()),
                )
            else:
                resultado = self.modelo.agregar_producto(
                    nombre, categoria_id, costo, venta, stock, minimo
                )
            exito, mensaje = resultado
            if not exito:
                messagebox.showerror("No se pudo guardar", mensaje, parent=ventana)
                return
            ventana.destroy()
            self.actualizar_tabla()
            if self.al_cambiar:
                self.al_cambiar()

        botones = tk.Frame(contenedor, bg=FONDO)
        botones.pack(fill="x", pady=(18, 0))
        crear_boton(botones, "Cancelar", ventana.destroy).pack(side="right")
        crear_boton(
            botones, "Guardar accesorio", guardar, principal=True
        ).pack(side="right", padx=(0, 8))
        ventana.bind("<Return>", lambda event: guardar())

    @staticmethod
    def _leer_monto(texto):
        # Convierto el precio escrito a un número que pueda guardar el modelo.
        limpio = texto.strip().replace("$", "").replace(".", "").replace(",", "")
        if not limpio:
            raise ValueError
        return float(limpio)

    def exportar_catalogo(self):
        # Pido la ubicación del PDF y exporto los productos del inventario.
        ruta = filedialog.asksaveasfilename(
            parent=self.winfo_toplevel(),
            title="Exportar catálogo",
            defaultextension=".pdf",
            filetypes=(("Documento PDF", "*.pdf"),),
            initialfile="catalogo_inventario.pdf",
        )
        if not ruta:
            return
        try:
            productos = self.modelo.obtener_productos(estado="Todos")
            exportar_inventario_pdf(ruta, productos)
        except (OSError, ValueError) as error:
            messagebox.showerror(
                "Error al exportar", str(error), parent=self.winfo_toplevel()
            )
            return
        messagebox.showinfo(
            "Catálogo PDF exportado",
            f"El archivo se guardó en:\n{ruta}",
            parent=self.winfo_toplevel(),
        )
