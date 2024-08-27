#!/usr/bin/env python3

# Author: Daniel Benjamin Perez Morales
# GitHub: https://github.com/DanielPerezMoralesDev13
# Email: danielperezdev@proton.me

from typing import Dict, Any
from toml import loads
from platform import system

# Definir la variable `font` según el sistema operativo
# * font: str = "monospace" if system() == "Linux" else ("Consolas" if system() == "Windows" else "Menlo") 
font: str = ""
if system() == "Linux": font = "monospace"
elif system() == "Windows": font = "Consolas"
elif system() == "Darwin": font = "Menlo"

# Cargar configuraciones utilizando `loads()` desde cadenas TOML
claveColorPrimary: Dict[str, Any] = loads(s = """\
    [colors.primary]
    background = ''
    foreground = ''
    """
)

claveColorNormal: Dict[str, Any] = loads(s = """\
    [colors.normal]
    black = ''
    red = ''
    green = ''
    yellow = ''
    blue = ''
    magenta = ''
    cyan = ''
    white = ''
    """
)

claveColorBright: Dict[str, Any] = loads(s = """\
    [colors.bright]
    black = ''
    red = ''
    green = ''
    yellow = ''
    blue = ''
    magenta = ''
    cyan = ''
    white = ''
    """
)

claveWindow: Dict[str, Any] = loads(s = """\
    [window]
    padding = { x = 5, y = 5 }
    opacity = 0.9
    startup_mode = "Maximized"
    """
)

claveCursor: Dict[str, Any] = loads(s = """\
    [cursor]
    style = { shape = "Block", blinking = "off" }    # Configura el estilo y el parpadeo del cursor
    thickness = 0.15                                 # Configura el grosor del cursor
    """
)

# Formatear la cadena `claveFont` después de definir `font`
claveFont: Dict[str, Any] = loads(s = """\
    [font]
    normal = {{ family = "{fontFamily}", style = "Regular" }}
    offset = {{ x = 0, y = 0 }}   
    size = 11.25                                     
    """.format(fontFamily = font)
)