# Author: Daniel Benjamin Perez Morales
# GitHub: https://github.com/DanielPerezMoralesDev13
# Email: danielperezdev@proton.me

from typing import Dict, Any
from toml import loads

monokai_pro: Dict[str, Any] = loads(s = """\
    # Default colors
    [colors.primary]
    background = '#2D2A2E'
    foreground = '#fff1f3'

    # Normal colors
    [colors.normal]
    black   = '#2c2525'
    red     = '#fd6883'
    green   = '#adda78'
    yellow  = '#f9cc6c'
    blue    = '#f38d70'
    magenta = '#a8a9eb'
    cyan    = '#85dacc'
    white   = '#fff1f3'

    # Bright colors
    [colors.bright]
    black   = '#72696a'
    red     = '#fd6883'
    green   = '#adda78'
    yellow  = '#f9cc6c'
    blue    = '#f38d70'
    magenta = '#a8a9eb'
    cyan    = '#85dacc'
    white   = '#fff1f3'
    """
)