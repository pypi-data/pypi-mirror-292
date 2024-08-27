# Author: Daniel Benjamin Perez Morales
# GitHub: https://github.com/DanielPerezMoralesDev13
# Email: danielperezdev@proton.me

from typing import Dict, Any
from toml import loads

gruvbox_material_medium_light: Dict[str, Any] = loads(s = """\
    # Colors (Gruvbox Material Medium Light)

    # Default colors
    [colors.primary]
    background = '#fbf1c7'
    foreground = '#654735'

    # Normal colors
    [colors.normal]
    black   = '#654735'
    red     = '#c14a4a'
    green   = '#6c782e'
    yellow  = '#b47109'
    blue    = '#45707a'
    magenta = '#945e80'
    cyan    = '#4c7a5d'
    white   = '#eee0b7'

    # Bright colors (same as normal colors)
    [colors.bright]
    black   = '#654735'
    red     = '#c14a4a'
    green   = '#6c782e'
    yellow  = '#b47109'
    blue    = '#45707a'
    magenta = '#945e80'
    cyan    = '#4c7a5d'
    white   = '#eee0b7'
    """
)