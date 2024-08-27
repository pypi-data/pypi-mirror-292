# Author: Daniel Benjamin Perez Morales
# GitHub: https://github.com/DanielPerezMoralesDev13
# Email: danielperezdev@proton.me

from typing import Dict, Any
from toml import loads

tender: Dict[str, Any] = loads(s = """\
    # Default colors
    [colors.primary]
    background = '#282828'
    foreground = '#eeeeee'

    # Normal colors
    [colors.normal]
    black   = '#282828'
    red     = '#f43753'
    green   = '#c9d05c'
    yellow  = '#ffc24b'
    blue    = '#b3deef'
    magenta = '#d3b987'
    cyan    = '#73cef4'
    white   = '#eeeeee'

    # Bright colors
    [colors.bright]
    black   = '#4c4c4c'
    red     = '#f43753'
    green   = '#c9d05c'
    yellow  = '#ffc24b'
    blue    = '#b3deef'
    magenta = '#d3b987'
    cyan    = '#73cef4'
    white   = '#feffff'
    """
)