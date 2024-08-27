# Author: Daniel Benjamin Perez Morales
# GitHub: https://github.com/DanielPerezMoralesDev13
# Email: danielperezdev@proton.me

from typing import Dict, Any
from toml import loads

nightfox: Dict[str, Any] = loads(s = """\
    # Colors (NightFox)

    # Default colors
    [colors.primary]
    background = '#192330'
    foreground = '#cdcecf'

    # Normal colors
    [colors.normal]
    black   = '#393b44'
    red     = '#c94f6d'
    green   = '#81b29a'
    yellow  = '#dbc074'
    blue    = '#719cd6'
    magenta = '#9d79d6'
    cyan    = '#63cdcf'
    white   = '#dfdfe0'

    # Bright colors
    [colors.bright]
    black   = '#575860'
    red     = '#d16983'
    green   = '#8ebaa4'
    yellow  = '#e0c989'
    blue    = '#86abdc'
    magenta = '#baa1e2'
    cyan    = '#7ad5d6'
    white   = '#e4e4e5'
    """
)