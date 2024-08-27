#!/usr/bin/env python3

# Author: Daniel Benjamin Perez Morales
# GitHub: https://github.com/DanielPerezMoralesDev13
# Email: danielperezdev@proton.me

from importlib import import_module
from types import ModuleType
from typing import Dict, Any, List
from sys import stderr

# Definimos los nombres de los temas
temasClaros: List[str] = [
    "alabaster", "ashes_light", "atom_one_light", "ayu_light", "catppuccin_latte",
    "enfocado_light", "everforest_light", "github_light_colorblind", "github_light_default",
    "github_light_high_contrast", "github_light", "github_light_tritanopia", "gruvbox_light",
    "gruvbox_material_hard_light", "gruvbox_material_medium_light", "high_contrast", "msx",
    "night_owlish_light", "noctis_lux", "nord_light", "papercolor_light", "papertheme",
    "pencil_light", "rose_pine_dawn", "solarized_light"
]

temasOscuros: List[str] = [
    "afterglow", "alacritty_0_12", "ashes_dark", "base16_default_dark", "bluish",
    "breeze", "catppuccin_frappe", "catppuccin_macchiato", "catppuccin_mocha", "chicago95",
    "citylights", "Cobalt2", "dark_pastels", "deep_space", "doom_one", "dracula_plus",
    "enfocado_dark", "everforest_dark", "falcon", "flat_remix", "flexoki", "github_dark_dimmed",
    "github_dark", "gnome_terminal", "google", "gruvbox_dark", "gruvbox_material_hard_dark",
    "gruvbox_material_medium_dark", "gruvbox_material", "hardhacker", "hatsunemiku", "horizon_dark",
    "inferno", "iris", "kanagawa_dragon", "kanagawa_wave", "konsole_linux", "low_contrast",
    "Mariana", "marine_dark", "material_theme", "meliora", "monokai_pro", "monokai",
    "moonlight_ii_vscode", "nightfox", "nord", "one_dark", "papercolor_dark", "pencil_dark",
    "rainbow", "remedy_dark", "rose_pine_moon", "seashells", "smoooooth", "snazzy", "solarized_dark",
    "solarized_osaka", "taerminal", "tango_dark", "tender", "terminal_app", "tomorrow_night_bright",
    "tomorrow_night", "ubuntu", "vesper", "wombat", "zenburn"
]

temasRecomendados: List[str] = [
    "alabaster_dark", "argonaut", "aura", "ayu_dark", "ayu_mirage", "baitong", "blood_moon",
    "bluescreen", "campbell", "carbonfox", "catppuccin", "challenger_deep", "cyber_punk_neon",
    "dark_pride", "dracula_inspired", "dracula", "github_dark_colorblind", "github_dark_default",
    "github_dark_high_contrast", "github_dark_tritanopia", "gotham", "greenscreen", "hyper",
    "iterm", "material_darker", "material_ocean", "material_theme_mod", "midnight_haze",
    "monokai_charcoal", "monokai_inspired", "nightfly", "night_owl", "nordic", "nord_inspired",
    "nord_wave", "oceanic_next", "omni", "onedark_inspired", "palenight", "pastel_dark",
    "rosepine_inspired", "rose_pine", "thelovelace", "tokyo_night", "tokyo_night_storm", "xterm"
]

async def cargar_temas(*, moduloBase: str, nombresTema: str) -> Dict[str, Any]:
    temasDiccionario: Dict[str, Any] = dict()
    try:
        tema: ModuleType = import_module(name = f"{moduloBase}.{nombresTema}")
        temasDiccionario[nombresTema] = tema
    except ModuleNotFoundError: print(f"El módulo {nombresTema} no se pudo encontrar en {moduloBase}.", end="\n", file = stderr)
    return temasDiccionario

# async def cargar_temas(*, moduloBase: str, nombresTemas: List[str]) -> Dict[str, Any]:
#     """
#     Carga dinámicamente módulos de temas especificados y los almacena en un diccionario.

#     Parámetros:
#     - moduloBase (str): El nombre base del módulo desde donde se cargarán los submódulos de temas.
#     - nombresTemas (List[str]): Una lista de nombres de los temas (submódulos) a cargar.

#     Retorno:
#     - Dict[str, Any]: Un diccionario donde las claves son los nombres de los temas y los valores son los módulos importados.

#     Comportamiento:
#     - Itera sobre la lista de nombres de temas.
#     - Intenta importar cada tema como un submódulo del módulo base.
#     - Si la importación es exitosa, agrega el módulo al diccionario `temasDiccionario` con el nombre del tema como clave.
#     - Si un módulo no se puede encontrar, imprime un mensaje de error en stderr.
#     - Retorna el diccionario con los módulos importados.

#     Ejemplo de uso:
#     - Si se llama a `cargar_temas(moduloBase="temas", nombresTemas=["tema1", "tema2"])`, la función intentará importar `temas.tema1` y `temas.tema2`.
#     """
#     temasDiccionario: Dict[str, Any] = dict()
#     for nombre in nombresTemas:
#         try:
#             tema: ModuleType = import_module(name = f"{moduloBase}.{nombre}")
#             temasDiccionario[nombre] = tema
#         except ModuleNotFoundError: print(f"El módulo {nombre} no se pudo encontrar en {moduloBase}.", end="\n", file = stderr)
#     return temasDiccionario


"""
Para ver el contenido del módulo importado dinámicamente a través del diccionario temasRecomendadosDiccionario, puedes acceder a sus atributos y métodos utilizando la función dir() y luego imprimir los atributos que desees.

print(temasRecomendadosDiccionario.keys())
print(dir(temasRecomendadosDiccionario["onedark_inspired"]))

print(temasRecomendadosDiccionario["onedark_inspired"].onedark_inspired)
"""

"""
from typing import Dict, Any
from TemasClaros.alabaster import alabaster
from TemasClaros.ashes_light import ashes_light
from TemasClaros.atom_one_light import atom_one_light
from TemasClaros.ayu_light import ayu_light
from TemasClaros.catppuccin_latte import catppuccin_latte
from TemasClaros.enfocado_light import enfocado_light
from TemasClaros.everforest_light import everforest_light
from TemasClaros.github_light_colorblind import github_light_colorblind
from TemasClaros.github_light_default import github_light_default
from TemasClaros.github_light_high_contrast import github_light_high_contrast
from TemasClaros.github_light import github_light
from TemasClaros.github_light_tritanopia import github_light_tritanopia
from TemasClaros.gruvbox_light import gruvbox_light
from TemasClaros.gruvbox_material_hard_light import gruvbox_material_hard_light
from TemasClaros.gruvbox_material_medium_light import gruvbox_material_medium_light
from TemasClaros.high_contrast import high_contrast
from TemasClaros.msx import msx
from TemasClaros.night_owlish_light import night_owlish_light
from TemasClaros.noctis_lux import noctis_lux
from TemasClaros.nord_light import nord_light
from TemasClaros.papercolor_light import papercolor_light
from TemasClaros.papertheme import papertheme
from TemasClaros.pencil_light import pencil_light
from TemasClaros.rose_pine_dawn import rose_pine_dawn
from TemasClaros.solarized_light import solarized_light

from TemasOscuros.afterglow import afterglow
from TemasOscuros.alacritty_0_12 import alacritty_0_12
from TemasOscuros.ashes_dark import ashes_dark
from TemasOscuros.base16_default_dark import base16_default_dark
from TemasOscuros.bluish import bluish
from TemasOscuros.breeze import breeze
from TemasOscuros.catppuccin_frappe import catppuccin_frappe
from TemasOscuros.catppuccin_macchiato import catppuccin_macchiato
from TemasOscuros.catppuccin_mocha import catppuccin_mocha
from TemasOscuros.chicago95 import chicago95
from TemasOscuros.citylights import citylights
from TemasOscuros.Cobalt2 import Cobalt2
from TemasOscuros.dark_pastels import dark_pastels
from TemasOscuros.deep_space import deep_space
from TemasOscuros.doom_one import doom_one
from TemasOscuros.dracula_plus import dracula_plus
from TemasOscuros.enfocado_dark import enfocado_dark
from TemasOscuros.everforest_dark import everforest_dark
from TemasOscuros.falcon import falcon
from TemasOscuros.flat_remix import flat_remix
from TemasOscuros.flexoki import flexoki
from TemasOscuros.github_dark_dimmed import github_dark_dimmed
from TemasOscuros.github_dark import github_dark
from TemasOscuros.gnome_terminal import gnome_terminal
from TemasOscuros.google import google
from TemasOscuros.gruvbox_dark import gruvbox_dark
from TemasOscuros.gruvbox_material_hard_dark import gruvbox_material_hard_dark
from TemasOscuros.gruvbox_material_medium_dark import gruvbox_material_medium_dark
from TemasOscuros.gruvbox_material import gruvbox_material
from TemasOscuros.hardhacker import hardhacker
from TemasOscuros.hatsunemiku import hatsunemiku
from TemasOscuros.horizon_dark import horizon_dark
from TemasOscuros.inferno import inferno
from TemasOscuros.iris import iris
from TemasOscuros.kanagawa_dragon import kanagawa_dragon
from TemasOscuros.kanagawa_wave import kanagawa_wave
from TemasOscuros.konsole_linux import konsole_linux
from TemasOscuros.low_contrast import low_contrast
from TemasOscuros.Mariana import Mariana
from TemasOscuros.marine_dark import marine_dark
from TemasOscuros.material_theme import material_theme
from TemasOscuros.meliora import meliora
from TemasOscuros.monokai_pro import monokai_pro
from TemasOscuros.monokai import monokai
from TemasOscuros.moonlight_ii_vscode import moonlight_ii_vscode
from TemasOscuros.nightfox import nightfox
from TemasOscuros.nord import nord
from TemasOscuros.one_dark import one_dark
from TemasOscuros.papercolor_dark import papercolor_dark
from TemasOscuros.pencil_dark import pencil_dark
from TemasOscuros.rainbow import rainbow
from TemasOscuros.remedy_dark import remedy_dark
from TemasOscuros.rose_pine_moon import rose_pine_moon
from TemasOscuros.seashells import seashells
from TemasOscuros.smoooooth import smoooooth
from TemasOscuros.snazzy import snazzy
from TemasOscuros.solarized_dark import solarized_dark
from TemasOscuros.solarized_osaka import solarized_osaka
from TemasOscuros.taerminal import taerminal
from TemasOscuros.tango_dark import tango_dark
from TemasOscuros.tender import tender
from TemasOscuros.terminal_app import terminal_app
from TemasOscuros.tomorrow_night_bright import tomorrow_night_bright
from TemasOscuros.tomorrow_night import tomorrow_night
from TemasOscuros.ubuntu import ubuntu
from TemasOscuros.vesper import vesper
from TemasOscuros.wombat import wombat
from TemasOscuros.zenburn import zenburn

from TemasRecomendados.alabaster_dark import alabaster_dark
from TemasRecomendados.argonaut import argonaut
from TemasRecomendados.aura import aura
from TemasRecomendados.ayu_dark import ayu_dark
from TemasRecomendados.ayu_mirage import ayu_mirage
from TemasRecomendados.baitong import baitong
from TemasRecomendados.blood_moon import blood_moon
from TemasRecomendados.bluescreen import bluescreen
from TemasRecomendados.campbell import campbell
from TemasRecomendados.carbonfox import carbonfox
from TemasRecomendados.catppuccin import catppuccin
from TemasRecomendados.challenger_deep import challenger_deep
from TemasRecomendados.cyber_punk_neon import cyber_punk_neon
from TemasRecomendados.dark_pride import dark_pride
from TemasRecomendados.dracula_inspired import dracula_inspired
from TemasRecomendados.dracula import dracula
from TemasRecomendados.github_dark_colorblind import github_dark_colorblind
from TemasRecomendados.github_dark_default import github_dark_default
from TemasRecomendados.github_dark_high_contrast import github_dark_high_contrast
from TemasRecomendados.github_dark_tritanopia import github_dark_tritanopia
from TemasRecomendados.gotham import gotham
from TemasRecomendados.greenscreen import greenscreen
from TemasRecomendados.hyper import hyper
from TemasRecomendados.iterm import iterm
from TemasRecomendados.material_darker import material_darker
from TemasRecomendados.material_ocean import material_ocean
from TemasRecomendados.material_theme_mod import material_theme_mod
from TemasRecomendados.midnight_haze import midnight_haze
from TemasRecomendados.monokai_charcoal import monokai_charcoal
from TemasRecomendados.monokai_inspired import monokai_inspired
from TemasRecomendados.nightfly import nightfly
from TemasRecomendados.night_owl import night_owl
from TemasRecomendados.nordic import nordic
from TemasRecomendados.nord_inspired import nord_inspired
from TemasRecomendados.nord_wave import nord_wave
from TemasRecomendados.oceanic_next import oceanic_next
from TemasRecomendados.omni import omni
from TemasRecomendados.onedark_inspired import onedark_inspired
from TemasRecomendados.palenight import palenight
from TemasRecomendados.pastel_dark import pastel_dark
from TemasRecomendados.rosepine_inspired import rosepine_inspired
from TemasRecomendados.rose_pine import rose_pine
from TemasRecomendados.thelovelace import thelovelace
from TemasRecomendados.tokyo_night import tokyo_night
from TemasRecomendados.tokyo_night_storm import tokyo_night_storm
from TemasRecomendados.xterm import xterm

temasClarosDiccionario: Dict[str, Any] = {
    "alabaster": alabaster,
    "ashes_light": ashes_light,
    "atom_one_light": atom_one_light,
    "ayu_light": ayu_light,
    "catppuccin_latte": catppuccin_latte,
    "enfocado_light": enfocado_light,
    "everforest_light": everforest_light,
    "github_light_colorblind": github_light_colorblind,
    "github_light_default": github_light_default,
    "github_light_high_contrast": github_light_high_contrast,
    "github_light": github_light,
    "github_light_tritanopia": github_light_tritanopia,
    "gruvbox_light": gruvbox_light,
    "gruvbox_material_hard_light": gruvbox_material_hard_light,
    "gruvbox_material_medium_light": gruvbox_material_medium_light,
    "high_contrast": high_contrast,
    "msx": msx,
    "night_owlish_light": night_owlish_light,
    "noctis_lux": noctis_lux,
    "nord_light": nord_light,
    "papercolor_light": papercolor_light,
    "papertheme": papertheme,
    "pencil_light": pencil_light,
    "rose_pine_dawn": rose_pine_dawn,
    "solarized_light": solarized_light
}


temasOscurosDiccionario: Dict[str, Any] = {
    "afterglow": afterglow,
    "alacritty_0_12": alacritty_0_12,
    "ashes_dark": ashes_dark,
    "base16_default_dark": base16_default_dark,
    "bluish": bluish,
    "breeze": breeze,
    "catppuccin_frappe": catppuccin_frappe,
    "catppuccin_macchiato": catppuccin_macchiato,
    "catppuccin_mocha": catppuccin_mocha,
    "chicago95": chicago95,
    "citylights": citylights,
    "Cobalt2": Cobalt2,
    "dark_pastels": dark_pastels,
    "deep_space": deep_space,
    "doom_one": doom_one,
    "dracula_plus": dracula_plus,
    "enfocado_dark": enfocado_dark,
    "everforest_dark": everforest_dark,
    "falcon": falcon,
    "flat_remix": flat_remix,
    "flexoki": flexoki,
    "github_dark_dimmed": github_dark_dimmed,
    "github_dark": github_dark,
    "gnome_terminal": gnome_terminal,
    "google": google,
    "gruvbox_dark": gruvbox_dark,
    "gruvbox_material_hard_dark": gruvbox_material_hard_dark,
    "gruvbox_material_medium_dark": gruvbox_material_medium_dark,
    "gruvbox_material": gruvbox_material,
    "hardhacker": hardhacker,
    "hatsunemiku": hatsunemiku,
    "horizon_dark": horizon_dark,
    "inferno": inferno,
    "iris": iris,
    "kanagawa_dragon": kanagawa_dragon,
    "kanagawa_wave": kanagawa_wave,
    "konsole_linux": konsole_linux,
    "low_contrast": low_contrast,
    "Mariana": Mariana,
    "marine_dark": marine_dark,
    "material_theme": material_theme,
    "meliora": meliora,
    "monokai_pro": monokai_pro,
    "monokai": monokai,
    "moonlight_ii_vscode": moonlight_ii_vscode,
    "nightfox": nightfox,
    "nord": nord,
    "one_dark": one_dark,
    "papercolor_dark": papercolor_dark,
    "pencil_dark": pencil_dark,
    "rainbow": rainbow,
    "remedy_dark": remedy_dark,
    "rose_pine_moon": rose_pine_moon,
    "seashells": seashells,
    "smoooooth": smoooooth,
    "snazzy": snazzy,
    "solarized_dark": solarized_dark,
    "solarized_osaka": solarized_osaka,
    "taerminal": taerminal,
    "tango_dark": tango_dark,
    "tender": tender,
    "terminal_app": terminal_app,
    "tomorrow_night_bright": tomorrow_night_bright,
    "tomorrow_night": tomorrow_night,
    "ubuntu": ubuntu,
    "vesper": vesper,
    "wombat": wombat,
    "zenburn": zenburn
}

temasRecomendadosDiccionario: Dict[str, Any] = {
    "alabaster_dark": alabaster_dark,
    "argonaut": argonaut,
    "aura": aura,
    "ayu_dark": ayu_dark,
    "ayu_mirage": ayu_mirage,
    "baitong": baitong,
    "blood_moon": blood_moon,
    "bluescreen": bluescreen,
    "campbell": campbell,
    "carbonfox": carbonfox,
    "catppuccin": catppuccin,
    "challenger_deep": challenger_deep,
    "cyber_punk_neon": cyber_punk_neon,
    "dark_pride": dark_pride,
    "dracula_inspired": dracula_inspired,
    "dracula": dracula,
    "github_dark_colorblind": github_dark_colorblind,
    "github_dark_default": github_dark_default,
    "github_dark_high_contrast": github_dark_high_contrast,
    "github_dark_tritanopia": github_dark_tritanopia,
    "gotham": gotham,
    "greenscreen": greenscreen,
    "hyper": hyper,
    "iterm": iterm,
    "material_darker": material_darker,
    "material_ocean": material_ocean,
    "material_theme_mod": material_theme_mod,
    "midnight_haze": midnight_haze,
    "monokai_charcoal": monokai_charcoal,
    "monokai_inspired": monokai_inspired,
    "nightfly": nightfly,
    "night_owl": night_owl,
    "nordic": nordic,
    "nord_inspired": nord_inspired,
    "nord_wave": nord_wave,
    "oceanic_next": oceanic_next,
    "omni": omni,
    "onedark_inspired": onedark_inspired,
    "palenight": palenight,
    "pastel_dark": pastel_dark,
    "rosepine_inspired": rosepine_inspired,
    "rose_pine": rose_pine,
    "thelovelace": thelovelace,
    "tokyo_night": tokyo_night,
    "tokyo_night_storm": tokyo_night_storm,
    "xterm": xterm
}
"""