# Author: Daniel Benjamin Perez Morales
# GitHub: https://github.com/DanielPerezMoralesDev13
# Email: danielperezdev@proton.me

from typing import Dict, Any
from toml import loads

github_dark_high_contrast: Dict[str, Any] = loads(s = """\
    # (Github Dark High Contrast) Colors for Alacritty

    # Default colors
    [colors.primary]
    background = '#0a0c10'
    foreground = '#f0f3f6'

    # Cursor colors
    [colors.cursor]
    text = '#0a0c10'
    cursor = '#f0f3f6'

    # Normal colors
    [colors.normal]
    black = '#7a828e'
    red = '#ff9492'
    green = '#26cd4d'
    yellow = '#f0b72f'
    blue = '#71b7ff'
    magenta = '#cb9eff'
    cyan = '#39c5cf'
    white = '#d9dee3'

    # Bright colors
    [colors.bright]
    black = '#9ea7b3'
    red = '#ffb1af'
    green = '#4ae168'
    yellow = '#f7c843'
    blue = '#91cbff'
    magenta = '#cb9eff'
    cyan = '#39c5cf'
    white = '#d9dee3'
    """
)