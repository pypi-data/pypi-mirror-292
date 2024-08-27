# Author: Daniel Benjamin Perez Morales
# GitHub: https://github.com/DanielPerezMoralesDev13
# Email: danielperezdev@proton.me

from typing import Dict, Any
from toml import loads

base16_default_dark: Dict[str, Any] = loads(s = """\
    # Colors (Base16 Default Dark)

    # Default colors
    [colors.primary]
    background = '#181818'
    foreground = '#d8d8d8'

    [colors.cursor]
    text = '#181818'
    cursor = '#d8d8d8'

    # Normal colors
    [colors.normal]
    black   = '#181818'
    red     = '#ab4642'
    green   = '#a1b56c'
    yellow  = '#f7ca88'
    blue    = '#7cafc2'
    magenta = '#ba8baf'
    cyan    = '#86c1b9'
    white   = '#d8d8d8'

    # Bright colors
    [colors.bright]
    black   = '#585858'
    red     = '#ab4642'
    green   = '#a1b56c'
    yellow  = '#f7ca88'
    blue    = '#7cafc2'
    magenta = '#ba8baf'
    cyan    = '#86c1b9'
    white   = '#f8f8f8'
    """
)