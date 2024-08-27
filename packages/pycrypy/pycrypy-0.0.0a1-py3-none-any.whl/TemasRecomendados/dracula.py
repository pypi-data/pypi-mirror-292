# Author: Daniel Benjamin Perez Morales
# GitHub: https://github.com/DanielPerezMoralesDev13
# Email: danielperezdev@proton.me

from typing import Dict, Any
from toml import loads

dracula: Dict[str, Any] = loads(s = """\
    # Colors (Dracula)

    # Default colors
    [colors.primary]
    background = '#282a36'
    foreground = '#f8f8f2'

    # Normal colors
    [colors.normal]
    black   = '#000000'
    red     = '#ff5555'
    green   = '#50fa7b'
    yellow  = '#f1fa8c'
    blue    = '#bd93f9'
    magenta = '#ff79c6'
    cyan    = '#8be9fd'
    white   = '#bbbbbb'

    # Bright colors
    [colors.bright]
    black   = '#555555'
    red     = '#ff5555'
    green   = '#50fa7b'
    yellow  = '#f1fa8c'
    blue    = '#caa9fa'
    magenta = '#ff79c6'
    cyan    = '#8be9fd'
    white   = '#ffffff'
    """
)