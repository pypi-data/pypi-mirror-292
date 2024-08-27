# Author: Daniel Benjamin Perez Morales
# GitHub: https://github.com/DanielPerezMoralesDev13
# Email: danielperezdev@proton.me

from typing import Dict, Any
from toml import loads

oceanic_next: Dict[str, Any] = loads(s = """\
    # Colors (Oceanic Next)

    # Default colors
    [colors.primary]
    background = '#1b2b34'
    foreground = '#d8dee9'

    # Normal colors
    [colors.normal]
    black   = '#29414f'
    red     = '#ec5f67'
    green   = '#99c794'
    yellow  = '#fac863'
    blue    = '#6699cc'
    magenta = '#c594c5'
    cyan    = '#5fb3b3'
    white   = '#65737e'

    # Bright colors
    [colors.bright]
    black   = '#405860'
    red     = '#ec5f67'
    green   = '#99c794'
    yellow  = '#fac863'
    blue    = '#6699cc'
    magenta = '#c594c5'
    cyan    = '#5fb3b3'
    white   = '#adb5c0'
    """
)