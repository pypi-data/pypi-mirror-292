# Author: Daniel Benjamin Perez Morales
# GitHub: https://github.com/DanielPerezMoralesDev13
# Email: danielperezdev@proton.me

from typing import Dict, Any
from toml import loads

gruvbox_material: Dict[str, Any] = loads(s = """\
    # Colors (Gruvbox Material Dark Medium)

    [colors.primary]
    background = '#282828'
    foreground = '#dfbf8e'

    [colors.normal]
    black   = '#665c54'
    red     = '#ea6962'
    green   = '#a9b665'
    yellow  = '#e78a4e'
    blue    = '#7daea3'
    magenta = '#d3869b'
    cyan    = '#89b482'
    white   = '#dfbf8e'

    [colors.bright]
    black   = '#928374'
    red     = '#ea6962'
    green   = '#a9b665'
    yellow  = '#e3a84e'
    blue    = '#7daea3'
    magenta = '#d3869b'
    cyan    = '#89b482'
    white   = '#dfbf8e'
    """
)