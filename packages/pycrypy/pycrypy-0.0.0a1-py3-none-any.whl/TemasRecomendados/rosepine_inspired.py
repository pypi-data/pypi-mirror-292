# Author: Daniel Benjamin Perez Morales
# GitHub: https://github.com/DanielPerezMoralesDev13
# Email: danielperezdev@proton.me

from typing import Dict, Any
from toml import loads
                                              
rosepine_inspired: Dict[str, Any] = loads(s = """\
    # Themes Colors (rosepine-inspired)

    # Default colors rosepine-inspired
    [colors.primary]
    background = '#1f1d29'
    foreground = '#ffffff'

    # Normal colors rosepine-inspired
    [colors.normal]
    black = '#403c58'
    red = '#ea6f91'
    green = '#9bced7'
    yellow = '#f1ca93'
    blue = '#34738e'
    magenta = '#c3a5e6'
    cyan = '#eabbb9'
    white = '#faebd7'

    # Bright colors rosepine-inspired
    [colors.bright]
    black = '#6f6e85'
    red = '#ea6f91'
    green = '#9bced7'
    yellow = '#f1ca93'
    blue = '#34738e'
    magenta = '#c3a5e6'
    cyan = '#eabbb9'
    white = '#ffffff'
    """
)