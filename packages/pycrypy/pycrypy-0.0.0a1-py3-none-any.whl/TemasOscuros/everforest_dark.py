# Author: Daniel Benjamin Perez Morales
# GitHub: https://github.com/DanielPerezMoralesDev13
# Email: danielperezdev@proton.me

from typing import Dict, Any
from toml import loads

everforest_dark: Dict[str, Any] = loads(s = """\
    # Colors (Everforest Dark)

    # Default colors
    [colors.primary]
    background = '#2d353b'
    foreground = '#d3c6aa'

    # Normal colors
    [colors.normal]
    black   = '#475258'
    red     = '#e67e80'
    green   = '#a7c080'
    yellow  = '#dbbc7f'
    blue    = '#7fbbb3'
    magenta = '#d699b6'
    cyan    = '#83c092'
    white   = '#d3c6aa'

    # Bright colors
    [colors.bright]
    black   = '#475258'
    red     = '#e67e80'
    green   = '#a7c080'
    yellow  = '#dbbc7f'
    blue    = '#7fbbb3'
    magenta = '#d699b6'
    cyan    = '#83c092'
    white   = '#d3c6aa'
    """
)