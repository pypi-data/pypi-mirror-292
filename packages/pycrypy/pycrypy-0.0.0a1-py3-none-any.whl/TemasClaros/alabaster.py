# Colors (Alabaster)
# author tonsky

# Author: Daniel Benjamin Perez Morales
# GitHub: https://github.com/DanielPerezMoralesDev13
# Email: danielperezdev@proton.me

from typing import Dict, Any
from toml import loads

alabaster: Dict[str, Any] = loads(s = """\
    [colors.primary]
    background = '#F7F7F7'
    foreground = '#434343'

    [colors.cursor]
    text = '#F7F7F7'
    cursor = '#434343'

    [colors.normal]
    black = '#000000'
    red = '#AA3731'
    green = '#448C27'
    yellow = '#CB9000'
    blue = '#325CC0'
    magenta = '#7A3E9D'
    cyan = '#0083B2'
    white = '#BBBBBB'

    [colors.bright]
    black = '#777777'
    red = '#F05050'
    green = '#60CB00'
    yellow = '#FFBC5D'
    blue = '#007ACC'
    magenta = '#E64CE6'
    cyan = '#00AACB'
    white = '#FFFFFF'
    """
)