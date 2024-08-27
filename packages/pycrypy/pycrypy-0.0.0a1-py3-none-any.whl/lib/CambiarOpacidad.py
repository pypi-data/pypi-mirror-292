#!/usr/bin/env python3

# Author: Daniel Benjamin Perez Morales
# GitHub: https://github.com/DanielPerezMoralesDev13
# Email: danielperezdev@proton.me

from typing import Dict, Any, List
from toml import dump, load
from config.Path import rutaAlacrittyToml
from lib.ClaveAlacritty import claveWindow
from lib.FormatColorAnsi import bold, italic

# Cambiar Opacidad -> Abreviado co
async def co(*, opacidad: float, l: List[str]) -> None:
    """
    Cambia la opacidad de la ventana en el fichero de configuración de Alacritty.

    Esta función actualiza la opacidad de la ventana en el fichero `alacritty.toml`, permitiendo personalizar la transparencia del emulador de terminal Alacritty. Si ciertas claves no existen en la configuración, la función las añade con valores predeterminados.

    Parámetros:
    - `opacidad (float)`: El nuevo nivel de opacidad de la ventana (valor entre 0.0 y 1.0).
    - `l (List[str])`: Una lista de comandos para mostrar en la terminal si la flag -v está activada.

    Acciones:
    1. Lee el fichero de configuración `alacritty.toml`.
    2. Actualiza el valor de la opacidad (`opacity`) en la configuración.
    3. Añade claves predeterminadas si no existen en la configuración, incluyendo `startup_mode` y `padding`.
    4. Escribe los cambios de vuelta en el fichero de configuración.
    5. Agrega el comando de la opacidad a la lista de comandos para la salida detallada.

    Retorna:
    - `None`
    """
    with open(file = rutaAlacrittyToml, mode = "r", encoding = "utf-8") as  f: dataOpacidadActual: Dict[str, Any] = load(f = f)
    claveWindow["window"]["opacity"] = opacidad

    # verificamos si existe la key "window" si no creaamos la clave con sus valores por default
    if "window" not in dataOpacidadActual:  dataOpacidadActual.update(claveWindow)
    if "opacity" not in dataOpacidadActual["window"]: dataOpacidadActual["window"]["opacity"] = opacidad
    else: dataOpacidadActual["window"]["opacity"] = opacidad
    if "startup_mode" not in dataOpacidadActual["window"]: dataOpacidadActual["window"]["startup_mode"] = "Maximized"
    if "padding" not in dataOpacidadActual["window"]: dataOpacidadActual["window"]["padding"] = dict(x = 5, y = 5)
    
    if "x" not in dataOpacidadActual["window"]["padding"]: dataOpacidadActual["window"]["padding"]["x"] = 5    
    if "y" not in dataOpacidadActual["window"]["padding"]: dataOpacidadActual["window"]["padding"]["y"] = 5
    
    with open(file = rutaAlacrittyToml, mode = "w") as f: dump(o = dataOpacidadActual, f = f)

    # Agregar la clave al listado de comandos para mostrar en la terminal si la flag -v es activada
    l.append(f"{bold(t = 'Opacity: ', c = 'verde')}{italic(t = str(opacidad), c = 'cyan')}")
    return None
