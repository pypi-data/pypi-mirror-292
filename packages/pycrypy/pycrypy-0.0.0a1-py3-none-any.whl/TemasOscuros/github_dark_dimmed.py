# Author: Daniel Benjamin Perez Morales
# GitHub: https://github.com/DanielPerezMoralesDev13
# Email: danielperezdev@proton.me

from typing import Dict, Any
from toml import loads

github_dark_dimmed: Dict[str, Any] = loads(s = """\
    # github Alacritty Colors

    # Default colors
    [colors.primary]
    background = '#22272e'
    foreground = '#768390'

    # Normal colors
    [colors.normal]
    black   = '#545d68'
    red     = '#f47067'
    green   = '#57ab5a'
    yellow  = '#c69026'
    blue    = '#539bf5'
    magenta = '#b083f0'
    cyan    = '#39c5cf'
    white   = '#909dab'

    # Bright colors
    [colors.bright]
    black   = '#636e7b'
    red     = '#ff938a'
    green   = '#6bc46d'
    yellow  = '#daaa3f'
    blue    = '#6cb6ff'
    magenta = '#dcbdfb'
    cyan    = '#56d4dd'
    white   = '#cdd9e5'

    [[colors.indexed_colors]]
    index = 16
    color = '#d18616'

    [[colors.indexed_colors]]
    index = 17
    color = '#ff938a'
    """
)