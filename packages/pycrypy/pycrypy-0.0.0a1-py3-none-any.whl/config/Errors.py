#!/usr/bin/env python3

# Author: Daniel Benjamin Perez Morales
# GitHub: https://github.com/DanielPerezMoralesDev13
# Email: danielperezdev@proton.me

from lib.FormatColorAnsi import bold, italic

# No se encontró el tema en el sistema: Abreviado net
async def net(nombreTema: str) -> str:
    """
    Genera un mensaje de error formateado cuando un tema específico no se encuentra en el sistema.

    Parámetros:
    - nombreTema (str): El nombre del tema que no se encontró.

    Retorno:
    - str: Un mensaje de error formateado indicando que el tema no se encontró.

    Comportamiento:
    - Construye un mensaje de error utilizando formato en negrita y cursiva.
    - `v1` contiene el texto en negrita "Error: No se encontró el tema" con color rojo.
    - `v2` contiene el nombre del tema en cursiva y color verde.
    - `v3` contiene el texto en negrita "en el sistema" con color rojo.
    - Retorna la concatenación de `v1`, `v2` y `v3`.

    Ejemplo de uso:
    - Si se llama a `net(nombreTema="temaDesconocido")`, la función retornará un mensaje formateado indicando que el tema "temaDesconocido" no se encontró en el sistema.
    """
    v1: str = bold(t="Error: No se encontró el tema", c="rojo")
    v2: str = italic(t=f"`{nombreTema}`", c="verde")
    v3: str = bold(t="en el sistema", c="rojo")
    return v1 + v2 + v3
