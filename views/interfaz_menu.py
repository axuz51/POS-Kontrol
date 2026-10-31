import tkinter as tk

from views.interfaz_inventario import VentanaInventario
from views.interfaz_pos import VentanaPOS
from views.interfaz_reportes import VentanaReportes
from views.tema import (
    ACENTO,
    ACENTO_OSCURO,
    BORDE,
    FONDO,
    PANEL_SECUNDARIO,
    TEXTO,
    TEXTO_SUAVE,
    configurar_estilos,
)


class VentanaMenuPrincipal:
    # Relaciono cada sección con el nombre que aparece en el encabezado.
    PAGINAS = {
        "pos": ("Punto de venta", "POS"),
        "inventario": ("Gestión de Inventario", "INVENTARIO"),
        "reportes": ("Cierre de Caja y Reportes", "REPORTES"),
    }

    def __init__(self, root, usuario_actual):
        # Preparo la ventana y muestro el punto de venta al iniciar.
        self.root = root
        self.usuario_actual = usuario_actual
        self.pagina_actual = "pos"
        self.root.title("POS-Kontrol")
        self.root.geometry("1440x880")
        self.root.minsize(1100, 700)
        self.root.configure(bg=FONDO)
        configurar_estilos(self.root)
        self.root.protocol("WM_DELETE_WINDOW", self.root.destroy)

        self._crear_barra_superior()
        self._crear_contenido()
        self.mostrar_pagina("pos")

    def _crear_barra_superior(self):
        # La barra muestra el nombre del sistema, el usuario y la opción de salir.
        barra = tk.Frame(
            self.root,
            bg="#17191B",
            height=64,
            highlightbackground=BORDE,
            highlightthickness=1,
        )
        barra.pack(fill="x")
        barra.pack_propagate(False)

        marca = tk.Frame(barra, bg="#17191B")
        marca.pack(side="left", padx=24)
        tk.Label(
            marca,
            text="▣",
            bg=ACENTO_OSCURO,
            fg=ACENTO,
            font=("Segoe UI", 15, "bold"),
            padx=8,
            pady=4,
        ).pack(side="left", padx=(0, 9))
        tk.Label(
            marca,
            text="POS-Kontrol",
            bg="#17191B",
            fg=TEXTO,
            font=("Segoe UI", 14, "bold"),
        ).pack(side="left")

        tk.Frame(barra, bg=BORDE, width=1).pack(
            side="left", fill="y", pady=13, padx=4
        )
        tk.Label(
            barra,
            text="▣  La Cumbre  /  Sede principal",
            bg="#17191B",
            fg=TEXTO_SUAVE,
            font=("Segoe UI", 9),
        ).pack(side="left", padx=17)

        btn_salir = tk.Button(
            barra,
            text="Salir",
            command=self.root.destroy,
            bg=PANEL_SECUNDARIO,
            fg=TEXTO,
            activebackground=BORDE,
            activeforeground=TEXTO,
            relief="flat",
            cursor="hand2",
            padx=14,
            pady=7,
            font=("Segoe UI", 9),
        )
        btn_salir.pack(side="right", padx=20)

        nombre = self.usuario_actual.get("nombre", "Usuario")
        rol = self.usuario_actual.get("rol", "Cajero")
        tk.Label(
            barra,
            text=f"{nombre}  ·  {rol}",
            bg="#17191B",
            fg=TEXTO,
            font=("Segoe UI", 9, "bold"),
        ).pack(side="right", padx=15)
        tk.Label(
            barra,
            text="●  Sincronizado",
            bg="#17191B",
            fg=ACENTO,
            font=("Segoe UI", 8),
        ).pack(side="right", padx=15)

    def _crear_contenido(self):
        # Armo la navegación lateral, el espacio de cada página y el estado.
        cuerpo = tk.Frame(self.root, bg=FONDO)
        cuerpo.pack(fill="both", expand=True)

        self.sidebar = tk.Frame(
            cuerpo,
            bg="#17191B",
            width=205,
            highlightbackground=BORDE,
            highlightthickness=1,
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        tk.Label(
            self.sidebar,
            text="OPERACIÓN",
            bg="#17191B",
            fg="#6F777B",
            font=("Segoe UI", 8, "bold"),
        ).pack(anchor="w", padx=18, pady=(23, 10))

        self.botones_nav = {}
        for clave, etiqueta in (
            ("pos", "▣   Punto de venta"),
            ("inventario", "▤   Inventario"),
            ("reportes", "▥   Cierre y reportes"),
        ):
            boton = tk.Button(
                self.sidebar,
                text=etiqueta,
                command=lambda pagina=clave: self.mostrar_pagina(pagina),
                anchor="w",
                bg="#17191B",
                fg=TEXTO_SUAVE,
                activebackground=ACENTO_OSCURO,
                activeforeground=ACENTO,
                relief="flat",
                bd=0,
                cursor="hand2",
                padx=14,
                pady=11,
                font=("Segoe UI", 9, "bold"),
            )
            boton.pack(fill="x", padx=10, pady=2)
            self.botones_nav[clave] = boton

        tk.Frame(self.sidebar, bg=BORDE, height=1).pack(
            fill="x", padx=16, pady=17
        )
        tk.Label(
            self.sidebar,
            text="SEDE ACTIVA",
            bg="#17191B",
            fg="#6F777B",
            font=("Segoe UI", 8, "bold"),
        ).pack(anchor="w", padx=18, pady=(0, 6))
        tk.Label(
            self.sidebar,
            text="La Cumbre\nBogotá, Colombia",
            bg="#17191B",
            fg=TEXTO_SUAVE,
            justify="left",
            font=("Segoe UI", 8),
        ).pack(anchor="w", padx=18)

        area = tk.Frame(cuerpo, bg=FONDO)
        area.pack(side="left", fill="both", expand=True)
        self.titulo_pagina = tk.Label(
            area,
            text="",
            bg=FONDO,
            fg=TEXTO,
            font=("Segoe UI", 13, "bold"),
        )
        self.titulo_pagina.pack(anchor="w", padx=22, pady=(13, 0))
        self.area_pagina = tk.Frame(area, bg=FONDO)
        self.area_pagina.pack(fill="both", expand=True, padx=22, pady=14)

        self.barra_estado = tk.Frame(self.root, bg="#17191B", height=27)
        self.barra_estado.pack(fill="x", side="bottom")
        self.barra_estado.pack_propagate(False)
        tk.Label(
            self.barra_estado,
            text="●  Todos los sistemas en línea     TERMINAL 01",
            bg="#17191B",
            fg=ACENTO,
            font=("Segoe UI", 8),
        ).pack(side="left", padx=17, pady=5)
        tk.Label(
            self.barra_estado,
            text="Valores en pesos colombianos (COP)",
            bg="#17191B",
            fg=TEXTO_SUAVE,
            font=("Segoe UI", 8),
        ).pack(side="right", padx=17, pady=5)

    def mostrar_pagina(self, pagina):
        # Cambio el resaltado y cargo la vista que corresponde a la sección.
        self.pagina_actual = pagina
        _, titulo = self.PAGINAS[pagina]
        self.titulo_pagina.config(text=titulo)
        for clave, boton in self.botones_nav.items():
            seleccionado = clave == pagina
            boton.config(
                bg=ACENTO_OSCURO if seleccionado else "#17191B",
                fg=ACENTO if seleccionado else TEXTO_SUAVE,
            )

        for widget in self.area_pagina.winfo_children():
            widget.destroy()

        if pagina == "pos":
            vista = VentanaPOS(
                self.area_pagina,
                usuario_actual=self.usuario_actual,
                al_guardar=self._refrescar_si_es_necesario,
            )
        elif pagina == "inventario":
            vista = VentanaInventario(
                self.area_pagina,
                al_cambiar=self._refrescar_si_es_necesario,
            )
        else:
            vista = VentanaReportes(
                self.area_pagina,
                usuario_actual=self.usuario_actual,
                al_cambiar=self._refrescar_si_es_necesario,
            )
        vista.pack(fill="both", expand=True)

    def _refrescar_si_es_necesario(self):
        # Actualizo la pantalla activa después de guardar un cambio.
        if self.pagina_actual == "reportes":
            for vista in self.area_pagina.winfo_children():
                actualizar = getattr(vista, "actualizar_reporte", None)
                if actualizar:
                    actualizar()
        elif self.pagina_actual == "inventario":
            for vista in self.area_pagina.winfo_children():
                actualizar = getattr(vista, "actualizar_tabla", None)
                if actualizar:
                    actualizar()
