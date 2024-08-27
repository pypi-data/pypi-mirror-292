# Author: Daniel Benjamin Perez Morales
# GitHub: https://github.com/DanielPerezMoralesDev13
# Email: danielperezdev@proton.me

from typing import Dict, Any
from toml import loads

rainbow: Dict[str, Any] = loads(s = """\
    # Default colors
    [colors.primary]
    background = '#192835'
    foreground = '#AADA4F'

    # Normal colors
    [colors.normal]
    black   = '#5B4375'
    red     = '#426bb6'
    green   = '#2286b5'
    yellow  = '#5ab782'
    blue    = '#93ca5b'
    magenta = '#c6c842'
    cyan    = '#8a5135'
    white   = '#c54646'

    # Bright colors
    [colors.bright]
    black   = '#5B4375'
    red     = '#426bb6'
    green   = '#2286b5'
    yellow  = '#5ab782'
    blue    = '#93ca5b'
    magenta = '#c6c842'
    cyan    = '#8a5135'
    white   = '#c54646'
    """
)