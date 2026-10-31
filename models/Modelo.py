import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime


class ModeloInventario:
    def __init__(self):
        # Uso la misma base de datos que inicializa la aplicación.
        self.db_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "Database",
            "pos_kontrol.db",
        )

    def conectar(self):
        # Activo el acceso por nombre de columna y las claves foráneas.
        conexion = sqlite3.connect(self.db_path)
        conexion.row_factory = sqlite3.Row
        conexion.execute("PRAGMA foreign_keys = ON")
        return conexion

    @contextmanager
    def _conexion(self):
        # Cierro la conexión siempre, incluso si una operación da error.
        conexion = self.conectar()
        try:
            with conexion:
                yield conexion
        finally:
            conexion.close()

    def obtener_categorias(self):
        # Devuelvo las categorías ordenadas para mostrarlas en los formularios.
        with self._conexion() as conexion:
            return conexion.execute(
                "SELECT id, nombre FROM categorias ORDER BY nombre"
            ).fetchall()

    def obtener_productos(self, termino="", categoria="Todas", estado="Todos"):
        # Aplico la búsqueda y los filtros directamente en la consulta.
        consulta = """
            SELECT p.id, p.nombre, p.categoria_id,
                   COALESCE(c.nombre, 'Sin categoría') AS categoria,
                   p.precio_compra, p.precio_venta, p.stock,
                   p.stock_minimo, p.activo
            FROM productos AS p
            LEFT JOIN categorias AS c ON c.id = p.categoria_id
            WHERE (? = '' OR p.nombre LIKE ? OR CAST(p.id AS TEXT) LIKE ?)
              AND (? = 'Todas' OR c.nombre = ?)
              AND (? = 'Todos'
                   OR (? = 'En stock' AND p.stock > p.stock_minimo)
                   OR (? = 'Stock bajo' AND p.stock <= p.stock_minimo)
                   OR (? = 'Inactivos' AND p.activo = 0))
            ORDER BY p.nombre
        """
        patron = f"%{termino.strip()}%"
        with self._conexion() as conexion:
            return conexion.execute(
                consulta,
                (
                    termino.strip(),
                    patron,
                    patron,
                    categoria,
                    categoria,
                    estado,
                    estado,
                    estado,
                    estado,
                ),
            ).fetchall()

    def buscar_productos(self, termino):
        # En el punto de venta solo busco productos disponibles en stock.
        return self.obtener_productos(termino=termino, estado="En stock")

    def agregar_producto(
        self,
        nombre,
        categoria_id,
        precio_compra,
        precio_venta,
        stock,
        stock_minimo,
    ):
        # Guardo el nuevo producto y devuelvo un mensaje que entiende la vista.
        try:
            with self._conexion() as conexion:
                conexion.execute(
                    """
                    INSERT INTO productos
                        (nombre, categoria_id, precio_compra, precio_venta,
                         stock, stock_minimo)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        nombre.strip(),
                        categoria_id,
                        precio_compra,
                        precio_venta,
                        stock,
                        stock_minimo,
                    ),
                )
            return True, "Accesorio agregado correctamente."
        except sqlite3.Error as error:
            return False, f"No se pudo guardar el accesorio: {error}"

    def actualizar_producto(
        self,
        producto_id,
        nombre,
        categoria_id,
        precio_compra,
        precio_venta,
        stock,
        stock_minimo,
        activo,
    ):
        # Actualizo los datos del producto seleccionado.
        try:
            with self._conexion() as conexion:
                conexion.execute(
                    """
                    UPDATE productos
                    SET nombre = ?, categoria_id = ?, precio_compra = ?,
                        precio_venta = ?, stock = ?, stock_minimo = ?,
                        activo = ?
                    WHERE id = ?
                    """,
                    (
                        nombre.strip(),
                        categoria_id,
                        precio_compra,
                        precio_venta,
                        stock,
                        stock_minimo,
                        activo,
                        producto_id,
                    ),
                )
            return True, "Accesorio actualizado correctamente."
        except sqlite3.Error as error:
            return False, f"No se pudo actualizar el accesorio: {error}"

    def cargar_datos_prueba(self):
        # Cargo ejemplos solo cuando la tabla todavía está vacía.
        categorias = ("Fundas", "Cables", "Cargadores", "Audio")
        with self._conexion() as conexion:
            for categoria_id, nombre in enumerate(categorias, start=1):
                conexion.execute(
                    "INSERT OR IGNORE INTO categorias (id, nombre) VALUES (?, ?)",
                    (categoria_id, nombre),
                )

            cantidad = conexion.execute(
                "SELECT COUNT(*) FROM productos"
            ).fetchone()[0]
            if cantidad:
                return

            productos_demo = [
                ("Estuche transparente iPhone 14", 1, 8900, 12900, 48, 5),
                ("Estuche rígido Samsung S23", 1, 10500, 16900, 36, 5),
                ("Cable USB-C a USB-C 1m", 2, 4200, 7900, 24, 5),
                ("Cargador USB-C 20W", 3, 9500, 14900, 60, 10),
                ("Audífonos inalámbricos TWS", 4, 18000, 29900, 18, 5),
            ]
            conexion.executemany(
                """
                INSERT INTO productos
                    (nombre, categoria_id, precio_compra, precio_venta,
                     stock, stock_minimo)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                productos_demo,
            )

    def registrar_venta(self, carrito, efectivo, qr, bold, usuario_id=None):
        # Valido la venta y guardo el cobro, sus detalles y el descuento de stock.
        if not carrito:
            raise ValueError("Agregue al menos un producto antes de cobrar.")

        with self._conexion() as conexion:
            total = 0
            productos = []
            for item in carrito:
                producto = conexion.execute(
                    """
                    SELECT id, precio_compra, precio_venta, stock, activo
                    FROM productos WHERE id = ?
                    """,
                    (item["id"],),
                ).fetchone()
                if producto is None or not producto["activo"]:
                    raise ValueError(
                        f"El producto {item['id']} ya no está disponible."
                    )
                cantidad = int(item["cantidad"])
                if cantidad < 1:
                    raise ValueError("La cantidad de un producto no es válida.")
                if producto["stock"] < cantidad:
                    raise ValueError(
                        f"Existencias insuficientes para el producto "
                        f"{item['id']}."
                    )
                total += producto["precio_venta"] * cantidad
                productos.append((producto, cantidad))

            if abs((efectivo + qr + bold) - total) > 0.01:
                raise ValueError(
                    "Los pagos deben coincidir con el total de la venta."
                )

            cursor = conexion.execute(
                """
                INSERT INTO ventas
                    (fecha_hora, total, monto_efectivo, monto_qr,
                     monto_bold, usuario_id)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    datetime.now().isoformat(timespec="seconds"),
                    total,
                    efectivo,
                    qr,
                    bold,
                    usuario_id,
                ),
            )
            venta_id = cursor.lastrowid

            for producto, cantidad in productos:
                conexion.execute(
                    """
                    INSERT INTO detalle_ventas
                        (venta_id, producto_id, cantidad,
                         precio_compra_unitario, precio_venta_unitario)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        venta_id,
                        producto["id"],
                        cantidad,
                        producto["precio_compra"],
                        producto["precio_venta"],
                    ),
                )
                conexion.execute(
                    "UPDATE productos SET stock = stock - ? WHERE id = ?",
                    (cantidad, producto["id"]),
                )

            return venta_id, total

    def obtener_reporte_dia(self, fecha=None):
        # Junto ventas, costos y gastos para armar el resumen de la fecha.
        fecha = fecha or datetime.now().date().isoformat()
        inicio_mes = f"{fecha[:7]}-01"
        with self._conexion() as conexion:
            ventas = conexion.execute(
                """
                SELECT COUNT(*) AS cantidad, COALESCE(SUM(total), 0) AS total,
                       COALESCE(SUM(monto_efectivo), 0) AS efectivo,
                       COALESCE(SUM(monto_qr), 0) AS qr,
                       COALESCE(SUM(monto_bold), 0) AS bold
                FROM ventas WHERE date(fecha_hora) = ? AND estado = 'COMPLETADA'
                """,
                (fecha,),
            ).fetchone()
            ventas_mes = conexion.execute(
                """
                SELECT COALESCE(SUM(total), 0) AS total
                FROM ventas
                WHERE date(fecha_hora) >= ?
                  AND date(fecha_hora) <= ?
                  AND estado = 'COMPLETADA'
                """,
                (inicio_mes, fecha),
            ).fetchone()["total"]
            costos = conexion.execute(
                """
                SELECT COALESCE(SUM(d.cantidad * d.precio_compra_unitario), 0)
                    AS total
                FROM detalle_ventas AS d
                JOIN ventas AS v ON v.id = d.venta_id
                WHERE date(v.fecha_hora) = ? AND v.estado = 'COMPLETADA'
                """,
                (fecha,),
            ).fetchone()["total"]
            egresos = conexion.execute(
                """
                SELECT COALESCE(SUM(monto), 0) AS total
                FROM egresos_caja_menor WHERE date(fecha_hora) = ?
                """,
                (fecha,),
            ).fetchone()["total"]
            movimientos = conexion.execute(
                """
                SELECT fecha_hora, categoria, descripcion, monto
                FROM egresos_caja_menor
                WHERE date(fecha_hora) = ?
                ORDER BY fecha_hora DESC
                """,
                (fecha,),
            ).fetchall()
            productos_vendidos = conexion.execute(
                """
                SELECT p.id AS producto_id, p.nombre,
                       SUM(d.cantidad) AS cantidad,
                       SUM(d.cantidad * d.precio_venta_unitario) AS total,
                       SUM(d.cantidad * d.precio_compra_unitario) AS costo,
                       SUM(d.cantidad * (
                           d.precio_venta_unitario - d.precio_compra_unitario
                       )) AS ganancia
                FROM detalle_ventas AS d
                JOIN ventas AS v ON v.id = d.venta_id
                JOIN productos AS p ON p.id = d.producto_id
                WHERE date(v.fecha_hora) = ? AND v.estado = 'COMPLETADA'
                GROUP BY p.id, p.nombre
                ORDER BY cantidad DESC, p.nombre
                """,
                (fecha,),
            ).fetchall()
            return {
                "fecha": fecha,
                "cantidad": ventas["cantidad"],
                "total": ventas["total"],
                "total_mes": ventas_mes,
                "efectivo": ventas["efectivo"],
                "qr": ventas["qr"],
                "bold": ventas["bold"],
                "costos": costos,
                "ganancia": ventas["total"] - costos,
                "egresos": egresos,
                "reserva_reposicion": costos,
                "ganancia_disponible": ventas["total"] - costos - egresos,
                "movimientos": movimientos,
                "productos_vendidos": productos_vendidos,
            }

    def registrar_egreso(self, categoria, monto, descripcion="", usuario_id=None):
        # Reviso los datos básicos antes de registrar un gasto.
        categoria = categoria.strip()
        descripcion = descripcion.strip()
        if not categoria:
            raise ValueError("Indica la categoría del gasto.")
        if monto <= 0:
            raise ValueError("El monto del gasto debe ser mayor que cero.")

        with self._conexion() as conexion:
            cursor = conexion.execute(
                """
                INSERT INTO egresos_caja_menor
                    (fecha_hora, monto, categoria, descripcion, usuario_id)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    datetime.now().isoformat(timespec="seconds"),
                    monto,
                    categoria,
                    descripcion or None,
                    usuario_id,
                ),
            )
            return cursor.lastrowid

    def obtener_saldos_iniciales(self, fecha):
        # Tomo como base el conteo del cierre anterior a la fecha consultada.
        with self._conexion() as conexion:
            cierre = conexion.execute(
                """
                SELECT efectivo_contado_costos, efectivo_contado_ganancias
                FROM cierres_caja
                WHERE date(fecha_cierre) < ?
                  AND efectivo_contado_costos IS NOT NULL
                  AND efectivo_contado_ganancias IS NOT NULL
                ORDER BY date(fecha_cierre) DESC, id DESC
                LIMIT 1
                """,
                (fecha,),
            ).fetchone()

        if cierre is None:
            return {
                "costos": 0,
                "ganancias": 0,
                "tiene_cierre_previo": False,
            }
        return {
            "costos": cierre["efectivo_contado_costos"],
            "ganancias": cierre["efectivo_contado_ganancias"],
            "tiene_cierre_previo": True,
        }

    def cerrar_caja(
        self,
        fecha,
        saldo_inicial_costos,
        saldo_inicial_ganancias,
        efectivo_contado_costos,
        efectivo_contado_ganancias,
        usuario_id=None,
    ):
        # Calculo lo esperado y la diferencia de cada fondo antes de guardarlo.
        resumen = self.obtener_reporte_dia(fecha)
        efectivo_esperado_costos = (
            saldo_inicial_costos + resumen["reserva_reposicion"]
        )
        efectivo_esperado_ganancias = (
            saldo_inicial_ganancias + resumen["ganancia_disponible"]
        )
        diferencia_costos = (
            efectivo_contado_costos - efectivo_esperado_costos
        )
        diferencia_ganancias = (
            efectivo_contado_ganancias - efectivo_esperado_ganancias
        )
        total_esperado = (
            efectivo_esperado_costos + efectivo_esperado_ganancias
        )
        total_contado = efectivo_contado_costos + efectivo_contado_ganancias
        diferencia_total = diferencia_costos + diferencia_ganancias

        with self._conexion() as conexion:
            cursor = conexion.execute(
                """
                INSERT INTO cierres_caja (
                    fecha_cierre, base_caja_inicial, total_ingresos,
                    total_costo_mercancia, ganancia_bruta, total_egresos,
                    ganancia_neta, monto_efectivo_esperado, monto_qr_total,
                    monto_bold_total, efectivo_real_contado, diferencia,
                    saldo_inicial_costos, saldo_inicial_ganancias,
                    efectivo_esperado_costos, efectivo_esperado_ganancias,
                    efectivo_contado_costos, efectivo_contado_ganancias,
                    diferencia_costos, diferencia_ganancias, usuario_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                          ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    datetime.now().isoformat(timespec="seconds"),
                    saldo_inicial_costos + saldo_inicial_ganancias,
                    resumen["total"],
                    resumen["costos"],
                    resumen["ganancia"],
                    resumen["egresos"],
                    resumen["ganancia_disponible"],
                    total_esperado,
                    resumen["qr"],
                    resumen["bold"],
                    total_contado,
                    diferencia_total,
                    saldo_inicial_costos,
                    saldo_inicial_ganancias,
                    efectivo_esperado_costos,
                    efectivo_esperado_ganancias,
                    efectivo_contado_costos,
                    efectivo_contado_ganancias,
                    diferencia_costos,
                    diferencia_ganancias,
                    usuario_id,
                ),
            )
            return (
                cursor.lastrowid,
                efectivo_esperado_costos,
                efectivo_esperado_ganancias,
                diferencia_costos,
                diferencia_ganancias,
            )
