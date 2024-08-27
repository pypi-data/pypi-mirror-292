# Author: Daniel Benjamin Perez Morales
# GitHub: https://github.com/DanielPerezMoralesDev13
# Email: danielperezdev@proton.me

from typing import Dict, Any
from toml import loads

enfocado_dark: Dict[str, Any] = loads(s = """\
    # Theme: enfocado_dark
    # Source:  https://github.com/wuelnerdotexe/vim-enfocado

    # Default colors
    [colors.primary]
    background =  '#181818'
    foreground =  '#b9b9b9'

    # Normal colors
    [colors.normal]
    black   = '#3b3b3b'
    red     = '#ed4a46'
    green   = '#70b433'
    yellow  = '#dbb32d'
    blue    = '#368aeb'
    magenta = '#eb6eb7'
    cyan    = '#3fc5b7'
    white   = '#b9b9b9'

    # Bright colors
    [colors.bright]
    black   = '#777777'
    red     = '#ff5e56'
    green   = '#83c746'
    yellow  = '#efc541'
    blue    = '#4f9cfe'
    magenta = '#ff81ca'
    cyan    = '#56d8c9'
    white   = '#dedede'
    """
)