import tkinter as tk
from tkinter import messagebox, ttk

from models.Modelo import ModeloInventario
from views.tema import (
    ACENTO,
    ACENTO_OSCURO,
    BORDE,
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
    # Dejo todos los precios con el mismo formato en pantalla.
    return f"$ {valor:,.0f}".replace(",", ".")


class VentanaPOS(tk.Frame):
    def __init__(self, parent, usuario_actual, al_guardar=None):
        # Preparo el carrito, el método de pago y los productos para vender.
        super().__init__(parent, bg=FONDO)
        configurar_estilos(self.winfo_toplevel())
        self.usuario_actual = usuario_actual
        self.modelo = ModeloInventario()
        self.modelo.cargar_datos_prueba()
        self.al_guardar = al_guardar
        self.carrito = {}
        self.total_pagar = 0
        self.metodo_pago = tk.StringVar(value="Efectivo")
        self.resultados_actuales = []

        self._crear_interfaz()
        self._actualizar_carrito()
        self.winfo_toplevel().bind("<F12>", self._atajo_procesar)

    def _crear_interfaz(self):
        # Separo la búsqueda y el carrito de la sección para cobrar.
        titulo = tk.Frame(self, bg=FONDO)
        titulo.pack(fill="x", pady=(0, 14))
        crear_etiqueta(
            titulo, "Nueva venta", bg=FONDO, tamano=20, negrita=True
        ).pack(side="left")
        crear_etiqueta(
            titulo,
            f"Venta #{self.modelo.obtener_reporte_dia()['cantidad'] + 1:05d}  ·  En curso",
            bg=FONDO,
            color=TEXTO_SUAVE,
            tamano=9,
        ).pack(side="left", padx=16, pady=(7, 0))

        cuerpo = tk.Frame(self, bg=FONDO)
        cuerpo.pack(fill="both", expand=True)
        cuerpo.grid_columnconfigure(0, weight=7, uniform="pos")
        cuerpo.grid_columnconfigure(1, weight=4, uniform="pos")
        cuerpo.grid_rowconfigure(1, weight=1)

        busqueda = crear_tarjeta(cuerpo, padx=16, pady=14)
        busqueda.grid(row=0, column=0, sticky="ew", padx=(0, 12), pady=(0, 12))
        crear_etiqueta(
            busqueda,
            "Escanea el código de barras o busca un producto",
            color=TEXTO_SUAVE,
            tamano=9,
        ).pack(anchor="w", pady=(0, 8))

        fila_busqueda = tk.Frame(busqueda, bg=PANEL)
        fila_busqueda.pack(fill="x")
        self.entry_busqueda = tk.Entry(
            fila_busqueda,
            bg=PANEL_SECUNDARIO,
            fg=TEXTO,
            insertbackground=ACENTO,
            relief="flat",
            font=("Segoe UI", 11),
        )
        self.entry_busqueda.pack(side="left", fill="x", expand=True, ipady=9)
        self.entry_busqueda.bind("<KeyRelease>", self._actualizar_sugerencias)
        self.entry_busqueda.bind("<Return>", self._agregar_primer_resultado)
        crear_boton(
            fila_busqueda,
            "Agregar",
            self._agregar_primer_resultado,
            principal=True,
        ).pack(side="left", padx=(10, 0))

        self.lista_sugerencias = tk.Listbox(
            busqueda,
            height=4,
            bg=PANEL_SECUNDARIO,
            fg=TEXTO,
            selectbackground=ACENTO_OSCURO,
            selectforeground=TEXTO,
            relief="flat",
            highlightthickness=0,
            font=("Segoe UI", 9),
        )
        self.lista_sugerencias.bind(
            "<Double-Button-1>", self._agregar_seleccionado
        )
        self.lista_sugerencias.bind(
            "<Return>", self._agregar_seleccionado
        )

        carrito = crear_tarjeta(cuerpo, padx=14, pady=14)
        carrito.grid(
            row=1, column=0, sticky="nsew", padx=(0, 12), pady=(0, 12)
        )
        barra_carrito = tk.Frame(carrito, bg=PANEL)
        barra_carrito.pack(fill="x", pady=(0, 10))
        crear_etiqueta(
            barra_carrito, "Carrito actual", tamano=12, negrita=True
        ).pack(side="left")
        self.lbl_conteo = crear_etiqueta(
            barra_carrito, "0 artículos", color=TEXTO_SUAVE, tamano=9
        )
        self.lbl_conteo.pack(side="left", padx=10)
        crear_boton(
            barra_carrito, "Vaciar carrito", self._vaciar_carrito, compacto=True
        ).pack(side="right")

        columnas = ("codigo", "nombre", "cantidad", "precio", "subtotal")
        self.tabla = ttk.Treeview(
            carrito,
            columns=columnas,
            show="headings",
            style="POS.Treeview",
            selectmode="browse",
        )
        encabezados = {
            "codigo": ("CÓDIGO", 80, "center"),
            "nombre": ("NOMBRE DEL PRODUCTO", 260, "w"),
            "cantidad": ("CANTIDAD", 75, "center"),
            "precio": ("PRECIO UNITARIO", 115, "e"),
            "subtotal": ("SUBTOTAL", 115, "e"),
        }
        for columna, (texto, ancho, ancla) in encabezados.items():
            self.tabla.heading(columna, text=texto)
            self.tabla.column(columna, width=ancho, anchor=ancla)
        self.tabla.pack(fill="both", expand=True)

        acciones = tk.Frame(carrito, bg=PANEL)
        acciones.pack(fill="x", pady=(10, 0))
        crear_boton(
            acciones, "−  Quitar unidad", lambda: self._cambiar_cantidad(-1),
            compacto=True,
        ).pack(side="left")
        crear_boton(
            acciones, "+  Agregar unidad", lambda: self._cambiar_cantidad(1),
            compacto=True,
        ).pack(side="left", padx=8)
        crear_boton(
            acciones, "Eliminar producto", self._eliminar_seleccionado,
            compacto=True,
        ).pack(side="right")

        cobro = crear_tarjeta(cuerpo, padx=18, pady=18)
        cobro.grid(row=0, column=1, rowspan=2, sticky="nsew", pady=(0, 12))
        crear_etiqueta(
            cobro, "TOTAL A PAGAR", color=TEXTO_SUAVE, tamano=9, negrita=True
        ).pack(anchor="w")
        self.lbl_total = crear_etiqueta(
            cobro, formato_pesos(0), tamano=30, negrita=True
        )
        self.lbl_total.pack(anchor="w", pady=(4, 12))
        crear_etiqueta(
            cobro, "Impuestos aplicables incluidos", color=TEXTO_SUAVE, tamano=8
        ).pack(anchor="w")

        tk.Frame(cobro, bg=BORDE, height=1).pack(fill="x", pady=16)
        crear_etiqueta(
            cobro, "Método de pago", tamano=10, negrita=True
        ).pack(anchor="w", pady=(0, 10))
        fila_metodos = tk.Frame(cobro, bg=PANEL)
        fila_metodos.pack(fill="x")
        self.botones_pago = {}
        for metodo, etiqueta in (
            ("Efectivo", "Efectivo"),
            ("QR", "QR"),
            ("Bold", "Datáfono Bold"),
        ):
            boton = tk.Radiobutton(
                fila_metodos,
                text=etiqueta,
                variable=self.metodo_pago,
                value=metodo,
                command=self._actualizar_pago,
                indicatoron=False,
                bg=PANEL_SECUNDARIO,
                fg=TEXTO,
                selectcolor=ACENTO_OSCURO,
                activebackground=ACENTO_OSCURO,
                activeforeground=TEXTO,
                relief="flat",
                padx=8,
                pady=12,
                font=("Segoe UI", 8, "bold"),
            )
            boton.pack(side="left", fill="x", expand=True, padx=(0, 6))
            self.botones_pago[metodo] = boton

        self.lbl_recibido = crear_etiqueta(
            cobro, "Efectivo recibido (COP)", tamano=9, negrita=True
        )
        self.lbl_recibido.pack(anchor="w", pady=(18, 7))
        self.entry_recibido = tk.Entry(
            cobro,
            bg=PANEL_SECUNDARIO,
            fg=TEXTO,
            insertbackground=ACENTO,
            relief="flat",
            justify="right",
            font=("Segoe UI", 14, "bold"),
        )
        self.entry_recibido.pack(fill="x", ipady=8)
        self.entry_recibido.bind("<KeyRelease>", self._calcular_cambio)

        panel_cambio = tk.Frame(cobro, bg=ACENTO_OSCURO, padx=12, pady=12)
        panel_cambio.pack(fill="x", pady=14)
        crear_etiqueta(
            panel_cambio, "Cambio / Devuelta", bg=ACENTO_OSCURO,
            color=TEXTO_SUAVE, tamano=9,
        ).pack(anchor="w")
        self.lbl_cambio = crear_etiqueta(
            panel_cambio, formato_pesos(0), bg=ACENTO_OSCURO,
            color=ACENTO, tamano=19, negrita=True,
        )
        self.lbl_cambio.pack(anchor="w", pady=(3, 0))

        self.lbl_estado_pago = crear_etiqueta(
            cobro, "Ingresa el efectivo recibido para continuar",
            color=TEXTO_SUAVE, tamano=8, wraplength=310, justify="left",
        )
        self.lbl_estado_pago.pack(anchor="w", pady=(4, 10))
        crear_boton(
            cobro,
            "✓  PROCESAR VENTA  (F12)",
            self.procesar_venta,
            principal=True,
        ).pack(fill="x", ipady=5, side="bottom")

    def _actualizar_sugerencias(self, _event=None):
        # Muestro coincidencias que tengan existencias disponibles.
        texto = self.entry_busqueda.get().strip()
        self.lista_sugerencias.delete(0, tk.END)
        self.resultados_actuales = []
        if not texto:
            self.lista_sugerencias.pack_forget()
            return

        self.resultados_actuales = [
            producto
            for producto in self.modelo.obtener_productos(termino=texto)
            if producto["activo"] and producto["stock"] > 0
        ]
        for producto in self.resultados_actuales:
            self.lista_sugerencias.insert(
                tk.END,
                f"PRD-{producto['id']:04d}  ·  {producto['nombre']}  ·  "
                f"{formato_pesos(producto['precio_venta'])}  ·  "
                f"{producto['stock']} disponibles",
            )
        if self.resultados_actuales:
            self.lista_sugerencias.pack(fill="x", pady=(8, 0))
        else:
            self.lista_sugerencias.pack_forget()

    def _agregar_primer_resultado(self, _event=None):
        # Agrego la primera coincidencia, útil al escanear un código.
        if not self.resultados_actuales:
            self._actualizar_sugerencias()
        if self.resultados_actuales:
            self._agregar_producto(self.resultados_actuales[0])
        return "break"

    def _agregar_seleccionado(self, _event=None):
        # Agrego el producto que se eligió en la lista de resultados.
        seleccion = self.lista_sugerencias.curselection()
        if seleccion:
            self._agregar_producto(self.resultados_actuales[seleccion[0]])
        return "break"

    def _agregar_producto(self, producto):
        # No dejo que el carrito supere las existencias del producto.
        producto_id = producto["id"]
        actual = self.carrito.get(producto_id, {}).get("cantidad", 0)
        if actual >= producto["stock"]:
            messagebox.showwarning(
                "Stock insuficiente",
                f"No hay más unidades disponibles de {producto['nombre']}.",
                parent=self.winfo_toplevel(),
            )
            return
        if producto_id in self.carrito:
            self.carrito[producto_id]["cantidad"] += 1
        else:
            self.carrito[producto_id] = {
                "id": producto_id,
                "nombre": producto["nombre"],
                "precio": producto["precio_venta"],
                "cantidad": 1,
                "stock": producto["stock"],
            }
        self.entry_busqueda.delete(0, tk.END)
        self.lista_sugerencias.pack_forget()
        self._actualizar_carrito()
        self.entry_busqueda.focus_set()

    def _producto_seleccionado(self):
        # Devuelvo el código del producto resaltado en la tabla del carrito.
        seleccion = self.tabla.selection()
        return int(seleccion[0]) if seleccion else None

    def _cambiar_cantidad(self, delta):
        # Ajusto la cantidad del producto seleccionado si hay stock suficiente.
        producto_id = self._producto_seleccionado()
        if producto_id is None:
            return
        item = self.carrito[producto_id]
        nueva_cantidad = item["cantidad"] + delta
        if nueva_cantidad <= 0:
            del self.carrito[producto_id]
        elif nueva_cantidad <= item["stock"]:
            item["cantidad"] = nueva_cantidad
        else:
            messagebox.showwarning(
                "Stock insuficiente",
                "La cantidad supera las existencias disponibles.",
                parent=self.winfo_toplevel(),
            )
        self._actualizar_carrito()

    def _eliminar_seleccionado(self):
        # Quito del carrito el producto seleccionado.
        producto_id = self._producto_seleccionado()
        if producto_id is not None:
            del self.carrito[producto_id]
            self._actualizar_carrito()

    def _vaciar_carrito(self):
        # Dejo el carrito vacío y actualizo los valores que se ven en pantalla.
        self.carrito.clear()
        self._actualizar_carrito()

    def _actualizar_carrito(self):
        # Vuelvo a dibujar los artículos y calculo el total que se va a cobrar.
        for item_id in self.tabla.get_children():
            self.tabla.delete(item_id)
        total_unidades = 0
        self.total_pagar = 0
        for producto_id, item in self.carrito.items():
            subtotal = item["precio"] * item["cantidad"]
            total_unidades += item["cantidad"]
            self.total_pagar += subtotal
            self.tabla.insert(
                "",
                "end",
                iid=str(producto_id),
                values=(
                    f"PRD-{producto_id:04d}",
                    item["nombre"],
                    item["cantidad"],
                    formato_pesos(item["precio"]),
                    formato_pesos(subtotal),
                ),
            )
        self.lbl_conteo.config(text=f"{total_unidades} artículos")
        self.lbl_total.config(text=formato_pesos(self.total_pagar))
        self._actualizar_pago()

    def _monto_recibido(self):
        # Leo el efectivo ingresado; si no es un número, lo dejo sin valor.
        texto = self.entry_recibido.get().strip()
        if not texto:
            return None
        try:
            return float(
                texto.replace("$", "").replace(".", "").replace(",", "").strip()
            )
        except ValueError:
            return None

    def _actualizar_pago(self):
        # Ajusto el campo y el cambio según el método de pago elegido.
        metodo = self.metodo_pago.get()
        if not hasattr(self, "entry_recibido"):
            return
        if metodo == "Efectivo":
            self.lbl_recibido.config(text="Efectivo recibido (COP)")
            self.entry_recibido.config(state="normal")
            self._calcular_cambio()
        else:
            self.lbl_recibido.config(text=f"Pago por {metodo}")
            self.entry_recibido.config(state="normal")
            self.entry_recibido.delete(0, tk.END)
            self.entry_recibido.insert(0, f"{self.total_pagar:.0f}")
            self.entry_recibido.config(state="readonly")
            self.lbl_cambio.config(text=formato_pesos(0))
            self.lbl_estado_pago.config(text="Pago completo; listo para procesar")

    def _calcular_cambio(self, _event=None):
        # Calculo la devolución solo cuando el pago se hace en efectivo.
        if not hasattr(self, "lbl_cambio"):
            return
        if self.metodo_pago.get() != "Efectivo":
            return
        recibido = self._monto_recibido()
        if recibido is None:
            self.lbl_cambio.config(text=formato_pesos(0))
            self.lbl_estado_pago.config(
                text="Ingresa el efectivo recibido para continuar",
                fg=TEXTO_SUAVE,
            )
        elif recibido >= self.total_pagar:
            self.lbl_cambio.config(
                text=formato_pesos(recibido - self.total_pagar), fg=ACENTO
            )
            self.lbl_estado_pago.config(
                text="Efectivo suficiente; listo para procesar",
                fg=ACENTO,
            )
        else:
            self.lbl_cambio.config(text="Falta dinero", fg=ROJO)
            self.lbl_estado_pago.config(
                text="El efectivo recibido no cubre el total", fg=ROJO
            )

    def procesar_venta(self):
        # Reviso el carrito y el pago antes de registrar la venta.
        if not self.carrito:
            messagebox.showwarning(
                "Carrito vacío",
                "Agrega al menos un producto antes de procesar la venta.",
                parent=self.winfo_toplevel(),
            )
            return

        metodo = self.metodo_pago.get()
        recibido = self._monto_recibido()
        if metodo == "Efectivo" and (
            recibido is None or recibido < self.total_pagar
        ):
            messagebox.showwarning(
                "Pago incompleto",
                "Verifica el efectivo recibido antes de continuar.",
                parent=self.winfo_toplevel(),
            )
            return

        efectivo = self.total_pagar if metodo == "Efectivo" else 0
        qr = self.total_pagar if metodo == "QR" else 0
        bold = self.total_pagar if metodo == "Bold" else 0
        try:
            venta_id, total = self.modelo.registrar_venta(
                list(self.carrito.values()),
                efectivo,
                qr,
                bold,
                self.usuario_actual.get("id"),
            )
        except (ValueError, OSError) as error:
            messagebox.showerror(
                "No se pudo procesar la venta",
                str(error),
                parent=self.winfo_toplevel(),
            )
            self._actualizar_sugerencias()
            return
        except Exception as error:
            messagebox.showerror(
                "Error al guardar la venta",
                f"No se guardó la venta. Detalle: {error}",
                parent=self.winfo_toplevel(),
            )
            return

        messagebox.showinfo(
            "Venta registrada",
            f"Venta #{venta_id:05d} guardada correctamente.\n"
            f"Total: {formato_pesos(total)}",
            parent=self.winfo_toplevel(),
        )
        self.carrito.clear()
        self.entry_recibido.config(state="normal")
        self.entry_recibido.delete(0, tk.END)
        self._actualizar_carrito()
        if self.al_guardar:
            self.al_guardar()

    def _atajo_procesar(self, _event=None):
        # Uso F12 como atajo para procesar la venta actual.
        self.procesar_venta()
        return "break"
