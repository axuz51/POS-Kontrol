import tkinter as tk
from tkinter import ttk


# Mantengo los colores en un solo lugar para que todas las pantallas coincidan.
FONDO = "#111315"
PANEL = "#1D1F21"
PANEL_SECUNDARIO = "#242729"
BORDE = "#303436"
TEXTO = "#E8E9EA"
TEXTO_SUAVE = "#92999D"
ACENTO = "#00D6BE"
ACENTO_OSCURO = "#103C38"
ROJO = "#E05C63"


def configurar_estilos(raiz):
    # Defino cómo se ven las tablas, pestañas y listas desplegables.
    estilo = ttk.Style(raiz)
    estilo.theme_use("clam")
    estilo.configure(
        "POS.Treeview",
        background=PANEL,
        foreground=TEXTO,
        fieldbackground=PANEL,
        borderwidth=0,
        rowheight=36,
        font=("Segoe UI", 9),
    )
    estilo.configure(
        "POS.Treeview.Heading",
        background=PANEL_SECUNDARIO,
        foreground=TEXTO_SUAVE,
        relief="flat",
        font=("Segoe UI", 8, "bold"),
    )
    estilo.map(
        "POS.Treeview",
        background=[("selected", ACENTO_OSCURO)],
        foreground=[("selected", TEXTO)],
    )
    estilo.configure(
        "POS.TCombobox",
        fieldbackground=PANEL,
        background=PANEL_SECUNDARIO,
        foreground=TEXTO,
        arrowcolor=ACENTO,
    )
    estilo.map(
        "POS.TCombobox",
        fieldbackground=[("readonly", PANEL)],
        foreground=[("readonly", TEXTO)],
        selectbackground=[("readonly", PANEL)],
        selectforeground=[("readonly", TEXTO)],
    )
    estilo.configure(
        "POS.TNotebook",
        background=FONDO,
        borderwidth=0,
        tabmargins=(0, 0, 0, 0),
    )
    estilo.configure(
        "POS.TNotebook.Tab",
        background=PANEL_SECUNDARIO,
        foreground=TEXTO_SUAVE,
        padding=(14, 8),
        borderwidth=0,
    )
    estilo.map(
        "POS.TNotebook.Tab",
        background=[("selected", PANEL)],
        foreground=[("selected", ACENTO)],
    )
    return estilo


def crear_boton(parent, texto, comando, principal=False, compacto=False):
    # Uso el mismo formato de botón en las distintas pantallas.
    fondo = ACENTO if principal else PANEL_SECUNDARIO
    color = "#06201D" if principal else TEXTO
    boton = tk.Button(
        parent,
        text=texto,
        command=comando,
        bg=fondo,
        fg=color,
        activebackground=ACENTO if principal else BORDE,
        activeforeground=color,
        relief="flat",
        bd=0,
        cursor="hand2",
        font=("Segoe UI", 9, "bold"),
        padx=12 if compacto else 18,
        pady=7 if compacto else 10,
    )
    return boton


def crear_tarjeta(parent, **kwargs):
    # Creo un panel con el fondo y el borde que usa el tema.
    return tk.Frame(
        parent,
        bg=PANEL,
        highlightbackground=BORDE,
        highlightthickness=1,
        **kwargs,
    )


def crear_etiqueta(parent, texto, *, color=TEXTO, tamano=10, negrita=False, **kwargs):
    # Mantengo un estilo común para los textos de la interfaz.
    return tk.Label(
        parent,
        text=texto,
        bg=kwargs.pop("bg", PANEL),
        fg=color,
        font=("Segoe UI", tamano, "bold" if negrita else "normal"),
        **kwargs,
    )
