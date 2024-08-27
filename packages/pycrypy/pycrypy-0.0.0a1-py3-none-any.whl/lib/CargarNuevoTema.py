#!/usr/bin/env python3

# Author: Daniel Benjamin Perez Morales
# GitHub: https://github.com/DanielPerezMoralesDev13
# Email: danielperezdev@proton.me

from toml import TomlDecodeError, load, dump
from typing import Dict, Any, List, Optional
from config.Errors import net
from config.Path import rutaAlacrittyToml
from lib.ClaveAlacritty import *
from config.Themes import * # temasClaros, temasOscuros, temasRecomendados
from sys import stderr, exit
from lib.FormatColorAnsi import bold, italic

#region Cargar Tema
# Cargar Nuevo Tema -> Abreivado cnt
async def cnt(*, nuevoTemaAlacritty: str, l: List[str]) -> None:
    """
    Carga un nuevo tema de configuración para Alacritty desde un módulo de tema especificado.

    Esta función busca un tema específico en los módulos de temas disponibles (`TemasClaros`, `TemasOscuros`, `TemasRecomendados`). Si el tema es encontrado, se carga la configuración del tema en la terminal de Alacritty. Si el fichero de configuración actual tiene problemas de formato, la función lo maneja y lo corrige si es necesario.

    Parámetros:
    - `nuevoTemaAlacritty (str)`: El nombre del nuevo tema que se desea cargar.
    - `l (List[str])`: Una lista de comandos para mostrar en la terminal si la flag -v está activada.

    Acciones:
    1. Carga los temas de los módulos `TemasClaros`, `TemasOscuros`, y `TemasRecomendados`.
    2. Verifica si el tema especificado (`nuevoTemaAlacritty`) existe en los módulos de temas cargados.
    3. Importa dinámicamente el módulo del tema desde el diccionario correspondiente y obtiene la configuración del tema.
    4. Si el tema no se encuentra en ninguno de los módulos, imprime un mensaje de error y termina la ejecución.
    5. Intenta leer el fichero de configuración de Alacritty (`rutaAlacrittyToml`). Si el fichero tiene un formato incorrecto, lo sobreescribe con un fichero vacío y vuelve a leerlo.
    6. Llama a la función `sta` para aplicar el nuevo tema a la configuración actual de Alacritty.
    7. Agrega un mensaje de error a la lista de comandos si el fichero de configuración de Alacritty tenía problemas de formato.

    Retorna:
    - `None`
    """
    # Cargar los temas dinamicamente
    # temasClarosDiccionario: Dict[str, Any] = await cargar_temas(moduloBase = "TemasClaros", nombresTemas = temasClaros.copy())
    # temasOscurosDiccionario: Dict[str, Any] = await cargar_temas(moduloBase = "TemasOscuros" , nombresTemas = temasOscuros.copy())
    # temasRecomendadosDiccionario: Dict[str, Any] = await cargar_temas(moduloBase = "TemasRecomendados" , nombresTemas  = temasRecomendados.copy())
    
    temasClarosDiccionario: Dict[str, Any] = dict()
    temasOscurosDiccionario: Dict[str, Any] = dict()
    temasRecomendadosDiccionario: Dict[str, Any] = dict()

    existeTema: bool = False
    moduloTema: Optional[ModuleType] = None
    dataNuevoTema: Dict[str, Any] = dict()

    """
    >>> importlib.import_module se usa para importar dinámicamente un módulo.
    >>> hasattr se usa para verificar si un objeto tiene un atributo o variable.
    >>> getattr se usa para obtener el valor de un atributo o variable dentro de un objeto.
    """
    # Verifica si el módulo está en el diccionario
    if nuevoTemaAlacritty in temasRecomendados:
        temasRecomendadosDiccionario.update(await cargar_temas(moduloBase = "TemasRecomendados", nombresTema = nuevoTemaAlacritty))

        # Importa el módulo dinámicamente desde el diccionario
        moduloTema = temasRecomendadosDiccionario[nuevoTemaAlacritty]

        # Aquí asumimos que `nuevoTemaAlacritty` es una variable dentro del módulo
        if hasattr(moduloTema, nuevoTemaAlacritty):
            dataNuevoTema = getattr(moduloTema, nuevoTemaAlacritty)
            existeTema = True

        else: print(f"No se encontró la variable {nuevoTemaAlacritty} dentro del módulo {nuevoTemaAlacritty}", file = stderr)
    
    # Verifica si el módulo está en el diccionario
    if not existeTema and nuevoTemaAlacritty in temasClaros:
        
        temasClarosDiccionario.update(await cargar_temas(moduloBase = "TemasClaros", nombresTema = nuevoTemaAlacritty))

        # Importa el módulo dinámicamente desde el diccionario
        moduloTema = temasClarosDiccionario[nuevoTemaAlacritty]
        
        # Aquí asumimos que `nuevoTemaAlacritty` es una variable dentro del módulo
        if hasattr(moduloTema, nuevoTemaAlacritty): 
            dataNuevoTema = getattr(moduloTema, nuevoTemaAlacritty)
            existeTema = True

        else: print(f"No se encontró la variable {nuevoTemaAlacritty} dentro del módulo {nuevoTemaAlacritty}", file = stderr)
    

    # Verifica si el módulo está en el diccionario
    if not existeTema and nuevoTemaAlacritty in temasOscuros:

        temasOscurosDiccionario.update(await cargar_temas(moduloBase = "TemasOscuros", nombresTema = nuevoTemaAlacritty))

        # Importa el módulo dinámicamente desde el diccionario
        moduloTema = temasOscurosDiccionario[nuevoTemaAlacritty]

        # Aquí asumimos que `nuevoTemaAlacritty` es una variable dentro del módulo
        if hasattr(moduloTema, nuevoTemaAlacritty): 
            dataNuevoTema = getattr(moduloTema, nuevoTemaAlacritty)
            existeTema = True
        else: print(f"No se encontró la variable {nuevoTemaAlacritty} dentro del módulo {nuevoTemaAlacritty}", end="\n", file = stderr)
    
    if not existeTema:
        print(await net(nombreTema = nuevoTemaAlacritty), end="\n", file = stderr)
        exit(1)
    
    e: Optional[TomlDecodeError] = None
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
        nuevoTemaAlacritty = nuevoTemaAlacritty,
        l = l
    )
        
    return None

#region Cambiar Tema
# Funcion que cambia el tema de alacritty
# SobreEscribir Tema -> Abreviado: sta
async def sta(
    rutaAlacrittyToml: str, 
    dataNuevoTema: Dict[str, Any],
    dataTemaActual: Dict[str, Any],
    nuevoTemaAlacritty: str,
    l: List[str]
) -> None:
    """
    Sobrescribe la configuración del tema en el fichero de configuración de Alacritty.

    Esta función actualiza la configuración actual de Alacritty con los valores del nuevo tema especificado. Si alguna clave necesaria no está presente en la configuración actual, se crea con valores por defecto. Finalmente, se guarda la configuración actualizada en el fichero de configuración de Alacritty.

    Parámetros:
    - `rutaAlacrittyToml (str)`: La ruta del fichero de configuración de Alacritty que se va a actualizar.
    - `dataNuevoTema (Dict[str, Any])`: La configuración del nuevo tema que se aplicará.
    - `dataTemaActual (Dict[str, Any])`: La configuración actual de Alacritty que se actualizará.
    - `nuevoTemaAlacritty (str)`: El nombre del nuevo tema que se aplicará.
    - `l (List[str])`: Una lista de comandos para mostrar en la terminal si la flag -v está activada.

    Acciones:
    1. Verifica si el fichero del nuevo tema contiene la clave `colors`. Si no, imprime un mensaje de error y termina la ejecución.
    2. Actualiza la configuración actual con los colores del nuevo tema.
    3. Valida y asegura que las claves necesarias (`font`, `window`, `cursor`) estén presentes en la configuración actual, creando las claves con valores por defecto si faltan.
    4. Sobrescribe el fichero de configuración de Alacritty con la configuración actualizada.
    5. Agrega un mensaje a la lista de comandos si la flag -v está activada, indicando que el nuevo tema ha sido aplicado.

    Retorna:
    - `None`
    """
    
    if "colors" not in dataNuevoTema:
        print(f"{bold(t = 'Error: El contenido del fichero no es valido', c = 'rojo')}", file = stderr, end="\n")
        exit(1)
    
    # Creamos la key colors
    dataTemaActual["colors"] = dataNuevoTema["colors"]

    # * Validacion de que existen todos los campos y si no existen los creamos las claves con sus valores por defecto
    if "font" not in dataTemaActual: dataTemaActual.update(claveFont)
    if "size" not in dataTemaActual["font"]: dataTemaActual["font"] = dict(size = 11.25)
    if "normal" not in dataTemaActual["font"]: dataTemaActual["font"]["normal"] = dict(family = "monospace", style = "Regular")
    if "family" not in dataTemaActual["font"]["normal"]: dataTemaActual["font"]["normal"]["family"] = "monospace"
    if "style" not in dataTemaActual["font"]["normal"]: dataTemaActual["font"]["normal"]["style"] = "Regular"
    if "offset" not in dataTemaActual["font"]: dataTemaActual["font"]["offset"] = dict(x = 0, y = 0)
    if "x" not in dataTemaActual["font"]["offset"]: dataTemaActual["font"]["offset"]["x"] = 0
    if "y" not in dataTemaActual["font"]["offset"]: dataTemaActual["font"]["offset"]["y"] = 0
    
    # verificamos si existe la key "window" si no creaamos la clave con sus valores por default
    if "window" not in dataTemaActual:  dataTemaActual.update(claveWindow)
    if "opacity" not in dataTemaActual["window"]: dataTemaActual["window"]["opacity"] = 0.9
    if "startup_mode" not in dataTemaActual["window"]: dataTemaActual["window"]["startup_mode"] = "Maximized"
    if "padding" not in dataTemaActual["window"]: dataTemaActual["window"]["padding"] = dict(x = 5, y = 5)
    if "x" not in dataTemaActual["window"]["padding"]: dataTemaActual["window"]["padding"]["x"] = 5
    if "y" not in dataTemaActual["window"]["padding"]: dataTemaActual["window"]["padding"]["y"] = 5
        
    # verificamos si existe la key "cursor" si no creaamos la clave con sus valores por default y
    if "cursor" not in dataTemaActual: dataTemaActual.update(claveCursor)
    if "thickness" not in dataTemaActual["cursor"]: dataTemaActual["cursor"]["thickness"] = 0.15
    if "style" not in dataTemaActual["cursor"]: dataTemaActual["cursor"]["style"] = dict(shape = "Block", blinking = "off")
    if "shape" not in dataTemaActual["cursor"]["style"]: dataTemaActual["cursor"]["style"]["shape"] = "Block"
    if "blinking" not in dataTemaActual["cursor"]["style"]: dataTemaActual["cursor"]["style"]["blinking"] = "off"
    
    # Intercambiamos los valores de los temas
    dataNuevoTema = dataTemaActual

    # # Sobre Escribimos el fichero
    with open(file = rutaAlacrittyToml, mode = "w") as f: dump(o = dataNuevoTema, f = f)
    
    # Agregar la clave al listado de comandos para mostrar en la terCargar el tema el tema actual que usa la terminal de alacrittyminal si la flag -v es activada
    l.append(f"{bold(t = 'Theme: ', c = 'verde')}{italic(t = nuevoTemaAlacritty, c = 'cyan')}")
    return None
#endregion
