# Author: Daniel Benjamin Perez Morales
# GitHub: https://github.com/DanielPerezMoralesDev13
# Email: danielperezdev@proton.me

from typing import Dict, Any
from toml import loads

high_contrast: Dict[str, Any] = loads(s = """\
    # Colors (High Contrast)

    # Default colors
    [colors.primary]
    background = '#444444'
    foreground = '#dddddd'

    # Colors the cursor will use if `custom_cursor_colors` is true
    [colors.cursor]
    text = '#aaaaaa'
    cursor = '#ffffff'

    # Normal colors
    [colors.normal]
    black   = '#000000'
    red     = '#ff0000'
    green   = '#00ff00'
    yellow  = '#ffff00'
    blue    = '#0000ff'
    magenta = '#ff00ff'
    cyan    = '#00ffff'
    white   = '#ffffff'

    # Bright colors
    [colors.bright]
    black   = '#000000'
    red     = '#ff0000'
    green   = '#00ff00'
    yellow  = '#ffff00'
    blue    = '#0000ff'
    magenta = '#ff00ff'
    cyan    = '#00ffff'
    white   = '#ffffff'
    """
)