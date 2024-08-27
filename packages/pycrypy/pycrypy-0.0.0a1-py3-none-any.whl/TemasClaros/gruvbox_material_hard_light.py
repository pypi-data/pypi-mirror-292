# Author: Daniel Benjamin Perez Morales
# GitHub: https://github.com/DanielPerezMoralesDev13
# Email: danielperezdev@proton.me

from typing import Dict, Any
from toml import loads

gruvbox_material_hard_light: Dict[str, Any] = loads(s = """\
    # Colors (Gruvbox Material Hard Light)

    # Default colors
    [colors.primary]
    background = '#f9f5d7'
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
    white   = '#f2e5bc'

    # Bright colors (same as normal colors)
    [colors.bright]
    black   = '#654735'
    red     = '#c14a4a'
    green   = '#6c782e'
    yellow  = '#b47109'
    blue    = '#45707a'
    magenta = '#945e80'
    cyan    = '#4c7a5d'
    white   = '#f2e5bc'
    """
)
