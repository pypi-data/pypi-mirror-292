# Author: Daniel Benjamin Perez Morales
# GitHub: https://github.com/DanielPerezMoralesDev13
# Email: danielperezdev@proton.me

from typing import Dict, Any
from toml import loads

vesper: Dict[str, Any] = loads(s = """\
    # Colors (Vesper)
    # Source https://github.com/raunofreiberg/vesper

    [colors.primary]
    background = '#101010'
    foreground = '#ffffff'

    [colors.normal]
    black   = '#101010'
    red     = '#f5a191'
    green   = '#90b99f'
    yellow  = '#e6b99d'
    blue    = '#aca1cf'
    magenta = '#e29eca'
    cyan    = '#ea83a5'
    white   = '#a0a0a0'

    [colors.bright]
    black   = '#7e7e7e'
    red     = '#ff8080'
    green   = '#99ffe4'
    yellow  = '#ffc799'
    blue    = '#b9aeda'
    magenta = '#ecaad6'
    cyan    = '#f591b2'
    white   = '#ffffff'
    """
)