# README.ctx (instrucciones de trabajo)

Project: Arquitectura Motor de Pagos LBTR (Manim)

Este archivo contiene reglas/convenciones para trabajar con este repo.

## Framework de escritura
- Usamos **PNLoP v3** como framework de escritura en este archivo (se irá completando por secciones).


## Reglas de versionado
- Cada cambio se guarda como un archivo nuevo (`archMDP-ASIS.vXYZ.py`, `archMDP-2014.vXYZ.py`).
- La etiqueta `version_document` (en pantalla) debe coincidir con el número de versión del archivo.
- Evitar sobrescribir versiones históricas salvo que el usuario lo pida explícitamente.

## Inicio de proyecto
- Al comenzar un proyecto nuevo (cuando se pega este contexto), crear/inicializar un repositorio si no existe.

## Forma de trabajar
- Si un cambio depende de detalles (posición exacta, timing, texto), preguntar antes de implementar.
- Si aparece un error, pedir el mensaje exacto y el archivo/versión que se está ejecutando; luego proponer 1–2 hipótesis y un fix.
- Mejor preguntar que “parchar” a ciegas.

## Render / caché
- Para iterar rápido: `-pql` y/o `-n inicio,fin` (rango de animaciones).
- Si falla el render por partials: borrar solo `media/videos/<escena>` antes de borrar `media/Tex`.

## Aprobación y logging
- Antes de ejecutar cambios (copias/ediciones/renombres/borrados) confirmar con el usuario.
- Después de cada cambio aprobado, registrar una entrada en `logs/CHANGELOG.log` (JSONL) con fecha/hora, acción, versión, archivos afectados y nota.

## Checklist rápido antes de entregar una versión
- `version_document` actualizado.
- Leyendas visibles y sin solaparse.
- Líneas/bolitas con el timing acordado.
- Rutas correctas (F5/Apache) y estado correcto (timeout/éxito).
