#!/usr/bin/env python3

# Author: Daniel Benjamin Perez Morales
# GitHub: https://github.com/DanielPerezMoralesDev13
# Email: danielperezdev@proton.me

from cli import Cli
from asyncio import run
from sys import exit

def main() -> None:
    """
    Funcion Principal
    """
    args: Cli = Cli()
    run(main = args.execute())
    return None

if __name__ == "__main__":
    main()
    exit(0)
