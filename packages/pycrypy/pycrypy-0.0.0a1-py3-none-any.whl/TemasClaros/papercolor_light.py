# Author: Daniel Benjamin Perez Morales
# GitHub: https://github.com/DanielPerezMoralesDev13
# Email: danielperezdev@proton.me

from typing import Dict, Any
from toml import loads

papercolor_light: Dict[str, Any] = loads(s = """\
    # Colors (PaperColor - Light)

    # Default colors
    [colors.primary]
    background = '#eeeeee'
    foreground = '#444444'

    [colors.cursor]
    text = '#eeeeee'
    cursor = '#444444'

    # Normal colors
    [colors.normal]
    black   = '#eeeeee'
    red     = '#af0000'
    green   = '#008700'
    yellow  = '#5f8700'
    blue    = '#0087af'
    magenta = '#878787'
    cyan    = '#005f87'
    white   = '#444444'

    # Bright colors
    [colors.bright]
    black   = '#bcbcbc'
    red     = '#d70000'
    green   = '#d70087'
    yellow  = '#8700af'
    blue    = '#d75f00'
    magenta = '#d75f00'
    cyan    = '#005faf'
    white   = '#005f87'
    """
)