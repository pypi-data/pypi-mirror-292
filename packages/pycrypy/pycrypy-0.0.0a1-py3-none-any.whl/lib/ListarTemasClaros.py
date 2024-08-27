#!/usr/bin/env python3

# Author: Daniel Benjamin Perez Morales
# GitHub: https://github.com/DanielPerezMoralesDev13
# Email: danielperezdev@proton.me

from sys import stdout
from prettytable import PrettyTable
from typing import List, Tuple
from lib.FormatColorAnsi import bold, italic

# Lista de temas claros recomendados con descripciones
temasClaros: List[Tuple[str, ...]] = [
    ("alabaster", "Un tema claro con un fondo limpio y minimalista."),
    ("ashes_light", "Un tema claro con tonos suaves y contrastes bajos."),
    ("atom_one_light", "Un tema claro con colores brillantes y acentuados."),
    ("ayu_light", "Un tema claro con un tono suave y colores suaves."),
    ("catppuccin_latte", "Un tema claro con colores inspirados en el café con leche."),
    ("enfocado_light", "Un tema claro con un enfoque en la legibilidad y el contraste."),
    ("everforest_light", "Un tema claro con tonos verdes suaves y un ambiente natural."),
    ("github_light_colorblind", "Un tema claro diseñado para ser accesible para personas con deficiencia de color."),
    ("github_light_default", "El tema claro predeterminado de GitHub."),
    ("github_light_high_contrast", "Un tema claro de GitHub con alto contraste."),
    ("github_light", "Un tema claro basado en el estilo de GitHub."),
    ("github_light_tritanopia", "Un tema claro de GitHub diseñado para personas con deficiencia de visión de color."),
    ("gruvbox_light", "Un tema claro con un estilo retro y colores suaves."),
    ("gruvbox_material_hard_light", "Un tema claro con un estilo material y colores duros."),
    ("gruvbox_material_medium_light", "Un tema claro con un estilo material y colores medios."),
    ("high_contrast", "Un tema claro con un alto contraste para mejorar la legibilidad."),
    ("msx", "Un tema claro con colores inspirados en la estética de los sistemas MSX."),
    ("night_owlish_light", "Un tema claro con tonos inspirados en la noche."),
    ("noctis_lux", "Un tema claro con un diseño elegante y colores suaves."),
    ("nord_light", "Un tema claro inspirado en el esquema de colores Nord con tonos suaves."),
    ("papercolor_light", "Un tema claro con un fondo de color papel y colores suaves."),
    ("papertheme", "Un tema claro con un fondo de color papel y una paleta de colores minimalista."),
    ("pencil_light", "Un tema claro con colores inspirados en lápices y tonos suaves."),
    ("rose_pine_dawn", "Un tema claro con tonos suaves inspirados en el amanecer."),
    ("solarized_light", "Un tema claro basado en el esquema de colores Solarized con tonos suaves.")
]

# Listar temas light: Abreviado: ltl
async def ltl() -> None:
    """
    ### Esta función lista los temas claros recomendados para Alacritty
    - Ejemplo:
    
    ```python
    ltl()
    ```
    """
    # Crear la tabla
    tabla: PrettyTable = PrettyTable()
    tabla.field_names = [f"{bold(t = 'Nombre del Tema', c = 'verde')}", f"{bold(t = 'Descripción', c = 'verde')}"] 

    # Añadir filas a la tabla
    for tema, descripcion in temasClaros:
        tabla.add_row(row = [f"{italic(t = tema, c = 'cyan')}", f"{italic(t = descripcion, c = 'azul')}"], divider = False) 
    
    # Imprimir la tabla
    print(tabla, end="\n", file = stdout)

    return None
