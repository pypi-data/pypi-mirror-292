# Author: Daniel Benjamin Perez Morales
# GitHub: https://github.com/DanielPerezMoralesDev13
# Email: danielperezdev@proton.me

from typing import Dict, Any
from toml import loads

nord: Dict[str, Any] = loads(s = """\
    # Colors (Nord)

    # Default colors
    [colors.primary]
    background = '#2E3440'
    foreground = '#D8DEE9'

    # Normal colors
    [colors.normal]
    black   = '#3B4252'
    red     = '#BF616A'
    green   = '#A3BE8C'
    yellow  = '#EBCB8B'
    blue    = '#81A1C1'
    magenta = '#B48EAD'
    cyan    = '#88C0D0'
    white   = '#E5E9F0'

    # Bright colors
    [colors.bright]
    black   = '#4C566A'
    red     = '#BF616A'
    green   = '#A3BE8C'
    yellow  = '#EBCB8B'
    blue    = '#81A1C1'
    magenta = '#B48EAD'
    cyan    = '#8FBCBB'
    white   = '#ECEFF4'
    """
)
