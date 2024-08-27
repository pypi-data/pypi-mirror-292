#!/usr/bin/env python3

# Author: Daniel Benjamin Perez Morales
# GitHub: https://github.com/DanielPerezMoralesDev13
# Email: danielperezdev@proton.me

from config.Path import rutaAlacrittyToml
from typing import Dict, Any, List
from toml import load, dump
from lib.ClaveAlacritty import claveCursor
from lib.FormatColorAnsi import bold, italic

# Cambiar Curso Shap -> Abreviado: ccs
async def ccs(*, nombreShape: str, l: List[str]) -> None:
    """
    Cambia la configuración de la forma del cursor en el fichero de configuración de Alacritty.

    Esta función actualiza la configuración de la forma del cursor en el fichero `alacritty.toml`, permitiendo personalizar cómo se muestra el cursor en el emulador de terminal Alacritty. Si ciertas claves no existen en la configuración, la función las añade con valores predeterminados.

    Parámetros:
    - `nombreShape (str)`: El nuevo valor de la forma del cursor.
    - `l (List[str])`: Una lista de comandos para mostrar en la terminal si la flag -v está activada.

    Acciones:
    1. Lee el fichero de configuración `alacritty.toml`.
    2. Actualiza el valor de la forma del cursor (`shape`) en la configuración.
    3. Añade claves predeterminadas si no existen en la configuración.
    4. Escribe los cambios de vuelta en el fichero de configuración.
    5. Agrega el comando de forma del cursor a la lista de comandos para la salida detallada.

    Retorna:
    - `None`
    """

    with open(file = rutaAlacrittyToml, mode = "r", encoding = "utf-8") as f:
        dataCursorShape: Dict[str, Any] = load(f = f)
    
    claveCursor["cursor"]["style"]["shape"] = nombreShape

    if "cursor" not in dataCursorShape: dataCursorShape.update(claveCursor)
    if "thickness" not in dataCursorShape["cursor"]: dataCursorShape["cursor"] = dict(thickness = 0.15)
    if "style" not in dataCursorShape["cursor"]: dataCursorShape["cursor"]["style"] = dict(shape = nombreShape, blinking = "off")
    if "blinking" not in dataCursorShape["cursor"]["style"]: dataCursorShape["cursor"]["style"] = dict(blinking = "off")

    dataCursorShape["cursor"]["style"]["shape"] = nombreShape
    
    # # Sobre Escribimos el fichero
    with open(file = rutaAlacrittyToml, mode = "w") as f: dump(o = dataCursorShape, f = f)
    
    # Agregar la clave al listado de comandos para mostrar en la terminal si la flag -v es activada
    l.append(f"{bold(t = 'Shape: ', c = 'verde')}{italic(t = nombreShape, c = 'cyan')}")
    return None
