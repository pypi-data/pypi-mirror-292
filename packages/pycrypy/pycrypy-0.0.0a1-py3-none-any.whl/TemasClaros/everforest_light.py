# Author: Daniel Benjamin Perez Morales
# GitHub: https://github.com/DanielPerezMoralesDev13
# Email: danielperezdev@proton.me

from typing import Dict, Any
from toml import loads

everforest_light: Dict[str, Any] = loads(s = """\
    # Colors (Everforest Light)

    # Default colors
    [colors.primary]
    background = '#fdf6e3'
    foreground = '#5c6a72'

    # Normal colors
    [colors.normal]
    black   = '#5c6a72'
    red     = '#f85552'
    green   = '#8da101'
    yellow  = '#dfa000'
    blue    = '#3a94c5'
    magenta = '#df69ba'
    cyan    = '#35a77c'
    white   = '#e0dcc7'

    # Bright Colors
    [colors.bright]
    black   = '#5c6a72'
    red     = '#f85552'
    green   = '#8da101'
    yellow  = '#dfa000'
    blue    = '#3a94c5'
    magenta = '#df69ba'
    cyan    = '#35a77c'
    white   = '#e0dcc7'
    """
)