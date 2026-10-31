from datetime import datetime
from pathlib import Path

import reportlab
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# Registro las fuentes incluidas con ReportLab para que el PDF use el mismo estilo.
_FUENTES = Path(reportlab.__file__).parent / "fonts"
pdfmetrics.registerFont(TTFont("Vera", str(_FUENTES / "Vera.ttf")))
pdfmetrics.registerFont(TTFont("Vera-Bold", str(_FUENTES / "VeraBd.ttf")))
pdfmetrics.registerFont(TTFont("Vera-Oblique", str(_FUENTES / "VeraIt.ttf")))
pdfmetrics.registerFont(
    TTFont("Vera-BoldOblique", str(_FUENTES / "VeraBI.ttf"))
)
pdfmetrics.registerFontFamily(
    "Vera",
    normal="Vera",
    bold="Vera-Bold",
    italic="Vera-Oblique",
    boldItalic="Vera-BoldOblique",
)


# Uso la misma paleta en las tablas y encabezados de los reportes.
_FONDO = colors.HexColor("#111315")
_PANEL = colors.HexColor("#202325")
_PANEL_ALTERNO = colors.HexColor("#292D30")
_TEXTO = colors.HexColor("#E8E9EA")
_SUAVE = colors.HexColor("#9AA1A5")
_ACENTO = colors.HexColor("#00D6BE")
_BORDE = colors.HexColor("#3A3F42")
_ROJO = colors.HexColor("#E05C63")
_FONDO_COSTOS = colors.HexColor("#17433D")
_FONDO_GANANCIAS = colors.HexColor("#4A3920")


def _pesos(valor):
    # Mantengo el formato de moneda igual al de las pantallas.
    return f"$ {valor:,.0f}".replace(",", ".")


def _estilos():
    # Centralizo los estilos de texto para los distintos reportes.
    base = getSampleStyleSheet()
    return {
        "titulo": ParagraphStyle(
            "ReporteTitulo",
            parent=base["Title"],
            fontName="Vera-Bold",
            fontSize=20,
            leading=24,
            textColor=_TEXTO,
            alignment=TA_LEFT,
            spaceAfter=2,
        ),
        "subtitulo": ParagraphStyle(
            "ReporteSubtitulo",
            parent=base["Normal"],
            fontName="Vera",
            fontSize=9,
            leading=13,
            textColor=_SUAVE,
        ),
        "seccion": ParagraphStyle(
            "ReporteSeccion",
            parent=base["Heading2"],
            fontName="Vera-Bold",
            fontSize=11,
            leading=14,
            textColor=_TEXTO,
            spaceBefore=12,
            spaceAfter=7,
        ),
        "kpi_titulo": ParagraphStyle(
            "ReporteKpiTitulo",
            parent=base["Normal"],
            fontName="Vera",
            fontSize=8,
            leading=11,
            textColor=_SUAVE,
        ),
        "kpi_valor": ParagraphStyle(
            "ReporteKpiValor",
            parent=base["Normal"],
            fontName="Vera-Bold",
            fontSize=15,
            leading=19,
            textColor=_TEXTO,
        ),
        "celda": ParagraphStyle(
            "ReporteCelda",
            parent=base["Normal"],
            fontName="Vera",
            fontSize=7.5,
            leading=10,
            textColor=_TEXTO,
        ),
        "celda_suave": ParagraphStyle(
            "ReporteCeldaSuave",
            parent=base["Normal"],
            fontName="Vera",
            fontSize=7.5,
            leading=10,
            textColor=_SUAVE,
        ),
        "fondo_costos": ParagraphStyle(
            "ReporteFondoCostos",
            parent=base["Normal"],
            fontName="Vera-Bold",
            fontSize=9,
            leading=12,
            textColor=_TEXTO,
        ),
        "fondo_ganancias": ParagraphStyle(
            "ReporteFondoGanancias",
            parent=base["Normal"],
            fontName="Vera-Bold",
            fontSize=9,
            leading=12,
            textColor=_TEXTO,
        ),
        "vacio": ParagraphStyle(
            "ReporteVacio",
            parent=base["Normal"],
            fontName="Vera-Oblique",
            fontSize=9,
            leading=13,
            textColor=_SUAVE,
        ),
        "derecha": ParagraphStyle(
            "ReporteDerecha",
            parent=base["Normal"],
            fontName="Vera",
            fontSize=7.5,
            leading=10,
            textColor=_TEXTO,
            alignment=TA_RIGHT,
        ),
    }


def _parrafo(texto, estilo):
    # Escapo los caracteres para que los datos no se interpreten como etiquetas.
    seguro = str(texto).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return Paragraph(seguro, estilo)


def _encabezado_pagina(canvas, documento):
    # Dibujo el fondo, la línea inferior y el número en cada página.
    canvas.saveState()
    ancho, alto = documento.pagesize
    canvas.setFillColor(_FONDO)
    canvas.rect(0, 0, ancho, alto, fill=1, stroke=0)
    canvas.setFillColor(_ACENTO)
    canvas.rect(
        documento.leftMargin,
        alto - 13 * mm,
        26 * mm,
        1.3 * mm,
        fill=1,
        stroke=0,
    )
    canvas.setStrokeColor(_BORDE)
    canvas.setLineWidth(0.5)
    canvas.line(
        documento.leftMargin,
        14 * mm,
        ancho - documento.rightMargin,
        14 * mm,
    )
    canvas.setFont("Vera", 7.5)
    canvas.setFillColor(_SUAVE)
    canvas.drawString(
        documento.leftMargin,
        9 * mm,
        "POS-Kontrol  |  Valores en pesos colombianos (COP)",
    )
    canvas.drawRightString(
        ancho - documento.rightMargin,
        9 * mm,
        f"Página {documento.page}",
    )
    canvas.restoreState()


def _crear_documento(ruta, paginas, nombre_archivo):
    # Configuro márgenes y metadatos comunes para los archivos PDF.
    margen_lateral = 15 * mm
    documento = SimpleDocTemplate(
        ruta,
        pagesize=paginas,
        rightMargin=margen_lateral,
        leftMargin=margen_lateral,
        topMargin=22 * mm,
        bottomMargin=20 * mm,
        title=nombre_archivo,
        author="POS-Kontrol",
        subject=nombre_archivo,
    )
    return documento


def _tabla_kpis(elementos, anchos):
    # Armo tarjetas con las cifras principales de cada reporte.
    estilos = _estilos()
    tarjetas = [
        Table(
            [
                [_parrafo(titulo, estilos["kpi_titulo"])],
                [_parrafo(valor, estilos["kpi_valor"])],
            ],
            colWidths=[ancho],
        )
        for (titulo, valor), ancho in zip(elementos, anchos)
    ]
    tabla = Table(
        [tarjetas],
        colWidths=anchos,
    )
    estilos = [
        ("BACKGROUND", (0, 0), (-1, -1), _PANEL),
        ("BOX", (0, 0), (-1, -1), 0.6, _BORDE),
        ("INNERGRID", (0, 0), (-1, -1), 0.6, _BORDE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
    ]
    for columna in range(len(elementos)):
        estilos.append(("LINEBEFORE", (columna, 0), (columna, 0), 2, _ACENTO))
    tabla.setStyle(TableStyle(estilos))
    return tabla


def _tabla_datos(filas, anchos, alineadas_derecha=()):
    # Aplico el formato de tabla y alineo a la derecha las columnas numéricas.
    tabla = Table(filas, colWidths=anchos, repeatRows=1, hAlign="LEFT")
    estilos = [
        ("BACKGROUND", (0, 0), (-1, 0), _PANEL_ALTERNO),
        ("TEXTCOLOR", (0, 0), (-1, 0), _ACENTO),
        ("FONTNAME", (0, 0), (-1, 0), "Vera-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 7),
        ("LEADING", (0, 0), (-1, 0), 9),
        ("BACKGROUND", (0, 1), (-1, -1), _PANEL),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [_PANEL, _PANEL_ALTERNO]),
        ("LINEBELOW", (0, 0), (-1, 0), 0.7, _ACENTO),
        ("LINEBELOW", (0, 1), (-1, -1), 0.25, _BORDE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]
    for columna in alineadas_derecha:
        estilos.append(("ALIGN", (columna, 0), (columna, -1), "RIGHT"))
    tabla.setStyle(TableStyle(estilos))
    return tabla


def exportar_inventario_pdf(ruta, productos, generado=None):
    # Preparo el resumen y el detalle del catálogo que voy a exportar.
    estilos = _estilos()
    productos = list(productos)
    activos = [producto for producto in productos if producto["activo"]]
    alertas = [
        producto for producto in activos
        if producto["stock"] <= producto["stock_minimo"]
    ]
    valor_costo = sum(
        producto["stock"] * producto["precio_compra"] for producto in activos
    )
    valor_venta = sum(
        producto["stock"] * producto["precio_venta"] for producto in activos
    )
    generado = generado or datetime.now().strftime("%d/%m/%Y %H:%M")

    documento = _crear_documento(
        ruta,
        landscape(A4),
        f"Catálogo de inventario - {generado}",
    )
    contenido = [
        _parrafo("Catálogo de inventario", estilos["titulo"]),
        _parrafo(
            f"Existencias, precios y estado de los accesorios  |  "
            f"Generado el {generado}",
            estilos["subtitulo"],
        ),
        Spacer(1, 8 * mm),
    ]

    ancho_util = landscape(A4)[0] - 30 * mm
    anchos_kpi = [ancho_util / 4] * 4
    contenido.append(
        _tabla_kpis(
            [
                ("REFERENCIAS ACTIVAS", str(len(activos))),
                ("STOCK BAJO", str(len(alertas))),
                ("VALOR AL COSTO", _pesos(valor_costo)),
                ("VALOR A PRECIO DE VENTA", _pesos(valor_venta)),
            ],
            anchos_kpi,
        )
    )
    contenido.append(
        _parrafo("Detalle de accesorios", estilos["seccion"])
    )

    if productos:
        # Incluyo el estado y los precios de cada producto del catálogo.
        encabezados = [
            "SKU / CÓDIGO",
            "NOMBRE DEL ACCESORIO",
            "CATEGORÍA",
            "EXISTENCIAS",
            "STOCK MÍNIMO",
            "PRECIO DE COSTO",
            "PRECIO DE VENTA",
            "ESTADO",
        ]
        filas = [[_parrafo(valor, estilos["celda"]) for valor in encabezados]]
        for producto in productos:
            activo = bool(producto["activo"])
            bajo = producto["stock"] <= producto["stock_minimo"]
            estado = (
                "Inactivo" if not activo else ("Stock bajo" if bajo else "En stock")
            )
            filas.append(
                [
                    _parrafo(f"PRD-{producto['id']:04d}", estilos["celda_suave"]),
                    _parrafo(producto["nombre"], estilos["celda"]),
                    _parrafo(producto["categoria"], estilos["celda_suave"]),
                    _parrafo(str(producto["stock"]), estilos["derecha"]),
                    _parrafo(str(producto["stock_minimo"]), estilos["derecha"]),
                    _parrafo(_pesos(producto["precio_compra"]), estilos["derecha"]),
                    _parrafo(_pesos(producto["precio_venta"]), estilos["derecha"]),
                    _parrafo(estado, estilos["celda"]),
                ]
            )
        anchos = [24, 57, 34, 24, 25, 38, 38, 27]
        escala = ancho_util / sum(anchos)
        contenido.append(
            _tabla_datos(
                filas,
                [ancho * escala * mm for ancho in anchos],
                alineadas_derecha=(3, 4, 5, 6),
            )
        )
    else:
        contenido.append(
            _parrafo("No hay accesorios para mostrar.", estilos["vacio"])
        )

    documento.build(
        contenido,
        onFirstPage=_encabezado_pagina,
        onLaterPages=_encabezado_pagina,
    )


def exportar_cierre_pdf(
    ruta,
    resumen,
    saldo_inicial_costos,
    saldo_inicial_ganancias,
    efectivo_contado_costos,
    efectivo_contado_ganancias,
    generado=None,
):
    # Calculo los valores del arqueo antes de armar las páginas del cierre.
    efectivo_esperado_costos = (
        saldo_inicial_costos + resumen["reserva_reposicion"]
    )
    efectivo_esperado_ganancias = (
        saldo_inicial_ganancias + resumen["ganancia_disponible"]
    )
    diferencia_costos = efectivo_contado_costos - efectivo_esperado_costos
    diferencia_ganancias = (
        efectivo_contado_ganancias - efectivo_esperado_ganancias
    )
    estilos = _estilos()
    generado = generado or datetime.now().strftime("%d/%m/%Y %H:%M")
    documento = _crear_documento(
        ruta,
        A4,
        f"Cierre de caja - {resumen['fecha']}",
    )
    contenido = [
        _parrafo("Cierre de caja y reportes", estilos["titulo"]),
        _parrafo(
            f"Resumen de la jornada del {resumen['fecha']}  |  "
            f"Generado el {generado}",
            estilos["subtitulo"],
        ),
        Spacer(1, 7 * mm),
    ]

    ancho_util = A4[0] - 30 * mm
    contenido.append(
        _tabla_kpis(
            [
                ("VENTAS REGISTRADAS", str(resumen["cantidad"])),
                ("TOTAL VENDIDO", _pesos(resumen["total"])),
            ],
            [ancho_util / 2, ancho_util / 2],
        )
    )
    contenido.append(Spacer(1, 4 * mm))
    contenido.append(
        _tabla_kpis(
            [
                ("EFECTIVO", _pesos(resumen["efectivo"])),
                ("QR", _pesos(resumen["qr"])),
                ("DATÁFONO BOLD", _pesos(resumen["bold"])),
            ],
            [ancho_util / 3] * 3,
        )
    )
    inicio_resumen = len(contenido)
    contenido.append(
        _parrafo("Resumen de ventas", estilos["seccion"])
    )
    resumen_filas = [
        ["Concepto", "Valor"],
        ["Costo de mercancía", _pesos(resumen["costos"])],
        ["Total vendido en el mes", _pesos(resumen["total_mes"])],
        ["Ganancia bruta", _pesos(resumen["ganancia"])],
        ["Egresos de caja menor", _pesos(resumen["egresos"])],
        [
            "Ganancia neta estimada",
            _pesos(resumen["ganancia"] - resumen["egresos"]),
        ],
    ]
    resumen_tabla = Table(
        [
            [
                _parrafo(fila[0], estilos["celda"]),
                _parrafo(fila[1], estilos["derecha"]),
            ]
            for fila in resumen_filas
        ],
        colWidths=[ancho_util * 0.62, ancho_util * 0.38],
        hAlign="LEFT",
    )
    resumen_tabla.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), _PANEL_ALTERNO),
                ("BACKGROUND", (0, 1), (-1, -1), _PANEL),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [_PANEL, _PANEL_ALTERNO]),
                ("TEXTCOLOR", (0, 0), (-1, 0), _ACENTO),
                ("FONTNAME", (0, 0), (-1, 0), "Vera-Bold"),
                ("LINEBELOW", (0, 0), (-1, 0), 0.7, _ACENTO),
                ("LINEBELOW", (0, 1), (-1, -1), 0.25, _BORDE),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    contenido.append(resumen_tabla)

    # Comparo los saldos iniciales con los movimientos y el efectivo contado.
    contenido.append(_parrafo("Arqueo de caja", estilos["seccion"]))
    arqueo_datos = [
        ("FONDO DE COSTOS", "", _ACENTO),
        ("Saldo inicial de costos", _pesos(saldo_inicial_costos), _TEXTO),
        (
            "Costo de productos vendidos",
            _pesos(resumen["reserva_reposicion"]),
            _TEXTO,
        ),
        (
            "Esperado en costos",
            _pesos(efectivo_esperado_costos),
            _ACENTO,
        ),
        (
            "Efectivo contado en costos",
            _pesos(efectivo_contado_costos),
            _TEXTO,
        ),
        (
            "Diferencia de costos",
            _pesos(diferencia_costos),
            _ACENTO if abs(diferencia_costos) < 0.01 else _ROJO,
        ),
        ("FONDO DE GANANCIAS", "", _ACENTO),
        (
            "Saldo inicial de ganancias",
            _pesos(saldo_inicial_ganancias),
            _TEXTO,
        ),
        (
            "Ganancia disponible después de gastos",
            _pesos(resumen["ganancia_disponible"]),
            _TEXTO,
        ),
        (
            "Esperado en ganancias",
            _pesos(efectivo_esperado_ganancias),
            _ACENTO,
        ),
        (
            "Efectivo contado en ganancias",
            _pesos(efectivo_contado_ganancias),
            _TEXTO,
        ),
        (
            "Diferencia de ganancias",
            _pesos(diferencia_ganancias),
            _ACENTO if abs(diferencia_ganancias) < 0.01 else _ROJO,
        ),
    ]
    arqueo = Table(
        [
            [
                _parrafo(
                    etiqueta,
                    estilos["fondo_costos"]
                    if indice == 0
                    else estilos["fondo_ganancias"]
                    if indice == 6
                    else estilos["celda_suave"],
                ),
                _parrafo(valor, estilos["derecha"]),
            ]
            for indice, (etiqueta, valor, _) in enumerate(arqueo_datos)
        ],
        colWidths=[ancho_util * 0.62, ancho_util * 0.38],
        hAlign="LEFT",
    )
    arqueo.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), _PANEL),
                ("ROWBACKGROUNDS", (0, 0), (-1, -1), [_PANEL, _PANEL_ALTERNO]),
                ("LINEBELOW", (0, 0), (-1, -1), 0.25, _BORDE),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("SPAN", (0, 0), (1, 0)),
                ("SPAN", (0, 6), (1, 6)),
                ("BACKGROUND", (0, 0), (-1, 0), _FONDO_COSTOS),
                ("BACKGROUND", (0, 6), (-1, 6), _FONDO_GANANCIAS),
                ("LINEBELOW", (0, 0), (-1, 0), 0.7, _ACENTO),
                ("LINEBELOW", (0, 6), (-1, 6), 0.7, colors.HexColor("#E6AD55")),
                ("TOPPADDING", (0, 0), (-1, 0), 8),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                ("TOPPADDING", (0, 6), (-1, 6), 8),
                ("BOTTOMPADDING", (0, 6), (-1, 6), 8),
            ]
        )
    )
    for indice, (_, _, color) in enumerate(arqueo_datos):
        if indice in (0, 6):
            continue
        arqueo.setStyle(
            TableStyle([("TEXTCOLOR", (1, indice), (1, indice), color)])
        )
    contenido.append(arqueo)
    fin_resumen = len(contenido)

    # Agrego el detalle de ventas y egresos de la jornada.
    contenido.append(
        _parrafo("Productos vendidos durante la jornada", estilos["seccion"])
    )
    productos_vendidos = list(resumen.get("productos_vendidos", ()))
    if productos_vendidos:
        filas_productos = [
            [
                _parrafo("CÓDIGO", estilos["celda"]),
                _parrafo("PRODUCTO", estilos["celda"]),
                _parrafo("UNIDADES", estilos["celda"]),
                _parrafo("TOTAL VENDIDO", estilos["celda"]),
                _parrafo("COSTO", estilos["celda"]),
                _parrafo("GANANCIA", estilos["celda"]),
            ]
        ]
        for producto in productos_vendidos:
            filas_productos.append(
                [
                    _parrafo(
                        f"PRD-{producto['producto_id']:04d}",
                        estilos["celda_suave"],
                    ),
                    _parrafo(producto["nombre"], estilos["celda"]),
                    _parrafo(str(producto["cantidad"]), estilos["derecha"]),
                    _parrafo(_pesos(producto["total"]), estilos["derecha"]),
                    _parrafo(_pesos(producto["costo"]), estilos["derecha"]),
                    _parrafo(_pesos(producto["ganancia"]), estilos["derecha"]),
                ]
            )
        contenido.append(
            _tabla_datos(
                filas_productos,
                [
                    ancho_util * 0.13,
                    ancho_util * 0.31,
                    ancho_util * 0.12,
                    ancho_util * 0.16,
                    ancho_util * 0.14,
                    ancho_util * 0.14,
                ],
                alineadas_derecha=(2, 3, 4, 5),
            )
        )
    else:
        contenido.append(
            _parrafo(
                "No se registraron productos vendidos durante esta jornada.",
                estilos["vacio"],
            )
        )

    contenido.append(
        _parrafo("Movimientos de caja menor", estilos["seccion"])
    )
    movimientos = list(resumen["movimientos"])
    if movimientos:
        filas = [
            [
                _parrafo("HORA", estilos["celda"]),
                _parrafo("CATEGORÍA", estilos["celda"]),
                _parrafo("DESCRIPCIÓN", estilos["celda"]),
                _parrafo("IMPORTE", estilos["celda"]),
            ]
        ]
        for movimiento in movimientos:
            filas.append(
                [
                    _parrafo(movimiento["fecha_hora"][11:16], estilos["celda_suave"]),
                    _parrafo(movimiento["categoria"], estilos["celda"]),
                    _parrafo(movimiento["descripcion"] or "—", estilos["celda"]),
                    _parrafo(_pesos(movimiento["monto"]), estilos["derecha"]),
                ]
            )
        contenido.append(
            _tabla_datos(
                filas,
                [
                    ancho_util * 0.14,
                    ancho_util * 0.23,
                    ancho_util * 0.41,
                    ancho_util * 0.22,
                ],
                alineadas_derecha=(3,),
            )
        )
    else:
        contenido.append(
            _parrafo(
                "No se registraron movimientos de caja menor en esta jornada.",
                estilos["vacio"],
            )
        )

    fin_detalles = len(contenido)
    contenido.append(
        _parrafo("Distribución de las ventas", estilos["seccion"])
    )
    ganancia_disponible = resumen.get(
        "ganancia_disponible",
        resumen["ganancia"] - resumen["egresos"],
    )
    distribucion_datos = [
        ["Fondo", "Cálculo", "Valor"],
        [
            "Reserva para reponer productos",
            "Costo de los productos vendidos",
            _pesos(resumen["reserva_reposicion"]),
        ],
        [
            "Ganancia bruta",
            "Ventas totales - costo",
            _pesos(resumen["ganancia"]),
        ],
        [
            "Gastos de caja menor",
            "Se restan de la ganancia",
            _pesos(resumen["egresos"]),
        ],
        [
            "Ganancia disponible",
            "Ganancia bruta - gastos",
            _pesos(ganancia_disponible),
        ],
    ]
    filas_distribucion = [
        [_parrafo(valor, estilos["celda"]) for valor in fila]
        for fila in distribucion_datos
    ]
    tabla_distribucion = Table(
        filas_distribucion,
        colWidths=[
            ancho_util * 0.38,
            ancho_util * 0.36,
            ancho_util * 0.26,
        ],
        hAlign="LEFT",
    )
    tabla_distribucion.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), _PANEL_ALTERNO),
                ("TEXTCOLOR", (0, 0), (-1, 0), _ACENTO),
                ("FONTNAME", (0, 0), (-1, 0), "Vera-Bold"),
                ("BACKGROUND", (0, 1), (-1, -1), _PANEL),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [_PANEL, _PANEL_ALTERNO]),
                ("LINEBELOW", (0, 0), (-1, 0), 0.7, _ACENTO),
                ("LINEBELOW", (0, 1), (-1, -1), 0.25, _BORDE),
                ("ALIGN", (2, 0), (2, -1), "RIGHT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("TEXTCOLOR", (0, -1), (-1, -1), _ACENTO),
                ("FONTNAME", (0, -1), (-1, -1), "Vera-Bold"),
            ]
        )
    )
    contenido.append(tabla_distribucion)
    contenido.append(
        _parrafo(
            "La separación se calcula sobre todas las ventas, incluidas las "
            "pagadas en efectivo, QR y Bold. Los gastos de caja menor se "
            "descuentan del fondo de ganancias; los saldos contados se "
            "trasladan como saldos iniciales al siguiente cierre.",
            estilos["subtitulo"],
        )
    )

    # Dejo el resumen de ventas y el arqueo al final del documento.
    contenido = (
        contenido[:inicio_resumen]
        + contenido[fin_resumen:fin_detalles]
        + contenido[fin_detalles:]
        + contenido[inicio_resumen:fin_resumen]
    )

    documento.build(
        contenido,
        onFirstPage=_encabezado_pagina,
        onLaterPages=_encabezado_pagina,
    )
