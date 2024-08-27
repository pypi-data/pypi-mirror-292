#!/usr/bin/env python3

# Author: Daniel Benjamin Perez Morales
# GitHub: https://github.com/DanielPerezMoralesDev13
# Email: danielperezdev@proton.me

from config.Path import rutaAlacrittyToml
from typing import Dict, Any, List
from toml import load, dump
from lib.FormatColorAnsi import bold, italic

# Cambiar Fuente -> Abreviado cf
async def cf(*, nombreFuente: str, l: List[str]) -> None:
    """
    Cambia la configuración de la fuente en el fichero de configuración de Alacritty.

    Esta función actualiza la configuración de la fuente en el fichero `alacritty.toml`, permitiendo personalizar la fuente utilizada en el emulador de terminal Alacritty. Si ciertas claves no existen en la configuración, la función las añade con valores predeterminados.

    Parámetros:
    - `nombreFuente (str)`: El nuevo nombre de la fuente.
    - `l (List[str])`: Una lista de comandos para mostrar en la terminal si la flag -v está activada.

    Acciones:
    1. Lee el fichero de configuración `alacritty.toml`.
    2. Actualiza el valor de la familia de la fuente (`family`) en la configuración.
    3. Añade claves predeterminadas si no existen en la configuración.
    4. Escribe los cambios de vuelta en el fichero de configuración.
    5. Agrega el comando de la fuente a la lista de comandos para la salida detallada.

    Retorna:
    - `None`
    """
    with open(file = rutaAlacrittyToml, mode = "r", encoding = "utf-8") as f: dataNuevaFuente: Dict[str, Any] = load(f = f)
    
    if "normal" not in dataNuevaFuente["font"]: dataNuevaFuente["font"]["normal"] = dict(family = nombreFuente, style = "Regular")

    if "family" not in dataNuevaFuente["font"]["normal"]: dataNuevaFuente["font"]["normal"]["family"] = nombreFuente

    if "family" in dataNuevaFuente["font"]["normal"]: dataNuevaFuente["font"]["normal"]["family"] = nombreFuente

    # Sobre Escribimos el fichero
    with open(file = rutaAlacrittyToml, mode = "w") as f: dump(o = dataNuevaFuente, f = f)

    # Agregar la clave al listado de comandos para mostrar en la terminal si la flag -v es activada
    l.append(f"{bold(t = 'Font: ', c = 'verde')}{italic(t = nombreFuente, c = 'cyan')}")
    return None
