#!/usr/bin/env python3

# Author: Daniel Benjamin Perez Morales
# GitHub: https://github.com/DanielPerezMoralesDev13
# Email: danielperezdev@proton.me

from lib.CargarNuevoTema import sta # sta -> sobreescribir tema actual -> Abreviado: sta
from toml import load, TomlDecodeError
from typing import Dict, Any, List, NoReturn, Optional, Union
from config.Path import rutaAlacrittyToml
from sys import stderr, exit
from lib.FormatColorAnsi import bold, italic

# Cambiar Tema Ruta -> Abreviado: ctr
async def ctr(*, rutaTema: str, l: List[str]) -> Union[None, NoReturn]:
    """
    Cambia el tema de configuración de Alacritty a partir de un fichero de tema especificado.

    Esta función reemplaza el tema actual de Alacritty con uno nuevo cargado desde un fichero de configuración de tema (`rutaTema`). Si el fichero del tema nuevo o el fichero de configuración de Alacritty tienen problemas de formato, la función maneja los errores y toma medidas para corregir el fichero de configuración.

    Parámetros:
    - `rutaTema (str)`: La ruta al fichero de tema que se desea aplicar.
    - `l (List[str])`: Una lista de comandos para mostrar en la terminal si la flag -v está activada.

    Acciones:
    1. Intenta leer el fichero del nuevo tema (`rutaTema`). Si ocurre un error al leer el fichero (como formato incorrecto o fichero no encontrado), imprime un mensaje de error y sale del programa.
    2. Intenta leer el fichero de configuración de Alacritty (`rutaAlacrittyToml`). Si el fichero tiene un formato incorrecto, lo sobreescribe con un fichero vacío y vuelve a leerlo.
    3. Llama a la función `sta` para aplicar el nuevo tema a la configuración actual de Alacritty.
    4. Agrega un mensaje de error a la lista de comandos si el fichero de configuración de Alacritty tenía problemas de formato.

    Retorna:
    - `None`
    """
    e: Optional[TomlDecodeError] = None
    try:
        with open(file = rutaTema, mode = 'r') as f: dataNuevoTema: Dict[str, Any] = load(f = f)
    except (TomlDecodeError, FileNotFoundError) as e:
        print(bold(t = f'Error: `{e}`.', c = 'rojo'), end = '\n', file = stderr)
        print(bold(t = f'Error: Verifique si el formato del fichero `{rutaTema}` es correcto o si la ruta del fichero es correcta.', c = 'verde'), end = '\n', file = stderr) 
        exit(1)

    # Cargar el tema el tema actual que usa la terminal de alacritty
    try:
        with open(file = rutaAlacrittyToml, mode = "r", encoding = "utf-8") as f: dataTemaActual: Dict[str, Any] = load(f = f)
    except TomlDecodeError as e:
        print(bold(t = f'Error: El formato del fichero no es correcto sera sobreescrito `{e}`.', c = 'rojo'), end = '\n', file = stderr)
        with open(file = rutaAlacrittyToml, mode = "w") as f: f.write("")
        with open(file = rutaAlacrittyToml, mode = "r", encoding = "utf-8") as f: dataTemaActual = load(f = f)

        # Agregar la clave al listado de comandos para mostrar en la terCargar el tema el tema actual que usa la terminal de alacrittyminal si la flag -v es activada   
        l.append(f"{bold(t = 'El formato del fichero no es correcto sera sobreescrito `{e}`.', c = 'rojo')}")

    await sta(
        rutaAlacrittyToml = rutaAlacrittyToml,
        dataNuevoTema = dataNuevoTema,
        dataTemaActual = dataTemaActual,
        nuevoTemaAlacritty = rutaTema,
        l = l
    )
    
    return None
