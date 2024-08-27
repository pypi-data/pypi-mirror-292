# Author: Daniel Benjamin Perez Morales
# GitHub: https://github.com/DanielPerezMoralesDev13
# Email: danielperezdev@proton.me

from typing import Dict, Any
from toml import loads

google: Dict[str, Any] = loads(s = """\
    [colors.primary]
    background = '#1d1f21'
    foreground = '#c5c8c6'

    [colors.normal]
    black   = '#1d1f21'
    red     = '#cc342b'
    green   = '#198844'
    yellow  = '#fba922'
    blue    = '#3971ed'
    magenta = '#a36ac7'
    cyan    = '#3971ed'
    white   = '#c5c8c6'

    [colors.bright]
    black   = '#969896'
    red     = '#cc342b'
    green   = '#198844'
    yellow  = '#fba922'
    blue    = '#3971ed'
    magenta = '#a36ac7'
    cyan    = '#3971ed'
    white   = '#ffffff'
    """
)