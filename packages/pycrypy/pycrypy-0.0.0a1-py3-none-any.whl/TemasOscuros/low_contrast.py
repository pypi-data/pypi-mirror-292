# Author: Daniel Benjamin Perez Morales
# GitHub: https://github.com/DanielPerezMoralesDev13
# Email: danielperezdev@proton.me

from typing import Dict, Any
from toml import loads

low_contrast: Dict[str, Any] = loads(s = """\
    # Colors (Dim)

    # Default colors
    [colors.primary]
    background = '#333333'
    foreground = '#dddddd'

    [colors.cursor]
    text = '#aaaaaa'
    cursor = '#ffffff'

    # Normal colors
    [colors.normal]
    black   = '#000000'
    red     = '#bb0000'
    green   = '#00bb00'
    yellow  = '#bbbb00'
    blue    = '#0000bb'
    magenta = '#bb00bb'
    cyan    = '#00bbbb'
    white   = '#bbbbbb'

    # Bright colors
    [colors.bright]
    black   = '#000000'
    red     = '#bb0000'
    green   = '#00bb00'
    yellow  = '#bbbb00'
    blue    = '#0000bb'
    magenta = '#bb00bb'
    cyan    = '#00bbbb'
    white   = '#bbbbbb'
    """
)