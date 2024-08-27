# Author: Daniel Benjamin Perez Morales
# GitHub: https://github.com/DanielPerezMoralesDev13
# Email: danielperezdev@proton.me

from typing import Dict, Any
from toml import loads

papertheme: Dict[str, Any] = loads(s = """\
    # Colors (Paper Theme)

    # Default colors
    [colors.primary]
    background = '#F2EEDE'
    foreground = '#000000'

    # Normal colors
    [colors.normal]
    black   = '#000000'
    red     = '#CC3E28'
    green   = '#216609'
    yellow  = '#B58900'
    blue    = '#1E6FCC'
    magenta = '#5C21A5'
    cyan    = '#158C86'
    white   = '#AAAAAA'

    # Bright colors
    [colors.bright]
    black   = '#555555'
    red     = '#CC3E28'
    green   = '#216609'
    yellow  = '#B58900'
    blue    = '#1E6FCC'
    magenta = '#5C21A5'
    cyan    = '#158C86'
    white   = '#AAAAAA'
    """
)