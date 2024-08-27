# Author: Daniel Benjamin Perez Morales
# GitHub: https://github.com/DanielPerezMoralesDev13
# Email: danielperezdev@proton.me

from typing import Dict, Any
from toml import loads

ayu_dark: Dict[str, Any] = loads(s = """\
    # Colors (Ayu Dark)

    # Default colors
    [colors.primary]
    background = '#0A0E14'
    foreground = '#B3B1AD'

    # Normal colors
    [colors.normal]
    black   = '#01060E'
    red     = '#EA6C73'
    green   = '#91B362'
    yellow  = '#F9AF4F'
    blue    = '#53BDFA'
    magenta = '#FAE994'
    cyan    = '#90E1C6'
    white   = '#C7C7C7'

    # Bright colors
    [colors.bright]
    black   = '#686868'
    red     = '#F07178'
    green   = '#C2D94C'
    yellow  = '#FFB454'
    blue    = '#59C2FF'
    magenta = '#FFEE99'
    cyan    = '#95E6CB'
    white   = '#FFFFFF'
    """
)