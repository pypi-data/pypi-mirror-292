# Author: Daniel Benjamin Perez Morales
# GitHub: https://github.com/DanielPerezMoralesDev13
# Email: danielperezdev@proton.me

from typing import Dict, Any
from toml import loads

greenscreen: Dict[str, Any] = loads(s = """\
    # Themes Colors (greenscreen)

    # Default colors greenscreen
    [colors.primary]
    background = '#0f101a'
    foreground = '#67e689'

    # Normal colors greenscreen
    [colors.normal]
    black = '#181a29'
    red = '#007700'
    green = '#00bb00'
    yellow = '#7fde5d'
    blue = '#4dbd72'
    magenta = '#2e9e3e'
    cyan = '#4ddb7c'
    white = '#67e689'
        
    # Bright colors greenscreen
    [colors.bright]
    black = '#282a40'
    red = '#007700'
    green = '#00bb00'
    yellow = '#7fde5d'
    blue = '#4dbd72'
    magenta = '#2e9e3e'
    cyan = '#4ddb7c'
    white = '#57d979'
    """
)