# Author: Daniel Benjamin Perez Morales
# GitHub: https://github.com/DanielPerezMoralesDev13
# Email: danielperezdev@proton.me

from typing import Dict, Any
from toml import loads

aura: Dict[str, Any] = loads(s = """\
    [colors.primary]
    background = "#15141b"
    foreground = "#edecee"

    [colors.cursor]
    cursor = "#a277ff"

    [colors.selection]
    text = "CellForeground"
    background = "#29263c"

    [colors.normal]
    black = "#110f18"
    red = "#ff6767"
    green = "#61ffca"
    yellow = "#ffca85"
    blue = "#a277ff"
    magenta = "#a277ff"
    cyan = "#61ffca"
    white = "#edecee"

    [colors.bright]
    black = "#4d4d4d"
    red = "#ff6767"
    green = "#61ffca"
    yellow = "#ffca85"
    blue = "#a277ff"
    magenta = "#a277ff"
    cyan = "#61ffca"
    white = "#edecee"
    """
)