# Author: Daniel Benjamin Perez Morales
# GitHub: https://github.com/DanielPerezMoralesDev13
# Email: danielperezdev@proton.me

from typing import Dict, Any
from toml import loads

hatsunemiku: Dict[str, Any] = loads(s = """\
    [colors.primary]
    background = '#242829'
    foreground = '#dcd7d7'

    [colors.normal]
    black   = '#242829'
    red     = '#df2683'
    green   = '#13868c'
    yellow  = '#fcfcdf'
    blue    = '#1a86b9'
    magenta = '#bc7fd2'
    cyan    = '#7cc7d6'
    white   = '#4a4b4b'

    [colors.bright]
    black   = '#7b8b99'
    red     = '#df2683'
    green   = '#13868c'
    yellow  = '#fcfcdf'
    blue    = '#1a86b9'
    magenta = '#bc7fd2'
    cyan    = '#7cc7d6'
    white   = '#dcd7d7'
    """
)