# Author: Daniel Benjamin Perez Morales
# GitHub: https://github.com/DanielPerezMoralesDev13
# Email: danielperezdev@proton.me

from typing import Dict, Any
from toml import loads

ayu_mirage: Dict[str, Any] = loads(s = """\
    # Themes Colors (ayu-mirage)

    # Default colors primary ayu-mirage
    [colors.primary]
    background = '#202734'
    foreground = '#CBCCC6'

    # Normal colors ayu-mirage
    [colors.normal]
    black = '#191E2A'
    red = '#FF3333'
    green = '#BAE67E'
    yellow = '#FFA759'
    blue = '#73D0FF'
    magenta = '#FFD580'
    cyan = '#95E6CB'
    white = '#C7C7C7'

    # Bright colors theme ayu-mirage
    [colors.bright]
    black = '#686868'
    red = '#F27983'
    green = '#A6CC70'
    yellow = '#FFCC66'
    blue = '#5CCFE6'
    magenta = '#FFEE99'
    cyan = '#95E6CB'
    white = '#FFFFFF'
    """
)