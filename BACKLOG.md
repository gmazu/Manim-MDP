# Historias de usuario (arquitectura Manim)

---
## Pendiente (próximo cambio)
- [2025-12-23 12:50] **Flujos**: reforzar líneas con cada transacción (más nítidas al usarse), y hacer salto “entrada al nodo → salida 180° → siguiente” para ver mejor el paso sobre las líneas.
- [2025-12-23 12:50] **Timeline/Changelog**: convertir el subtítulo en changelog dinámico que se actualiza según la línea de tiempo (estilo tail -f).

## HU-01: Visualizar rutas normales (hecho)
- **Como** usuario técnico
- **Quiero** ver las transacciones que fluyen por F5 → OSB → Tux → Tandem
- **Para** entender el comportamiento normal
- **Criterios**: 16 bolitas iniciales; las exitosas llegan a Tandem A visibles y verdes; OSB/Tux/Tandem aparecen rápido (columna completa).

## HU-02: Mostrar timeouts en F5 (hecho)
- **Como** usuario operativo
- **Quiero** ver las transacciones que quedan atascadas en F5
- **Para** evidenciar timeouts
- **Criterios**: 4 bolitas se quedan en F5, se ponen rojas y luego grises; aparece línea y etiqueta “Pago Timeout” apuntando a F5; se desconectan las líneas antiguas.

## HU-03: Reconexión vía Apache (hecho)
- **Como** arquitecto
- **Quiero** ver el bypass por Apache M1 y sus nuevas rutas
- **Para** validar la solución AS-IS
- **Criterios**: aparecen Apache M1/L1; nuevas líneas MDP→Apache M1→OSB M1→Tux A/L→Tandem A; 16 bolitas nuevas pasan por Apache y quedan verdes en Tandem.

## HU-04: Leyendas y versiones (hecho)
- **Como** consumidor del video
- **Quiero** ver la versión y las leyendas de estado
- **Para** identificar la build y los significados
- **Criterios**: versión visible bajo el título (v2.2.x); leyenda con colores (Morandé/Longovilo/Aconcagua/Inactivo/Timeout/Exitosa/TX Pago); etiquetas de timeout/éxito alineadas con las animaciones.

## HU-05: Render rápido y final (hecho)
- **Como** operador
- **Quiero** comandos claros de render
- **Para** generar previews y finales
- **Criterios**: comandos en README/RENDER.md para 1080p/4K MP4/WebM; usar 16:9; opción sin preview (`--disable_preview`).

## HU-06: Entregas visibles en Tandem (hecho)
- **Como** analista
- **Quiero** que las transacciones exitosas queden centradas en Tandem
- **Para** visualizar cantidades entregadas
- **Criterios**: todas las exitosas (iniciales + vía Apache) quedan verdes y se posicionan con offsets sobre Tandem A sin solaparse demasiado.

## HU-07: Líneas más suaves (pendiente)
- **Como** observador
- **Quiero** que las líneas blancas sean menos intensas/difusas
- **Para** que la escena se vea menos cargada visualmente
- **Criterios**: reducir opacidad o stroke de las líneas blancas en conexiones principales.

## Registro de cambios
- [2025-12-30 13:05] **DONE**: rutas con entrada/salida 180° en F5/OSB/Tux y rutas Apache; versión v2.2.7.
- [2025-12-23 12:14] **DONE**: Ajuste de linea de tiempo (alineacion de fechas) y cambio de titulo a TOBE 2026 en hito RollBack F5; version v2.2.4.
- [2025-12-23 13:42] **DONE**: Subtitulo toma `detail` del hito actual en `cronos.yaml` y se actualiza junto a la linea de tiempo.
