# Author: Daniel Benjamin Perez Morales
# GitHub: https://github.com/DanielPerezMoralesDev13
# Email: danielperezdev@proton.me

from typing import Dict, Any
from toml import loads
                         
monokai_inspired: Dict[str, Any] = loads(s = """\
    # Themes Colors (monokai-inspired)

    # Default colors monokai-inspired
    [colors.primary]
    background = '#171714'
    foreground = '#f8f8f2'

    # Normal colors monokai-inspired
    [colors.normal]
    black = '#272822'
    red = '#f92672'
    green = '#a6e22e'
    yellow = '#f4bf75'
    blue = '#66d9ef'
    magenta = '#ae81ff'
    cyan = '#a1efe4'
    white = '#f8f8f2'

    # Bright colors monokai-inspired
    [colors.bright]
    black = '#75715e'
    red = '#f92672'
    green = '#a6e22e'
    yellow = '#f4bf75'
    blue = '#66d9ef'
    magenta = '#ae81ff'
    cyan = '#a1efe4'
    white = '#f9f8f5'
    """
)