# Author: Daniel Benjamin Perez Morales
# GitHub: https://github.com/DanielPerezMoralesDev13
# Email: danielperezdev@proton.me

from typing import Dict, Any
from toml import loads

cyber_punk_neon: Dict[str, Any] = loads(s = """\
    # Cyber Punk Neon
    # Source https//github.com/Roboron3042/Cyberpunk-Neon

    # Default colors
    [colors.primary]
    background = '#000b1e'
    foreground = '#0abdc6'

    [colors.cursor]
    text   = '#000b1e'
    cursor = '#0abdc6'

    # Normal colors
    [colors.normal]
    black   = '#123e7c'
    red     = '#ff0000'
    green   = '#d300c4'
    yellow  = '#f57800'
    blue    = '#123e7c'
    magenta = '#711c91'
    cyan    = '#0abdc6'
    white   = '#d7d7d5'

    # Bright colors
    [colors.bright]
    black   = '#1c61c2'
    red     = '#ff0000'
    green   = '#d300c4'
    yellow  = '#f57800'
    blue    = '#00ff00'
    magenta = '#711c91'
    cyan    = '#0abdc6'
    white   = '#d7d7d5'
    """
)