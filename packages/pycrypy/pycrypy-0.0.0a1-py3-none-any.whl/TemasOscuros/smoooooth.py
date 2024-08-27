# Author: Daniel Benjamin Perez Morales
# GitHub: https://github.com/DanielPerezMoralesDev13
# Email: danielperezdev@proton.me

from typing import Dict, Any
from toml import loads

smoooooth: Dict[str, Any] = loads(s = """\
    # Color theme ported from iTerm 2 Smoooooth

    [colors.primary]
    foreground = '#dbdbdb'
    background = '#14191e'

    [colors.cursor]
    text = '#000000'
    cursor = '#fefffe'

    [colors.selection]
    text = '#000000'
    background = '#b3d7ff'

    [colors.normal]
    black   = '#14191e'
    red     = '#b43c29'
    green   = '#00c200'
    yellow  = '#c7c400'
    blue    = '#2743c7'
    magenta = '#bf3fbd'
    cyan    = '#00c5c7'
    white   = '#c7c7c7'

    [colors.bright]
    black   = '#676767'
    red     = '#dc7974'
    green   = '#57e690'
    yellow  = '#ece100'
    blue    = '#a6aaf1'
    magenta = '#e07de0'
    cyan    = '#5ffdff'
    white   = '#feffff'
    """
)