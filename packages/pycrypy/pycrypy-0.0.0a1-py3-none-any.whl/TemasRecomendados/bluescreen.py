# Author: Daniel Benjamin Perez Morales
# GitHub: https://github.com/DanielPerezMoralesDev13
# Email: danielperezdev@proton.me

from typing import Dict, Any
from toml import loads

bluescreen: Dict[str, Any] = loads(s = """\
    # Themes Colors (bluescreen)

    # Default colors bluescreen
    [colors.primary]
    background = '#011627'
    foreground = '#4fb3ff'
    
    # Normal colors bluescreen
    [colors.normal]
    black = '#181a29'
    red = '#336dff'
    green = '#0091ff'
    yellow = '#47ffd4'
    blue = '#6378ff'
    magenta = '#7a7dff'
    cyan = '#8ffff2'
    white = '#bdfff7'
        
    # Bright colors bluescreen
    [colors.bright]
    black = '#282a40'
    red = '#336dff'
    green = '#0091ff'
    yellow = '#47ffd4'
    blue = '#6378ff'
    magenta = '#7a7dff'
    cyan = '#8ffff2'
    white = '#bce6e0'
    """
)