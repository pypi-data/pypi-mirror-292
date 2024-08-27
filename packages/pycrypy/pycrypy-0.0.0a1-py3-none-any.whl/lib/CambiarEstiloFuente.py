#!/usr/bin/env python3

# Author: Daniel Benjamin Perez Morales
# GitHub: https://github.com/DanielPerezMoralesDev13
# Email: danielperezdev@proton.me

from config.Path import rutaAlacrittyToml
from typing import Dict, Any, List
from toml import load, dump
from lib.ClaveAlacritty import font
from lib.FormatColorAnsi import bold, italic

# Cambiar Estilo Fuente -> Abreviado cef
async def cef(*, estiloFuente: str, l: List[str]) -> None:
    """
    Cambia la configuración del estilo de la fuente en el fichero de configuración de Alacritty.

    Esta función actualiza la configuración del estilo de la fuente en el fichero `alacritty.toml`, permitiendo personalizar cómo se muestra el estilo de la fuente en el emulador de terminal Alacritty. Si ciertas claves no existen en la configuración, la función las añade con valores predeterminados.

    Parámetros:
    - `estiloFuente (str)`: El nuevo valor del estilo de la fuente.
    - `l (List[str])`: Una lista de comandos para mostrar en la terminal si la flag -v está activada.

    Acciones:
    1. Lee el fichero de configuración `alacritty.toml`.
    2. Actualiza el valor del estilo de la fuente (`style`) en la configuración.
    3. Añade claves predeterminadas si no existen en la configuración.
    4. Escribe los cambios de vuelta en el fichero de configuración.
    5. Agrega el comando de estilo de la fuente a la lista de comandos para la salida detallada.

    Retorna:
    - `None`
    """

    with open(file = rutaAlacrittyToml, mode = "r", encoding = "utf-8") as f:
        dataEstiloFuente: Dict[str, Any] = load(f = f)
    
    if "normal" not in dataEstiloFuente["font"]:
        dataEstiloFuente["font"]["normal"] = dict(family = font, style = estiloFuente)

    if "style" not in dataEstiloFuente["font"]["normal"]:
        dataEstiloFuente["font"]["normal"]["style"] = estiloFuente
    
    if "style" in dataEstiloFuente["font"]["normal"]:
        dataEstiloFuente["font"]["normal"]["style"] = estiloFuente
    
    # Sobre Escribimos el fichero
    with open(file = rutaAlacrittyToml, mode = "w") as f: dump(o = dataEstiloFuente, f = f)

    # Agregar la clave al listado de comandos para mostrar en la terminal si la flag -v es activada
    l.append(f"{bold(t = 'Style: ', c = 'verde')}{italic(t = estiloFuente, c = 'cyan')}")
    return None
