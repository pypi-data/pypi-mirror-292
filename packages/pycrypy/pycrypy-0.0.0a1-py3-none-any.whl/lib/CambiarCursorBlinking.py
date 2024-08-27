#!/usr/bin/env python3

# Author: Daniel Benjamin Perez Morales
# GitHub: https://github.com/DanielPerezMoralesDev13
# Email: danielperezdev@proton.me

from config.Path import rutaAlacrittyToml
from typing import Dict, Any, List
from toml import load, dump
from lib.ClaveAlacritty import claveCursor
from lib.FormatColorAnsi import bold, italic

# Cambiar Cursor Blinking -> Abreviado ccb
async def ccb(*, nombreBlinking: str, l: List[str]) -> None:
    """
    Cambia la configuración de parpadeo del cursor en el fichero de configuración de Alacritty.

    Esta función actualiza la configuración de parpadeo del cursor en el fichero `alacritty.toml`, permitiendo personalizar cómo parpadea el cursor en el emulador de terminal Alacritty. Si ciertas claves no existen en la configuración, la función las añade con valores predeterminados.

    Parámetros:
    - `nombreBlinking (str)`: El nuevo valor de parpadeo para el cursor.
    - `l (List[str])`: Una lista de comandos para mostrar en la terminal si la flag -v está activada.

    Acciones:
    1. Lee el fichero de configuración `alacritty.toml`.
    2. Actualiza el valor de parpadeo del cursor (`blinking`) en la configuración.
    3. Añade claves predeterminadas si no existen en la configuración.
    4. Escribe los cambios de vuelta en el fichero de configuración.
    5. Agrega el comando de parpadeo a la lista de comandos para la salida detallada.

    Retorna:
    - `None`
    """

    with open(file = rutaAlacrittyToml, mode = "r", encoding = "utf-8") as f:
        dataCursorBlinking: Dict[str, Any] = load(f = f)

    claveCursor["cursor"]["style"]["blinking"] = nombreBlinking

    if "cursor" not in dataCursorBlinking: dataCursorBlinking.update(claveCursor)
    
    if "thickness" not in dataCursorBlinking["cursor"]: dataCursorBlinking["cursor"] = dict(thickness = 0.15)
    if "style" not in dataCursorBlinking["cursor"]: dataCursorBlinking["cursor"]["style"] = dict(shape = "Block", blinking = nombreBlinking)
    if "shape" not in dataCursorBlinking["cursor"]["style"]: dataCursorBlinking["cursor"]["style"] = dict(shape = "Block")

    dataCursorBlinking["cursor"]["style"]["blinking"] = nombreBlinking
    # Sobre Escribimos el fichero
    with open(file = rutaAlacrittyToml, mode = "w") as f: dump(o = dataCursorBlinking, f = f)

    # Agregar la clave al listado de comandos para mostrar en la terminal si la flag -v es activada
    l.append(f"{bold(t = 'Blinking: ', c = 'verde')}{italic(t = nombreBlinking, c = 'cyan')}")
    return None
