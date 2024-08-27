# Author: Daniel Benjamin Perez Morales
# GitHub: https://github.com/DanielPerezMoralesDev13
# Email: danielperezdev@proton.me

from typing import Dict, Any
from toml import loads

atom_one_light: Dict[str, Any] = loads(s = """\
    [colors.primary]
    background = '#f8f8f8'
    foreground = '#2a2b33'

    [colors.normal]
    black   = '#000000'
    red     = '#de3d35'
    green   = '#3e953a'
    yellow  = '#d2b67b'
    blue    = '#2f5af3'
    magenta = '#a00095'
    cyan    = '#3e953a'
    white   = '#bbbbbb'

    [colors.bright]
    black   = '#000000'
    red     = '#de3d35'
    green   = '#3e953a'
    yellow  = '#d2b67b'
    blue    = '#2f5af3'
    magenta = '#a00095'
    cyan    = '#3e953a'
    white   = '#ffffff'
    """
)