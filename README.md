# Arquitectura Motor de Pagos LBTR – Guía Manim

Escenas y renders del flujo MDP → F5/Apache → OSB → Tux → Tandem.

## Escenas principales
- `archMDP-2014.v105.py` (histórica)
- `archMDP-ASIS.v221.py` (AS-IS 2025, etiqueta en pantalla: v2.2.1)
- Otras iteraciones: `archMDP-ASIS.v200..v220.py` (backups previos)

Clase de escena en todos los scripts: `ArquitecturaMDPLBTR`.

## Requisitos
- Python 3.10+
- Manim CE 0.19.1 (comandos compatibles con esta versión)

Instalación rápida:
```bash
pip install manim
```

## Render recomendado
Usa resoluciones 16:9 para evitar desalineado al abrir.
- 1080p MP4: `manim -pqh archMDP-ASIS.v221.py ArquitecturaMDPLBTR -r 1920,1080 --format=mp4`
- 4K MP4: `manim -pqh archMDP-ASIS.v221.py ArquitecturaMDPLBTR -r 3840,2160 --format=mp4`
- 1080p WebM: `manim -pqh archMDP-ASIS.v221.py ArquitecturaMDPLBTR -r 1920,1080 --format=webm`

Notas:
- Quita `-p` o usa `--disable_preview` si no quieres que abra el video al terminar.
- `-pql` para iterar rápido; render final en `-pqh` o 4K.

## Convenciones de versión
- Cada cambio crea un archivo nuevo con la versión en el nombre.
- La etiqueta de versión en pantalla (`version_document`) debe coincidir con el nombre del archivo.
- No sobrescribir archivos previos; conservarlos para comparar.

## Errores y caché
- Si ves `InvalidDataError` o problemas con partials: borra la carpeta de video de la escena, ej. `rm -rf media/videos/archMDP-ASIS.v221`.
- Para un render completamente limpio: `rm -rf media/videos/archMDP-ASIS.v221 media/Tex media/texts` y luego renderiza.

## Detalles de la escena AS-IS v2.2.1
- 16 transacciones iniciales: 4 quedan en F5 (timeout) y se marcan rojo→gris; el resto llega a Tandem A y se marca en verde.
- Tras los timeouts, se desconecta el flujo original y se muestra bypass vía Apache (MDP → Apache M1 → OSB M1 → Tux A/L → Tandem A).
- 16 transacciones adicionales pasan por Apache y terminan en Tandem A (verdes).
- Se usan leyendas para explicar estados (timeout/éxito/TX) y una etiqueta de versión bajo el título.

## Documentos útiles
- `RENDER.md`: comandos de render (1080p/4K, MP4/WebM).
- `BACKLOG.md`: historias de usuario / pendientes.
- `logs/STATUS.html`: ChangeBacklog (mezcla backlog + cambios).
- `topo.yaml`: ejemplo de entrada para parametrizar nodos/rutas.
- `CONTEXT.md`: reglas e instrucciones de trabajo (prompt interno).

Usa solo el dashboard combinado (`logs/STATUS.html`); el changelog HTML separado ya no se genera.

## Autor / Uso
Mazū (2025). Uso interno e ilustrativo. No redistribuir sin permiso.
