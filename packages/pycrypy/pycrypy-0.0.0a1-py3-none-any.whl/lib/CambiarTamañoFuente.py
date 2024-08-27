#!/usr/bin/env python3

# Author: Daniel Benjamin Perez Morales
# GitHub: https://github.com/DanielPerezMoralesDev13
# Email: danielperezdev@proton.me

from config.Path import rutaAlacrittyToml
from typing import Dict, Any, List
from toml import load, dump
from lib.ClaveAlacritty import font
from lib.FormatColorAnsi import bold, italic

# Cambiar Tamaño Fuente: Abreviado -> ctf
async def ctf(*, tamañoFuente: float, l: List[str]) -> None:
    """
    Cambia el tamaño de la fuente en el fichero de configuración de Alacritty.

    Esta función actualiza el tamaño de la fuente en el fichero `alacritty.toml`, permitiendo personalizar el tamaño del texto en el emulador de terminal Alacritty. Si ciertas claves no existen en la configuración, la función las añade con valores predeterminados.

    Parámetros:
    - `tamañoFuente (float)`: El nuevo tamaño de la fuente a establecer.
    - `l (List[str])`: Una lista de comandos para mostrar en la terminal si la flag -v está activada.

    Acciones:
    1. Lee el fichero de configuración `alacritty.toml`.
    2. Actualiza el valor del tamaño de la fuente (`font.size`) en la configuración.
    3. Añade claves predeterminadas si no existen en la configuración, incluyendo `font.normal` y `font.offset`.
    4. Escribe los cambios de vuelta en el fichero de configuración.
    5. Agrega el comando del tamaño de la fuente a la lista de comandos para la salida detallada.

    Retorna:
    - `None`
    """
    with open(file = rutaAlacrittyToml, mode = "r", encoding = "utf-8") as f: dataTamañoFuente: Dict[str, Any] = load(f = f)
    if "normal" not in dataTamañoFuente["font"]: dataTamañoFuente["font"]["normal"] = dict(family = font, style = "Regular")
    if "family" not in dataTamañoFuente["font"]["normal"]: dataTamañoFuente["font"]["normal"]["family"] = font
    if "offset" not in dataTamañoFuente["font"]: dataTamañoFuente["font"]["offset"] = dict(x = 0, y = 0)
    dataTamañoFuente["font"]["size"] = tamañoFuente

    # Sobre Escribimos el fichero
    with open(file = rutaAlacrittyToml, mode = "w") as f: dump(o = dataTamañoFuente, f = f)

    # Agregar la clave al listado de comandos para mostrar en la terminal si la flag -v es activada
    l.append(f"{bold(t = 'Size Font: ', c = 'verde')}{italic(t = str(tamañoFuente), c = 'cyan')}")
    return None
