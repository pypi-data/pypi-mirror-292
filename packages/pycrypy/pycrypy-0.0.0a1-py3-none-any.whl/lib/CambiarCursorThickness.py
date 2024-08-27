#!/usr/bin/env python3

# Author: Daniel Benjamin Perez Morales
# GitHub: https://github.com/DanielPerezMoralesDev13
# Email: danielperezdev@proton.me

from config.Path import rutaAlacrittyToml
from typing import Dict, Any, List
from toml import load, dump
from lib.ClaveAlacritty import claveCursor
from lib.FormatColorAnsi import bold, italic

# Cambiar cursor thickness -> Abreviado: cct
async def cct(*, grosorCursorThickness: float, l: List[str]) -> None:
    """
    Cambia la configuración del grosor del cursor en el fichero de configuración de Alacritty.

    Esta función actualiza la configuración del grosor del cursor en el fichero `alacritty.toml`, permitiendo personalizar cómo se muestra el grosor del cursor en el emulador de terminal Alacritty. Si ciertas claves no existen en la configuración, la función las añade con valores predeterminados.

    Parámetros:
    - `grosorCursorThickness (float)`: El nuevo valor del grosor del cursor.
    - `l (List[str])`: Una lista de comandos para mostrar en la terminal si la flag -v está activada.

    Acciones:
    1. Lee el fichero de configuración `alacritty.toml`.
    2. Actualiza el valor del grosor del cursor (`thickness`) en la configuración.
    3. Añade claves predeterminadas si no existen en la configuración.
    4. Escribe los cambios de vuelta en el fichero de configuración.
    5. Agrega el comando de grosor del cursor a la lista de comandos para la salida detallada.

    Retorna:
    - `None`
    """

    with open(file = rutaAlacrittyToml, mode = "r", encoding = "utf-8") as f:
        dataCursorThickness: Dict[str, Any] = load(f = f)
    
    claveCursor["cursor"]["style"]["thickness"] = grosorCursorThickness

    if "cursor" not in dataCursorThickness: dataCursorThickness.update(claveCursor)
    if "thickness" not in dataCursorThickness["cursor"]: dataCursorThickness["cursor"] = dict(thickness = grosorCursorThickness)
    else: dataCursorThickness["cursor"]["thickness"] = grosorCursorThickness
    if "style" not in dataCursorThickness["cursor"]: dataCursorThickness["cursor"]["style"] = dict(shape = grosorCursorThickness, blinking = "off")
    if "blinking" not in dataCursorThickness["cursor"]["style"]: dataCursorThickness["cursor"]["style"] = dict(blinking = "off")
    
    # Sobre Escribimos el fichero
    with open(file = rutaAlacrittyToml, mode = "w") as f: dump(o = dataCursorThickness, f = f)

    # Agregar la clave al listado de comandos para mostrar en la terminal si la flag -v es activada
    l.append(f"{bold(t = 'Thickness: ', c = 'verde')}{italic(t = str(grosorCursorThickness), c = 'cyan')}")
    return None
