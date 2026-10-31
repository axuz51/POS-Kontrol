import sqlite3
import tkinter as tk
from datetime import date
from tkinter import filedialog, messagebox, ttk

from models.Modelo import ModeloInventario
from views.exportar_pdf import exportar_cierre_pdf
from views.tema import (
    ACENTO,
    ACENTO_OSCURO,
    FONDO,
    PANEL,
    PANEL_SECUNDARIO,
    TEXTO,
    TEXTO_SUAVE,
    configurar_estilos,
    crear_boton,
    crear_etiqueta,
    crear_tarjeta,
)


# Muestro los valores en pesos sin decimales y con separador de miles.
def formato_pesos(valor):
    return f"$ {valor:,.0f}".replace(",", ".")


class VentanaReportes(tk.Frame):
    def __init__(self, parent, usuario_actual, al_cambiar=None):
        super().__init__(parent, bg=FONDO)
        configurar_estilos(self.winfo_toplevel())
        # Guardo los datos que necesito para el reporte y el cierre de caja.
        self.modelo = ModeloInventario()
        self.usuario_actual = usuario_actual
        self.al_cambiar = al_cambiar
        self.fecha = date.today().isoformat()
        self.resumen = {}
        self.saldos_iniciales = self.modelo.obtener_saldos_iniciales(
            self.fecha
        )

        self._crear_interfaz()
        self.actualizar_reporte()

    def _crear_interfaz(self):
        # Organizo la pantalla en el resumen de ventas y el arqueo de los fondos.
        encabezado = tk.Frame(self, bg=FONDO)
        encabezado.pack(fill="x", pady=(0, 14))
        texto = tk.Frame(encabezado, bg=FONDO)
        texto.pack(side="left", fill="x", expand=True)
        crear_etiqueta(
            texto, "Cierre de Caja y Reportes",
            bg=FONDO, tamano=20, negrita=True,
        ).pack(anchor="w")
        crear_etiqueta(
            texto,
            f"Resumen de ventas y movimientos del {self.fecha}",
            bg=FONDO, color=TEXTO_SUAVE, tamano=9,
        ).pack(anchor="w", pady=(4, 0))
        crear_boton(
            encabezado, "Exportar reporte PDF", self.exportar_reporte,
        ).pack(side="right")

        kpis = tk.Frame(self, bg=FONDO)
        kpis.pack(fill="x", pady=(0, 12))
        for columna in range(4):
            kpis.grid_columnconfigure(columna, weight=1, uniform="reportes")
        self.kpi_total = self._crear_kpi(kpis, "Ventas totales del día", "$ 0", 0)
        self.kpi_efectivo = self._crear_kpi(kpis, "Ventas en efectivo", "$ 0", 1)
        self.kpi_qr = self._crear_kpi(kpis, "Ventas por QR", "$ 0", 2)
        self.kpi_bold = self._crear_kpi(kpis, "Ventas por datáfono", "$ 0", 3)

        contenido = tk.Frame(self, bg=FONDO)
        contenido.pack(fill="both", expand=True)
        contenido.grid_columnconfigure(0, weight=6, uniform="columnas")
        contenido.grid_columnconfigure(1, weight=4, uniform="columnas")
        contenido.grid_rowconfigure(0, weight=1)

        izquierda = tk.Frame(contenido, bg=FONDO)
        izquierda.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        derecha = crear_tarjeta(contenido, padx=16, pady=16)
        derecha.grid(row=0, column=1, sticky="nsew")

        resumen = crear_tarjeta(izquierda, padx=16, pady=14)
        resumen.pack(fill="x", pady=(0, 12))
        crear_etiqueta(
            resumen, "Ventas del día", tamano=12, negrita=True
        ).pack(anchor="w")
        crear_etiqueta(
            resumen,
            "Costo, total y ganancia de la jornada",
            color=TEXTO_SUAVE,
            tamano=8,
        ).pack(anchor="w", pady=(3, 10))
        self.filas_resumen = {}
        for clave, etiqueta in (
            ("costos", "Costo de mercancía"),
            ("total", "Total vendido"),
            ("total_mes", "Total vendido en el mes"),
            ("ganancia", "Ganancia bruta"),
            ("egresos", "Egresos de caja menor"),
            ("neta", "Ganancia neta estimada"),
        ):
            # Dejo el total del día y el del mes juntos para compararlos rápido.
            if clave == "total":
                fila_totales = tk.Frame(resumen, bg=PANEL)
                fila_totales.pack(fill="x", pady=5)
                for clave_total, etiqueta_total in (
                    ("total", "Total vendido hoy"),
                    ("total_mes", "Total vendido en el mes"),
                ):
                    bloque = tk.Frame(fila_totales, bg=PANEL)
                    bloque.pack(side="left", fill="x", expand=True)
                    crear_etiqueta(
                        bloque, etiqueta_total, color=TEXTO_SUAVE, tamano=8
                    ).pack(anchor="w")
                    valor = crear_etiqueta(
                        bloque, "$ 0", tamano=9, negrita=True
                    )
                    valor.pack(anchor="w", pady=(2, 0))
                    self.filas_resumen[clave_total] = valor
                continue
            if clave == "total_mes":
                continue
            fila = tk.Frame(resumen, bg=PANEL)
            fila.pack(fill="x", pady=5)
            crear_etiqueta(
                fila, etiqueta, color=TEXTO_SUAVE, tamano=9
            ).pack(side="left")
            valor = crear_etiqueta(
                fila, "$ 0", tamano=9, negrita=True
            )
            valor.pack(side="right")
            self.filas_resumen[clave] = valor
        # Separo visualmente la reserva para reponer productos de la ganancia.
        distribucion = tk.Frame(resumen, bg=PANEL)
        distribucion.pack(fill="x", pady=(11, 4))
        distribucion.grid_columnconfigure(0, weight=1, uniform="fondos")
        distribucion.grid_columnconfigure(1, weight=1, uniform="fondos")

        fondo_reposicion = tk.Frame(
            distribucion, bg="#172A27", padx=11, pady=10
        )
        fondo_reposicion.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        crear_etiqueta(
            fondo_reposicion, "RESERVA PARA REPONER PRODUCTOS",
            bg="#172A27", color=TEXTO_SUAVE, tamano=7, wraplength=190,
        ).pack(anchor="w")
        self.lbl_reserva_reposicion = crear_etiqueta(
            fondo_reposicion, "$ 0",
            bg="#172A27", color=ACENTO, tamano=15, negrita=True,
        )
        self.lbl_reserva_reposicion.pack(anchor="w", pady=(5, 0))

        fondo_ganancia = tk.Frame(
            distribucion, bg="#252420", padx=11, pady=10
        )
        fondo_ganancia.grid(row=0, column=1, sticky="ew", padx=(5, 0))
        crear_etiqueta(
            fondo_ganancia, "GANANCIA DISPONIBLE",
            bg="#252420", color=TEXTO_SUAVE, tamano=7, wraplength=190,
        ).pack(anchor="w")
        self.lbl_ganancia_disponible = crear_etiqueta(
            fondo_ganancia, "$ 0",
            bg="#252420", color="#E6AD55", tamano=15, negrita=True,
        )
        self.lbl_ganancia_disponible.pack(anchor="w", pady=(5, 0))
        crear_etiqueta(
            resumen,
            "Costo y ganancia calculados sobre todas las ventas; "
            "los gastos se restan de la ganancia.",
            color=TEXTO_SUAVE, tamano=7, wraplength=500, justify="left",
        ).pack(anchor="w", pady=(4, 0))
        self.lbl_cantidad_ventas = crear_etiqueta(
            resumen, "0 ventas registradas",
            color=TEXTO_SUAVE, tamano=8,
        )
        self.lbl_cantidad_ventas.pack(anchor="w", pady=(12, 0))

        # En estas pestañas muestro el detalle de ventas y los gastos registrados.
        panel_detalles = tk.Frame(izquierda, bg=FONDO)
        panel_detalles.pack(fill="both", expand=True)
        pestanas = ttk.Notebook(panel_detalles, style="POS.TNotebook")
        pestanas.pack(fill="both", expand=True)

        productos = tk.Frame(pestanas, bg=PANEL, padx=12, pady=12)
        pestanas.add(productos, text="Productos vendidos")
        crear_etiqueta(
            productos, "Detalle de productos vendidos hoy",
            tamano=11, negrita=True,
        ).pack(anchor="w", pady=(0, 8))
        columnas_productos = ("codigo", "producto", "cantidad", "total")
        self.tabla_productos = ttk.Treeview(
            productos,
            columns=columnas_productos,
            show="headings",
            style="POS.Treeview",
            height=6,
        )
        for clave, etiqueta, ancho, ancla in (
            ("codigo", "CÓDIGO", 75, "center"),
            ("producto", "PRODUCTO", 230, "w"),
            ("cantidad", "UNIDADES", 75, "center"),
            ("total", "TOTAL VENDIDO", 105, "e"),
        ):
            self.tabla_productos.heading(clave, text=etiqueta)
            self.tabla_productos.column(clave, width=ancho, anchor=ancla)
        self.tabla_productos.pack(fill="both", expand=True)
        self.lbl_sin_productos = crear_etiqueta(
            productos,
            "Todavía no hay productos vendidos hoy.",
            color=TEXTO_SUAVE,
            tamano=8,
        )

        movimientos = tk.Frame(pestanas, bg=PANEL, padx=12, pady=12)
        pestanas.add(movimientos, text="Caja menor")
        barra_movimientos = tk.Frame(movimientos, bg=PANEL)
        barra_movimientos.pack(fill="x", pady=(0, 8))
        crear_etiqueta(
            barra_movimientos, "Gastos y movimientos de caja menor",
            tamano=11, negrita=True,
        ).pack(side="left")
        crear_boton(
            barra_movimientos, "+  Agregar gasto",
            self.abrir_formulario_egreso, principal=True, compacto=True,
        ).pack(side="right")
        columnas = ("hora", "categoria", "descripcion", "monto")
        self.tabla_movimientos = ttk.Treeview(
            movimientos,
            columns=columnas,
            show="headings",
            style="POS.Treeview",
            height=6,
        )
        for clave, etiqueta, ancho, ancla in (
            ("hora", "HORA", 65, "center"),
            ("categoria", "CONCEPTO", 105, "w"),
            ("descripcion", "DESCRIPCIÓN", 210, "w"),
            ("monto", "IMPORTE", 100, "e"),
        ):
            self.tabla_movimientos.heading(clave, text=etiqueta)
            self.tabla_movimientos.column(clave, width=ancho, anchor=ancla)
        self.tabla_movimientos.pack(fill="both", expand=True)
        self.lbl_sin_movimientos = crear_etiqueta(
            movimientos,
            "No hay movimientos de caja menor registrados hoy.",
            color=TEXTO_SUAVE,
            tamano=8,
        )
        self.lbl_sin_movimientos.pack(anchor="w", pady=(7, 0))

        encabezado_caja = tk.Frame(derecha, bg=PANEL)
        encabezado_caja.pack(fill="x")
        crear_etiqueta(
            encabezado_caja, "Resumen de arqueo", tamano=12, negrita=True
        ).pack(side="left")
        crear_etiqueta(
            encabezado_caja, "● Turno abierto",
            bg=ACENTO_OSCURO, color=ACENTO, tamano=8,
        ).pack(side="right", padx=6, pady=4)
        crear_etiqueta(
            derecha,
            "Los saldos iniciales se toman del cierre anterior, incluso si "
            "pertenece al mes pasado.",
            color=TEXTO_SUAVE, tamano=8,
        ).pack(anchor="w", pady=(5, 14))

        # Si todavía no hay un cierre previo, los fondos arrancan en cero.
        tiene_cierre_previo = self.saldos_iniciales["tiene_cierre_previo"]
        texto_inicio = (
            "Saldos iniciales cargados automáticamente desde el último cierre."
            if tiene_cierre_previo
            else "No hay un cierre anterior; ambos fondos comienzan en $ 0 y "
            "se cargarán automáticamente en los próximos días."
        )
        crear_etiqueta(
            derecha, texto_inicio, color=TEXTO_SUAVE, tamano=8,
            wraplength=310, justify="left",
        ).pack(anchor="w", pady=(0, 8))

        self._crear_panel_fondo(
            derecha,
            clave="costos",
            titulo="FONDO DE COSTOS · REPOSICIÓN",
            texto_saldo="Saldo inicial de costos",
            texto_movimiento="Costo de productos vendidos hoy",
            texto_esperado="Esperado en costos",
            texto_contado="Efectivo contado en costos",
            valor_inicial=self.saldos_iniciales["costos"],
            color="#172A27",
        )
        self._crear_panel_fondo(
            derecha,
            clave="ganancias",
            titulo="FONDO DE GANANCIAS",
            texto_saldo="Saldo inicial de ganancias",
            texto_movimiento="Ganancia de hoy, después de gastos",
            texto_esperado="Esperado en ganancias",
            texto_contado="Efectivo contado en ganancias",
            valor_inicial=self.saldos_iniciales["ganancias"],
            color="#252420",
        )

        self.lbl_diferencia = crear_etiqueta(
            derecha,
            "Diferencia total: $ 0",
            color=ACENTO,
            tamano=9,
            negrita=True,
        )
        self.lbl_diferencia.pack(anchor="w", pady=(10, 8))
        crear_boton(
            derecha, "🔒  GUARDAR CIERRE DE LOS DOS FONDOS",
            self.efectuar_cierre, principal=True,
        ).pack(fill="x", ipady=4)
        crear_etiqueta(
            derecha,
            "Los conteos de hoy pasarán a ser los saldos iniciales de mañana.",
            color=TEXTO_SUAVE, tamano=8, wraplength=310,
        ).pack(anchor="center", pady=(8, 0))

    def _crear_kpi(self, parent, titulo, valor, columna):
        # Reutilizo este formato para las cuatro cifras principales del día.
        tarjeta = crear_tarjeta(parent, padx=13, pady=12)
        tarjeta.grid(row=0, column=columna, sticky="ew", padx=(0, 9))
        crear_etiqueta(
            tarjeta, titulo, color=TEXTO_SUAVE, tamano=8
        ).pack(anchor="w")
        numero = crear_etiqueta(
            tarjeta, valor, tamano=19, negrita=True
        )
        numero.pack(anchor="w", pady=(7, 0))
        return numero

    def _crear_panel_fondo(
        self,
        parent,
        *,
        clave,
        titulo,
        texto_saldo,
        texto_movimiento,
        texto_esperado,
        texto_contado,
        valor_inicial,
        color,
    ):
        # Cada panel comparte la misma estructura para costos y ganancias.
        panel = tk.Frame(parent, bg=color, padx=10, pady=8)
        panel.pack(fill="x", pady=(0, 7))
        crear_etiqueta(
            panel, titulo, bg=color, color=ACENTO, tamano=8, negrita=True
        ).pack(anchor="w", pady=(0, 3))

        fila_saldo = tk.Frame(panel, bg=color)
        fila_saldo.pack(fill="x", pady=2)
        crear_etiqueta(
            fila_saldo, texto_saldo, bg=color,
            color=TEXTO_SUAVE, tamano=8,
        ).pack(side="left")
        saldo = crear_etiqueta(
            fila_saldo,
            formato_pesos(valor_inicial),
            bg=color,
            color=TEXTO,
            tamano=9,
            negrita=True,
        )
        saldo.pack(side="right")

        fila_movimiento = tk.Frame(panel, bg=color)
        fila_movimiento.pack(fill="x", pady=2)
        crear_etiqueta(
            fila_movimiento, texto_movimiento, bg=color,
            color=TEXTO_SUAVE, tamano=8,
        ).pack(side="left")
        movimiento = crear_etiqueta(
            fila_movimiento, "$ 0", bg=color, tamano=8, negrita=True
        )
        movimiento.pack(side="right")
        setattr(self, f"lbl_movimiento_{clave}", movimiento)

        fila_esperado = tk.Frame(panel, bg=color)
        fila_esperado.pack(fill="x", pady=2)
        crear_etiqueta(
            fila_esperado, texto_esperado, bg=color,
            color=TEXTO, tamano=8, negrita=True,
        ).pack(side="left")
        esperado = crear_etiqueta(
            fila_esperado, "$ 0", bg=color,
            color=ACENTO, tamano=10, negrita=True,
        )
        esperado.pack(side="right")
        setattr(self, f"lbl_esperado_{clave}", esperado)

        fila_contado = tk.Frame(panel, bg=color)
        fila_contado.pack(fill="x", pady=(4, 2))
        crear_etiqueta(
            fila_contado, texto_contado, bg=color,
            color=TEXTO_SUAVE, tamano=8,
        ).pack(side="left")
        entrada_contado = tk.Entry(
            fila_contado,
            bg=PANEL_SECUNDARIO,
            fg=TEXTO,
            insertbackground=ACENTO,
            relief="flat",
            justify="right",
            width=12,
            font=("Segoe UI", 9, "bold"),
        )
        entrada_contado.pack(side="right", ipady=3)
        entrada_contado.bind("<KeyRelease>", self._actualizar_diferencia)
        setattr(self, f"entry_contado_{clave}", entrada_contado)

        diferencia = crear_etiqueta(
            panel, "Diferencia: $ 0", bg=color,
            color=ACENTO, tamano=8, negrita=True,
        )
        diferencia.pack(anchor="e", pady=(2, 0))
        setattr(self, f"lbl_diferencia_{clave}", diferencia)

    def actualizar_reporte(self):
        # Vuelvo a consultar los datos y actualizo las etiquetas del resumen.
        self.resumen = self.modelo.obtener_reporte_dia(self.fecha)
        self.kpi_total.config(text=formato_pesos(self.resumen["total"]))
        self.kpi_efectivo.config(text=formato_pesos(self.resumen["efectivo"]))
        self.kpi_qr.config(text=formato_pesos(self.resumen["qr"]))
        self.kpi_bold.config(text=formato_pesos(self.resumen["bold"]))
        self.filas_resumen["costos"].config(
            text=formato_pesos(self.resumen["costos"])
        )
        self.filas_resumen["total"].config(
            text=formato_pesos(self.resumen["total"])
        )
        self.filas_resumen["total_mes"].config(
            text=formato_pesos(self.resumen["total_mes"])
        )
        self.filas_resumen["ganancia"].config(
            text=formato_pesos(self.resumen["ganancia"])
        )
        self.filas_resumen["egresos"].config(
            text=formato_pesos(self.resumen["egresos"])
        )
        self.filas_resumen["neta"].config(
            text=formato_pesos(self.resumen["ganancia_disponible"])
        )
        self.lbl_reserva_reposicion.config(
            text=formato_pesos(self.resumen["reserva_reposicion"])
        )
        self.lbl_ganancia_disponible.config(
            text=formato_pesos(self.resumen["ganancia_disponible"])
        )
        self.lbl_cantidad_ventas.config(
            text=f"{self.resumen['cantidad']} ventas registradas"
        )
        # Quito las filas anteriores antes de cargar el detalle actualizado.
        for item_id in self.tabla_productos.get_children():
            self.tabla_productos.delete(item_id)
        for producto in self.resumen["productos_vendidos"]:
            self.tabla_productos.insert(
                "",
                "end",
                values=(
                    f"PRD-{producto['producto_id']:04d}",
                    producto["nombre"],
                    producto["cantidad"],
                    formato_pesos(producto["total"]),
                ),
            )
        if self.resumen["productos_vendidos"]:
            self.lbl_sin_productos.pack_forget()
        else:
            self.lbl_sin_productos.pack(anchor="w", pady=(7, 0))

        # Cargo también los movimientos de caja menor de la jornada.
        for item_id in self.tabla_movimientos.get_children():
            self.tabla_movimientos.delete(item_id)
        for movimiento in self.resumen["movimientos"]:
            self.tabla_movimientos.insert(
                "",
                "end",
                values=(
                    movimiento["fecha_hora"][11:16],
                    movimiento["categoria"],
                    movimiento["descripcion"] or "—",
                    formato_pesos(movimiento["monto"]),
                ),
            )
        if self.resumen["movimientos"]:
            self.lbl_sin_movimientos.pack_forget()
        else:
            self.lbl_sin_movimientos.pack(anchor="w", pady=(7, 0))
        self._actualizar_diferencia()

    def abrir_formulario_egreso(self):
        # Abro una ventana aparte para registrar los gastos de caja menor.
        ventana = tk.Toplevel(self.winfo_toplevel())
        ventana.title("Registrar gasto de caja menor")
        ventana.configure(bg=FONDO)
        ventana.transient(self.winfo_toplevel())
        ventana.grab_set()
        ventana.resizable(False, False)
        ventana.geometry("430x360")

        formulario = tk.Frame(ventana, bg=FONDO, padx=24, pady=20)
        formulario.pack(fill="both", expand=True)
        crear_etiqueta(
            formulario, "Registrar gasto",
            bg=FONDO, tamano=16, negrita=True,
        ).pack(anchor="w", pady=(0, 14))
        crear_etiqueta(
            formulario, "Categoría", bg=FONDO,
            color=TEXTO_SUAVE, tamano=9,
        ).pack(anchor="w", pady=(5, 4))
        categoria = ttk.Combobox(
            formulario,
            values=("Transporte", "Insumos", "Servicios", "Mantenimiento", "Otros"),
            style="POS.TCombobox",
            font=("Segoe UI", 10),
        )
        categoria.pack(fill="x", ipady=5)

        crear_etiqueta(
            formulario, "Monto (COP)", bg=FONDO,
            color=TEXTO_SUAVE, tamano=9,
        ).pack(anchor="w", pady=(12, 4))
        monto = tk.Entry(
            formulario,
            bg=PANEL_SECUNDARIO,
            fg=TEXTO,
            insertbackground=ACENTO,
            relief="flat",
            font=("Segoe UI", 10),
        )
        monto.pack(fill="x", ipady=7)

        crear_etiqueta(
            formulario, "Descripción", bg=FONDO,
            color=TEXTO_SUAVE, tamano=9,
        ).pack(anchor="w", pady=(12, 4))
        descripcion = tk.Entry(
            formulario,
            bg=PANEL_SECUNDARIO,
            fg=TEXTO,
            insertbackground=ACENTO,
            relief="flat",
            font=("Segoe UI", 10),
        )
        descripcion.pack(fill="x", ipady=7)

        def guardar():
            # Si los datos o la base de datos fallan, aviso y dejo el formulario abierto.
            try:
                valor = self._leer_monto(monto)
                self.modelo.registrar_egreso(
                    categoria.get(),
                    valor,
                    descripcion.get(),
                    self.usuario_actual.get("id"),
                )
            except ValueError as error:
                messagebox.showerror(
                    "Revisa los datos", str(error), parent=ventana
                )
                return
            except sqlite3.Error as error:
                messagebox.showerror(
                    "No se pudo registrar el gasto",
                    f"El gasto no fue guardado. Detalle: {error}",
                    parent=ventana,
                )
                return

            ventana.destroy()
            self.actualizar_reporte()
            if self.al_cambiar:
                self.al_cambiar()

        acciones = tk.Frame(formulario, bg=FONDO)
        acciones.pack(fill="x", pady=(18, 0))
        crear_boton(acciones, "Cancelar", ventana.destroy).pack(side="right")
        crear_boton(
            acciones, "Guardar gasto", guardar, principal=True
        ).pack(side="right", padx=(0, 8))
        ventana.bind("<Return>", lambda event: guardar())
        categoria.focus_set()

    def _leer_monto(self, entrada):
        # Acepto montos escritos con símbolo de pesos o separadores comunes.
        texto = entrada.get().strip()
        if not texto:
            return 0
        return float(
            texto.replace("$", "").replace(".", "").replace(",", "")
        )

    def _actualizar_diferencia(self, _event=None):
        # Recalculo el arqueo cada vez que cambia uno de los valores contados.
        try:
            contado_costos = self._leer_monto(self.entry_contado_costos)
            contado_ganancias = self._leer_monto(
                self.entry_contado_ganancias
            )
            if min(
                contado_costos,
                contado_ganancias,
            ) < 0:
                raise ValueError
        except ValueError:
            self.lbl_diferencia.config(
                text="Diferencia: valor inválido", fg="#E05C63"
            )
            return

        # Comparo lo contado con el saldo inicial más el movimiento del día.
        esperado_costos = (
            self.saldos_iniciales["costos"]
            + self.resumen["reserva_reposicion"]
        )
        esperado_ganancias = (
            self.saldos_iniciales["ganancias"]
            + self.resumen["ganancia_disponible"]
        )
        diferencia_costos = contado_costos - esperado_costos
        diferencia_ganancias = contado_ganancias - esperado_ganancias
        self.lbl_movimiento_costos.config(
            text=formato_pesos(self.resumen["reserva_reposicion"])
        )
        self.lbl_movimiento_ganancias.config(
            text=formato_pesos(self.resumen["ganancia_disponible"])
        )
        self.lbl_esperado_costos.config(
            text=formato_pesos(esperado_costos)
        )
        self.lbl_esperado_ganancias.config(
            text=formato_pesos(esperado_ganancias)
        )
        self.lbl_diferencia_costos.config(
            text=f"Diferencia: {formato_pesos(diferencia_costos)}",
            fg=ACENTO if abs(diferencia_costos) < 0.01 else "#E6AD55",
        )
        self.lbl_diferencia_ganancias.config(
            text=f"Diferencia: {formato_pesos(diferencia_ganancias)}",
            fg=ACENTO if abs(diferencia_ganancias) < 0.01 else "#E6AD55",
        )
        diferencia_total = diferencia_costos + diferencia_ganancias
        self.lbl_diferencia.config(
            text=f"Diferencia total: {formato_pesos(diferencia_total)}",
            fg=ACENTO if abs(diferencia_total) < 0.01 else "#E6AD55",
        )

    def efectuar_cierre(self):
        # Valido los conteos antes de pedir confirmación y guardarlos.
        try:
            contado_costos = self._leer_monto(self.entry_contado_costos)
            contado_ganancias = self._leer_monto(
                self.entry_contado_ganancias
            )
            if min(
                contado_costos,
                contado_ganancias,
            ) < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror(
                "Valores inválidos",
                "Los conteos deben ser montos válidos y no negativos.",
                parent=self.winfo_toplevel(),
            )
            return

        esperado_costos = (
            self.saldos_iniciales["costos"]
            + self.resumen["reserva_reposicion"]
        )
        esperado_ganancias = (
            self.saldos_iniciales["ganancias"]
            + self.resumen["ganancia_disponible"]
        )
        diferencia_costos = contado_costos - esperado_costos
        diferencia_ganancias = contado_ganancias - esperado_ganancias
        confirmar = messagebox.askyesno(
            "Confirmar cierre",
            "¿Deseas guardar el cierre de ambos fondos?\n\n"
            f"Reserva para reponer: "
            f"{formato_pesos(self.resumen['reserva_reposicion'])}\n"
            f"Ganancia disponible: "
            f"{formato_pesos(self.resumen['ganancia_disponible'])}\n\n"
            f"Costos — esperado: {formato_pesos(esperado_costos)}, "
            f"contado: {formato_pesos(contado_costos)}, "
            f"diferencia: {formato_pesos(diferencia_costos)}\n"
            f"Ganancias — esperado: {formato_pesos(esperado_ganancias)}, "
            f"contado: {formato_pesos(contado_ganancias)}, "
            f"diferencia: {formato_pesos(diferencia_ganancias)}",
            parent=self.winfo_toplevel(),
        )
        if not confirmar:
            return

        # El cierre guarda lo contado como base para el siguiente arqueo.
        try:
            (
                cierre_id,
                esperado_costos,
                esperado_ganancias,
                diferencia_costos,
                diferencia_ganancias,
            ) = self.modelo.cerrar_caja(
                self.fecha,
                self.saldos_iniciales["costos"],
                self.saldos_iniciales["ganancias"],
                contado_costos,
                contado_ganancias,
                self.usuario_actual.get("id"),
            )
        except sqlite3.Error as error:
            messagebox.showerror(
                "No se pudo guardar el cierre",
                f"El cierre no fue registrado. Detalle: {error}",
                parent=self.winfo_toplevel(),
            )
            return

        messagebox.showinfo(
            "Cierre guardado",
            f"Cierre #{cierre_id} registrado.\n\n"
            f"Costos esperados: {formato_pesos(esperado_costos)}\n"
            f"Diferencia de costos: {formato_pesos(diferencia_costos)}\n\n"
            f"Ganancias esperadas: {formato_pesos(esperado_ganancias)}\n"
            f"Diferencia de ganancias: {formato_pesos(diferencia_ganancias)}",
            parent=self.winfo_toplevel(),
        )
        if self.al_cambiar:
            self.al_cambiar()

    def exportar_reporte(self):
        # Pido dónde guardar el PDF y luego lo genero con los datos actuales.
        ruta = filedialog.asksaveasfilename(
            parent=self.winfo_toplevel(),
            title="Exportar reporte del día",
            defaultextension=".pdf",
            filetypes=(("Documento PDF", "*.pdf"),),
            initialfile=f"cierre_caja_{self.fecha}.pdf",
        )
        if not ruta:
            return
        try:
            contado_costos = self._leer_monto(self.entry_contado_costos)
            contado_ganancias = self._leer_monto(
                self.entry_contado_ganancias
            )
            if min(
                contado_costos,
                contado_ganancias,
            ) < 0:
                raise ValueError(
                    "Los conteos no pueden ser negativos."
                )
            exportar_cierre_pdf(
                ruta,
                self.resumen,
                self.saldos_iniciales["costos"],
                self.saldos_iniciales["ganancias"],
                contado_costos,
                contado_ganancias,
            )
        except (OSError, ValueError) as error:
            messagebox.showerror(
                "Error al exportar", str(error), parent=self.winfo_toplevel()
            )
            return
        messagebox.showinfo(
            "Reporte PDF exportado",
            f"El archivo se guardó en:\n{ruta}",
            parent=self.winfo_toplevel(),
        )
