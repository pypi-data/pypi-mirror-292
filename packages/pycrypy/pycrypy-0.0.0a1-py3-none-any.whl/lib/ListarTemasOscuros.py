#!/usr/bin/env python3

# Author: Daniel Benjamin Perez Morales
# GitHub: https://github.com/DanielPerezMoralesDev13
# Email: danielperezdev@proton.me

from sys import stdout
from prettytable import PrettyTable
from typing import List, Tuple

from lib.FormatColorAnsi import bold, italic

temasOscuros: List[Tuple[str, ...]] = [
    ("afterglow", "Tema oscuro con tonos cálidos que imitan el resplandor del atardecer."),
    ("alacritty_0_12", "Tema específico para la versión 0.12 de Alacritty, con colores oscuros y contrastantes."),
    ("ashes_dark", "Tema oscuro con una paleta de grises y tonos apagados."),
    ("base16_default_dark", "Tema oscuro basado en la paleta Base16 con un diseño limpio."),
    ("bluish", "Tema oscuro con tonos azules profundos y contrastantes."),
    ("breeze", "Tema oscuro basado en el estilo Breeze con colores suaves."),
    ("catppuccin_frappe", "Variante del tema Catppuccin con un estilo frappé, suave y oscuro."),
    ("catppuccin_macchiato", "Variante del tema Catppuccin con un estilo macchiato, suave y oscuro."),
    ("catppuccin_mocha", "Variante del tema Catppuccin con un estilo mocha, suave y oscuro."),
    ("chicago95", "Tema inspirado en los colores del sistema operativo Chicago 95."),
    ("citylights", "Tema oscuro con colores inspirados en las luces de la ciudad de noche."),
    ("Cobalt2", "Tema oscuro con un esquema de colores azul profundo y contrastante."),
    ("dark_pastels", "Tema oscuro con colores pastel apagados."),
    ("deep_space", "Tema oscuro inspirado en los colores del espacio profundo."),
    ("doom_one", "Tema oscuro con un estilo inspirado en Doom, con colores intensos."),
    ("dracula_plus", "Variante del tema Dracula con ajustes adicionales para un estilo más oscuro."),
    ("enfocado_dark", "Tema oscuro con un enfoque en la legibilidad y el contraste."),
    ("everforest_dark", "Tema oscuro con una paleta verde y madera oscura."),
    ("falcon", "Tema oscuro con tonos metálicos y un estilo agresivo."),
    ("flat_remix", "Tema oscuro con un diseño plano y moderno."),
    ("flexoki", "Tema oscuro con una paleta flexible y contrastante."),
    ("github_dark_dimmed", "Tema oscuro de GitHub con colores ligeramente atenuados."),
    ("github_dark", "Tema oscuro de GitHub con colores contrastantes y modernos."),
    ("gnome_terminal", "Tema oscuro inspirado en el terminal GNOME."),
    ("google", "Tema oscuro inspirado en los colores oscuros del diseño de Google."),
    ("gruvbox_dark", "Tema oscuro basado en el esquema de colores Gruvbox con alto contraste."),
    ("gruvbox_material_hard_dark", "Variante del tema Gruvbox con un estilo más oscuro y contrastante."),
    ("gruvbox_material_medium_dark", "Variante del tema Gruvbox con un estilo oscuro pero menos intenso."),
    ("gruvbox_material", "Tema Gruvbox Material con colores oscuros y cómodos."),
    ("hardhacker", "Tema oscuro con un diseño agresivo y moderno."),
    ("hatsunemiku", "Tema oscuro inspirado en el personaje Hatsune Miku con colores vibrantes."),
    ("horizon_dark", "Tema oscuro con una paleta de colores inspirada en el horizonte nocturno."),
    ("inferno", "Tema oscuro con tonos cálidos inspirados en el fuego y la lava."),
    ("iris", "Tema oscuro con colores morados y suaves."),
    ("kanagawa_dragon", "Tema oscuro inspirado en la mitología japonesa con tonos oscuros y vibrantes."),
    ("kanagawa_wave", "Tema oscuro inspirado en las olas japonesas con colores intensos."),
    ("konsole_linux", "Tema oscuro basado en el terminal Konsole de Linux."),
    ("low_contrast", "Tema oscuro con bajo contraste para una experiencia más suave."),
    ("Mariana", "Tema oscuro con una paleta inspirada en la profundidad del océano Mariana."),
    ("marine_dark", "Tema oscuro con colores marinos y profundos."),
    ("material_theme", "Tema oscuro basado en el estilo Material Design."),
    ("meliora", "Tema oscuro con colores oscuros y cálidos."),
    ("monokai_pro", "Variante del clásico tema Monokai con un estilo moderno."),
    ("monokai", "Tema oscuro clásico con colores vibrantes y contraste alto."),
    ("moonlight_ii_vscode", "Tema oscuro con una paleta de colores inspirada en la luz de la luna."),
    ("nightfox", "Tema oscuro con una paleta inspirada en la noche y los zorros."),
    ("nord", "Tema oscuro basado en el estilo nordic con colores fríos y suaves."),
    ("one_dark", "Tema oscuro inspirado en el tema One Dark."),
    ("papercolor_dark", "Tema oscuro con colores de papel y diseño suave."),
    ("pencil_dark", "Tema oscuro con un esquema de colores inspirados en lápices."),
    ("rainbow", "Tema oscuro con una paleta de colores inspirada en el arcoíris."),
    ("remedy_dark", "Tema oscuro con colores que ayudan a reducir la fatiga ocular."),
    ("rose_pine_moon", "Tema oscuro con tonos suaves y de luna inspirados en Rose Pine."),
    ("seashells", "Tema oscuro con una paleta inspirada en las conchas marinas."),
    ("smoooooth", "Tema oscuro con una paleta de colores suaves y relajantes."),
    ("snazzy", "Tema oscuro con colores vibrantes y un estilo llamativo."),
    ("solarized_dark", "Tema oscuro basado en el esquema de colores Solarized."),
    ("solarized_osaka", "Variante del tema Solarized con una paleta inspirada en Osaka."),
    ("taerminal", "Tema oscuro con un estilo moderno y contrastante."),
    ("tango_dark", "Tema oscuro basado en el estilo Tango con colores intensos."),
    ("tender", "Tema oscuro con una paleta de colores suaves y agradables."),
    ("terminal_app", "Tema oscuro con un diseño enfocado en la usabilidad."),
    ("tomorrow_night_bright", "Tema oscuro con colores brillantes inspirados en la noche."),
    ("tomorrow_night", "Tema oscuro con colores inspirados en la noche y el amanecer."),
    ("ubuntu", "Tema oscuro inspirado en el diseño de Ubuntu."),
    ("vesper", "Tema oscuro con una paleta inspirada en la calma de la tarde."),
    ("wombat", "Tema oscuro con colores intensos y un estilo agresivo."),
    ("zenburn", "Tema oscuro con colores apagados y un estilo relajante.")
]

# Listar temas dark: Abreviado: ltd
async def ltd() -> None:
    """
    ### Esta función lista los temas oscuros recomendados para Alacritty
    - Ejemplo:
    
    ```python
    ltd()
    ```
    """
    # Crear la tabla
    tabla: PrettyTable = PrettyTable()
    tabla.field_names = [f"{bold(t = 'Nombre del Tema', c = 'verde')}", f"{bold(t = 'Descripción', c = 'verde')}"] 

    # Añadir filas a la tabla
    for tema, descripcion in temasOscuros:
        tabla.add_row(row = [f"{italic(t = tema, c = 'cyan')}", f"{italic(t = descripcion, c = 'azul')}"], divider = False) 
    
    # Imprimir la tabla
    print(tabla, end="\n", file = stdout)

    return None
