# Author: Daniel Benjamin Perez Morales
# GitHub: https://github.com/DanielPerezMoralesDev13
# Email: danielperezdev@proton.me

from typing import Dict, Any
from toml import loads

noctis_lux: Dict[str, Any] = loads(s = """\
    # Colors (NoctixLux)

    # Default colors
    [colors.primary]
    background = '#fef8ec'
    foreground = '#005661'

    # Normal colors
    [colors.normal]
    black = '#003b42'
    red = '#e34e1c'
    green = '#00b368'
    yellow = '#f49725'
    blue = '#0094f0'
    magenta = '#ff5792'
    cyan = '#00bdd6'
    white = '#8ca6a6'

    # Bright colors
    [colors.bright]
    black = '#004d57'
    red = '#ff4000'
    green = '#00d17a'
    yellow = '#ff8c00'
    blue = '#0fa3ff'
    magenta = '#ff6b9f'
    cyan = '#00cbe6'
    white = '#bbc3c4'
    """
)