# POS-Kontrol

Sistema de Control de Inventario y Punto de Venta (POS) para escritorio.
La ventana de inicio de sesión se abre centrada en su tamaño compacto; el menú
principal se abre maximizado, con la barra de tareas de Windows visible.

##  Tecnologías
* **Lenguaje:** Python
* **Control de versiones:** Git & GitHub
* **Entorno:** Visual Studio Code

## Instalación

Instala las dependencias del proyecto antes de ejecutarlo:

```powershell
python -m pip install -r requirements.txt
```

Los catálogos de inventario y los reportes de cierre de caja se exportan en PDF.
El cierre muestra también el detalle de productos vendidos y permite registrar
gastos de caja menor desde la pantalla de reportes. El dinero se distribuye en
dos fondos: costos para reponer los productos y ganancias. La reserva de costos
se calcula con el costo de todos los productos vendidos; los gastos de caja
menor se descuentan únicamente de las ganancias. Cada fondo tiene su propio
saldo inicial, efectivo esperado, conteo físico y diferencia. Los saldos iniciales
se cargan automáticamente desde el último cierre, incluso al cambiar de mes. Si
todavía no existe ningún cierre, ambos fondos comienzan en cero. La distribución
incluye las ventas pagadas en efectivo, QR y Bold.
Los reportes diarios muestran también el total vendido acumulado durante el mes;
ese acumulado se calcula por fechas y empieza de nuevo en cada mes, mientras que
los saldos de costos y ganancias se conservan desde el último cierre.

##  Proyecto Formativo SENA
Desarrollo de software orientado a la gestión eficiente de inventarios y ventas.
