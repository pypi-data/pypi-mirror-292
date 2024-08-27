#!/usr/bin/env python3

# Author: Daniel Benjamin Perez Morales
# GitHub: https://github.com/DanielPerezMoralesDev13
# Email: danielperezdev@proton.me

from os.path import join, expanduser
from pathlib import Path
from typing import List

from lib.FormatColorAnsi import bold, italic

# Verificar si el directorio existe el fichero alcritty.toml
# Verficar Si Directorio Existe -> Abreviado: vsde
async def vsde(l: List[str]) -> None:
    ruta: Path = Path(rutaDirectorioConfig)
    if not ruta.exists():
        ruta.mkdir(parents = True, exist_ok = True)
        l.append(f"{bold(t = 'Directorio creado: ', c = 'verde')}{italic(t = rutaDirectorioConfig, c = 'cyan')}")
    
    ruta = Path(rutaDirectorioAlacrittyToml)
    
    if not ruta.exists():
        ruta.mkdir(parents = True, exist_ok = True)
        l.append(f"{bold(t = 'Directorio creado: ', c = 'verde')}{italic(t = rutaDirectorioAlacrittyToml, c = 'cyan')}")
    
    ruta = Path(rutaAlacrittyToml)
    ruta.touch()
    l.append(f"{bold(t = 'Fichero creado: ', c = 'verde')}{italic(t = rutaAlacrittyToml, c = 'cyan')}")
    return None

rutaAlacrittyToml: str = join(expanduser(path = '~'), ".config", "alacritty", "alacritty.toml")
rutaDirectorioConfig: str = join(expanduser(path = '~'), ".config")
rutaDirectorioAlacrittyToml: str = join(expanduser(path = '~'), ".config", "alacritty")
