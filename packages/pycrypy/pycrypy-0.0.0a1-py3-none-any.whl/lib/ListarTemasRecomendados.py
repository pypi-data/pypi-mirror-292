#!/usr/bin/env python3

# Author: Daniel Benjamin Perez Morales
# GitHub: https://github.com/DanielPerezMoralesDev13
# Email: danielperezdev@proton.me

from sys import stdout
from prettytable import PrettyTable
from typing import List, Tuple

from lib.FormatColorAnsi import bold, italic

temasRecomendados: List[Tuple[str, ...]] = [
    ("alabaster_dark", "Tema oscuro con un estilo elegante y minimalista."),
    ("argonaut", "Tema con colores vibrantes y un fondo oscuro."),
    ("aura", "Tema con una paleta de colores suave y moderna."),
    ("ayu_dark", "Tema oscuro con acentos azulados y verdes."),
    ("ayu_mirage", "Variación del tema Ayu con un estilo único."),
    ("baitong", "Tema oscuro con un contraste alto."),
    ("blood_moon", "Tema con tonos rojos y oscur"),
    ("bluescreen", "Inspirado en las pantallas azules de error."),
    ("campbell", "Tema basado en los colores del logo de Campbell."),
    ("carbonfox", "Tema oscuro con tonos de carbón."),
    ("catppuccin", "Tema suave y acogedor con un estilo pastel."),
    ("challenger_deep", "Tema con un esquema de colores profundos y oscur"),
    ("cyber_punk_neon", "Tema con colores neón y un estilo cyberpunk."),
    ("dark_pride", "Tema oscuro con acentos en tonos de orgullo."),
    ("dracula_inspired", "Inspirado en el popular tema Dracula."),
    ("dracula", "Tema oscuro con una paleta rica y contrastante."),
    ("github_dark_colorblind", "Versión del tema GitHub para personas con daltonismo."),
    ("github_dark_default", "Tema oscuro predeterminado de GitHub."),
    ("github_dark_high_contrast", "Versión de alto contraste del tema GitHub oscuro."),
    ("github_dark_tritanopia", "Adaptación para tritanopía del tema GitHub."),
    ("gotham", "Tema con un estilo urbano y moderno."),
    ("greenscreen", "Tema con un fondo verde vibrante."),
    ("hyper", "Tema inspirado en el terminal Hyper."),
    ("iterm", "Tema basado en los colores del terminal iTerm."),
    ("material_darker", "Variante oscura del tema Material."),
    ("material_ocean", "Tema inspirado en la estética de Material Ocean."),
    ("material_theme_mod", "Modificación del tema Material Theme."),
    ("midnight_haze", "Tema con un fondo oscuro y brumoso."),
    ("monokai_charcoal", "Variante del tema Monokai con tonos carbón."),
    ("monokai_inspired", "Inspirado en el clásico tema Monokai."),
    ("nightfly", "Tema con un estilo nocturno y profundo."),
    ("night_owl", "Tema oscuro con acentos en tonos de azul."),
    ("nordic", "Tema inspirado en los colores del norte."),
    ("nord_inspired", "Inspirado en el tema Nordic con ajustes."),
    ("nord_wave", "Variante del tema Nordic con un toque de ola."),
    ("oceanic_next", "Tema con un esquema de colores oceánic"),
    ("omni", "Tema con una paleta de colores dinámica."),
    ("onedark_inspired", "Inspirado en el tema One Dark."),
    ("palenight", "Tema con un estilo nocturno y relajado."),
    ("pastel_dark", "Tema oscuro con colores pastel."),
    ("rosepine_inspired", "Inspirado en el tema Rose Pine."),
    ("rose_pine", "Tema con una paleta de colores rosados y pin"),
    ("thelovelace", "Tema con un estilo romántico y cálido."),
    ("tokyo_night", "Tema inspirado en la noche de Tokio."),
    ("tokyo_night_storm", "Variante del tema Tokyo Night con un toque tormentoso."),
    ("xterm", "Tema inspirado en el estilo clásico de xterm.")
]


# Listar temas recomendados: Abreviado: ltr
async def ltr() -> None:
    """
    ### Esta función lista los temas recomendados para Alacritty
    - Ejemplo:
    
    ```python
    ltr()
    ```
    """
    # Crear la tabla
    tabla: PrettyTable = PrettyTable()
    tabla.field_names = [f"{bold(t = 'Nombre del Tema', c = 'verde')}", f"{bold(t = 'Descripción', c = 'verde')}"] 

    # Añadir filas a la tabla
    for tema, descripcion in temasRecomendados:
        tabla.add_row(row = [f"{italic(t = tema, c = 'cyan')}", f"{italic(t = descripcion, c = 'azul')}"], divider = False) 
    
    # Imprimir la tabla
    print(tabla, end="\n", file = stdout)
    
    return None
