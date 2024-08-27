# Author: Daniel Benjamin Perez Morales
# GitHub: https://github.com/DanielPerezMoralesDev13
# Email: danielperezdev@proton.me

from typing import Dict, Any
from toml import loads

doom_one: Dict[str, Any] = loads(s = """\
    # Colors (Doom One)

    # Default colors
    [colors.primary]
    background = '#282c34'
    foreground = '#bbc2cf'

    # Normal colors
    [colors.normal]
    black   = '#282c34'
    red     = '#ff6c6b'
    green   = '#98be65'
    yellow  = '#ecbe7b'
    blue    = '#51afef'
    magenta = '#c678dd'
    cyan    = '#46d9ff'
    white   = '#bbc2cf'
    """
)