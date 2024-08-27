#!/usr/bin/env python3

# Author: Daniel Benjamin Perez Morales
# GitHub: https://github.com/DanielPerezMoralesDev13
# Email: danielperezdev@proton.me

from typing import List, Dict, Any
from toml import dump, load
from config.Path import rutaAlacrittyToml
from lib.ClaveAlacritty import claveWindow
from lib.FormatColorAnsi import bold, italic

# Cambiar padding -> Abreviado: cp
async def cp(*, listaPadding: List[int], l: List[str]) -> None:
    """
    Cambia el padding de la ventana en el fichero de configuración de Alacritty.

    Esta función actualiza los valores de padding en el fichero `alacritty.toml`, permitiendo personalizar el espacio entre el contenido de la ventana y sus bordes en el emulador de terminal Alacritty. Si ciertas claves no existen en la configuración, la función las añade con valores predeterminados.

    Parámetros:
    - `listaPadding (List[int])`: Una lista con dos valores enteros que representan el padding en los ejes x e y, respectivamente.
    - `l (List[str])`: Una lista de comandos para mostrar en la terminal si la flag -v está activada.

    Acciones:
    1. Lee el fichero de configuración `alacritty.toml`.
    2. Actualiza los valores de padding (`padding.x` y `padding.y`) en la configuración.
    3. Añade claves predeterminadas si no existen en la configuración, incluyendo `opacity` y `startup_mode`.
    4. Escribe los cambios de vuelta en el fichero de configuración.
    5. Agrega el comando del padding a la lista de comandos para la salida detallada.

    Retorna:
    - `None`
    """
    with open(file = rutaAlacrittyToml, mode = "r", encoding = "utf-8") as  f: dataPaddingActual: Dict[str, Any] = load(f = f)
    claveWindow["window"]["padding"]["x"] = listaPadding[0]
    claveWindow["window"]["padding"]["y"] = listaPadding[1]

    # verificamos si existe la key "window" si no creaamos la clave con sus valores por default
    if "window" not in dataPaddingActual:  dataPaddingActual.update(claveWindow)
    if "opacity" not in dataPaddingActual["window"]: dataPaddingActual["window"]["opacity"] = 0.9
    if "startup_mode" not in dataPaddingActual["window"]: dataPaddingActual["window"]["startup_mode"] = "Maximized"
    if "padding" not in dataPaddingActual["window"]: dataPaddingActual["window"]["padding"] = dict(x = listaPadding[0], y = listaPadding[1])
    
    if "x" not in dataPaddingActual["window"]["padding"]: dataPaddingActual["window"]["padding"]["x"] = listaPadding[0]
    else: dataPaddingActual["window"]["padding"]["x"] = listaPadding[0]
    
    if "y" not in dataPaddingActual["window"]["padding"]: dataPaddingActual["window"]["padding"]["y"] = listaPadding[1]
    else: dataPaddingActual["window"]["padding"]["y"] = listaPadding[1]


    with open(file = rutaAlacrittyToml, mode = "w") as f: dump(o = dataPaddingActual, f = f)

    # Agregar la clave al listado de comandos para mostrar en la terminal si la flag -v es activada
    l.append(f"{bold(t = 'Padding: ', c = 'verde')}{italic(t =  list(map(lambda i: str(i), listaPadding)), c = 'cyan')}")
    return None