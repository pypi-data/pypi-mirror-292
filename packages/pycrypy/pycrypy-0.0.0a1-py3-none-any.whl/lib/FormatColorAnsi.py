#!/usr/bin/env python3

# Author: Daniel Benjamin Perez Morales
# GitHub: https://github.com/DanielPerezMoralesDev13
# Email: danielperezdev@proton.me

from typing import Dict, List, Union
from colored import Fore, Style  # type: ignore

colorDict: Dict[str, str] = {
    "negro": Fore.BLACK,
    "rojo": Fore.RED,
    "verde": Fore.GREEN,
    "amarillo": Fore.YELLOW,
    "azul": Fore.BLUE,
    "cyan": Fore.CYAN,
    "blanco": Fore.WHITE,
}

def bold(*, t: Union[str, List[str]] = "", c: str) -> str:
    """
    ### Esta función devuelve un string con el texto en negrita y el color especificado
    - Colores disponibles: `negro`, `rojo`, `verde`, `amarillo`, `azul`, `cyan`, `blanco`
    - Ejemplo:
    
    ```python
    bold(t = "Hola mundo", c = "verde")
    ```
    """
    if c.lower() in colorDict.keys(): c = colorDict[c.lower()]
    else: c = Fore.BLACK
    color: str = f"{Style.bold}{c}"
    return f"{color}{t}{Style.reset}"

def italic(*, t: Union[str, List[str]] = "", c: str) -> str:
    """
    ### Esta función devuelve un string con el texto en cursiva y el color especificado
    - Colores disponibles: `negro`, `rojo`, `verde`, `amarillo`, `azul`, `cyan`, `blanco`
    - Ejemplo:
    
    ```python
    italic(t = "Hola mundo", c = "verde")
    ```
    """
    if c in colorDict.keys(): c = colorDict[c]
    else: c = Fore.BLACK
    color: str = f"{Style.italic}{c}"
    return f"{color}{t}{Style.reset}"

def underline(*, t: Union[str, List[str]] = "", c: str) -> str:
    """
    ### Esta función devuelve un string con el texto subrayado y el color especificado
    - Colores disponibles: `negro`, `rojo`, `verde`, `amarillo`, `azul`, `cyan`, `blanco`
    - Ejemplo:
    
    ```python
    underline(t = "Hola mundo", c = "verde")
    ```
    """
    if c in colorDict.keys(): c = colorDict[c]
    else: c = Fore.BLACK
    color: str = f"{Style.underline}{c}"
    return f"{color}{t}{Style.reset}"
