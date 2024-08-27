# Author: Daniel Benjamin Perez Morales
# GitHub: https://github.com/DanielPerezMoralesDev13
# Email: danielperezdev@proton.me

from typing import Dict, Any
from toml import loads

gruvbox_material_hard_dark: Dict[str, Any] = loads(s = """\
    # Colors (Gruvbox Material Hard Dark)

    # Default colors
    [colors.primary]
    background = '#1d2021'
    foreground = '#d4be98'

    # Normal colors
    [colors.normal]
    black   = '#32302f'
    red     = '#ea6962'
    green   = '#a9b665'
    yellow  = '#d8a657'
    blue    = '#7daea3'
    magenta = '#d3869b'
    cyan    = '#89b482'
    white   = '#d4be98'

    # Bright colors (same as normal colors)
    [colors.bright]
    black   = '#32302f'
    red     = '#ea6962'
    green   = '#a9b665'
    yellow  = '#d8a657'
    blue    = '#7daea3'
    magenta = '#d3869b'
    cyan    = '#89b482'
    white   = '#d4be98'
    """
)