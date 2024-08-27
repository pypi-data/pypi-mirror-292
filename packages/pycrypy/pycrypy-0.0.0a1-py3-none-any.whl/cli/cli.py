# Author: Daniel Benjamin Perez Morales
# GitHub: https://github.com/DanielPerezMoralesDev13
# Email: danielperezdev@proton.me


from argparse import Namespace, ArgumentParser
from pathlib import Path
from sys import argv, stderr, exit, stdout
import os, sys

sys.path.append(os.path.abspath(path=os.path.join(os.path.dirname(p=__file__), "..")))

"""
```python
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
```

### `sys.path.append(...)`

- **`sys.path`**: Es una lista en Python que contiene las rutas donde el intérprete de Python buscará los módulos a importar.
- **`sys.path.append(...)`**: Añade un nuevo directorio a la lista `sys.path`. Esto significa que Python buscará módulos también en el directorio que se añada aquí.

### `os.path.abspath(...)`

- **`os.path.abspath(path)`**: Convierte una ruta relativa en una ruta absoluta. Esto es útil para asegurarse de que siempre se trabaje con rutas completas, independientemente del directorio actual desde el que se ejecute el script.

### `os.path.join(...)`

- **`os.path.join(*paths)`**: Junta uno o más componentes de ruta de una manera independiente del sistema operativo. En este caso, se están juntando dos componentes:
  - `os.path.dirname(__file__)`: El directorio donde se encuentra el fichero actual (`__file__`).
  - `'..'`: El directorio padre del directorio actual.

### `os.path.dirname(...)`

- **`os.path.dirname(path)`**: Devuelve la ruta del directorio de un fichero. Aquí, está recibiendo `__file__`, que es una variable que contiene la ruta del fichero Python que se está ejecutando.

### `__file__`

- **`__file__`**: Es una variable que contiene la ruta del fichero Python que se está ejecutando.

### Juntando todo:

1. **`os.path.dirname(__file__)`**: Obtiene la ruta del directorio donde se encuentra el fichero Python que se está ejecutando.
2. **`os.path.join(os.path.dirname(__file__), '..')`**: Junta la ruta del directorio del fichero actual con `'..'`, que representa el directorio padre, obteniendo así la ruta del directorio padre del fichero actual.
3. **`os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))`**: Convierte esta ruta relativa del directorio padre en una ruta absoluta.
4. **`sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))`: Añade esta ruta absoluta del directorio padre a `sys.path`, lo que permite importar módulos desde el directorio padre del fichero actual.

En resumen, esta línea de código añade el directorio padre del fichero actual al `sys.path`, permitiendo importar módulos desde ese directorio.
"""
from config.Path import (
    vsde,
    rutaAlacrittyToml,
)  # Verficar Si Directorio Existe -> Abreviado: vsde
from lib.CambiarCursorThickness import cct  # Cambiar cursor thickness -> Abreviado: cct
from lib.CambiarTemaRuta import ctr  # Cambiar tema ruta -> Abreviado: ctr
from lib.CargarNuevoTema import cnt  # Cargar nuevo tema -> Abreviado: cnt
from lib.CambiarFuente import cf  # Cambiar fuente -> Abreviado: cf
from lib.CambiarEstiloFuente import cef  # Cambiar estilo de fuente -> Abreviado: cef
from lib.CambiarPadding import cp  # Cambiar padding -> Abreviado: cp
from lib.CambiarCursorShape import ccs  # Cambiar cursor shape -> Abreviado: ccs
from lib.CambiarCursorBlinking import ccb  # Cambiar cursor blinking -> Abreviado: ccb
from lib.CambiarTamañoFuente import ctf  # Cambiar tamaño de fuente -> Abreviado: ctf
from lib.CambiarOpacidad import co  # Cambiar opacidad -> Abreviado: co
from lib.CambiarCursorShape import ccs  # Cambiar cursor shape -> Abreviado: ccs
from lib.CambiarCursorBlinking import ccb  # Cambiar cursor blinking -> Abreviado: ccb
from lib.CambiarTamañoFuente import ctf  # Cambiar tamaño de fuente -> Abreviado: ctf
from lib.CambiarOpacidad import co  # Cambiar opacidad -> Abreviado: co
from typing import List, NoReturn, Optional, Type, Union
from lib.FormatColorAnsi import italic, bold
from lib.ListarTemasClaros import ltl
from lib.ListarTemasOscuros import ltd
from lib.ListarTemasRecomendados import ltr

"""
Foro de StackOverflow sobre como parsear varios argumentos a una lista
https://stackoverflow.com/questions/15753701/how-can-i-pass-a-list-as-a-command-line-argument-with-argparse

Foro No hay async lambda
https://stackoverflow.com/questions/40746213/how-to-use-await-in-a-python-lambda
"""


class Cli:
    """
    La clase Cli es parte del programa pycrypy y proporciona una interfaz de línea de comandos (CLI) para configurar fácilmente Alacritty, un emulador de terminal altamente personalizable.

    A través de diversos argumentos y opciones, los usuarios pueden modificar configuraciones como el tema, la fuente, el tamaño de la fuente, el estilo de la fuente, la opacidad, el padding y la forma del cursor, entre otras. La clase también incluye opciones para listar temas recomendados, oscuros y claros, así como mostrar la versión del programa y habilitar un modo detallado de salida.

    Esta clase facilita la personalización de Alacritty directamente desde la terminal, ofreciendo una experiencia de configuración rápida y conveniente.
    """

    def __init__(self: "Cli") -> None:
        self.__version__: str = "0.0.0a1"
        "* Version de la utilidad pycrypy"
        self.parser = ArgumentParser(
            prog=f"{bold(t = 'pycrypy', c = 'blanco')}",  # Nombre del programa que se muestra en la ayuda
            description=f"{bold(t = 'pycrypy es una herramienta de línea de comandos diseñada para configurar fácilmente las opciones de Alacritty desde la terminal utilizando Python.', c = 'azul')}",  # Descripción breve del programa
            add_help=True,  # Permite añadir automáticamente la opción -h/--help para mostrar la ayuda
            epilog=f"{italic(t = '¡Disfruta configurando tu Alacritty con pycrypy!', c = 'verde')}",  # Mensaje al final de la ayuda
            exit_on_error=False,  # Controla si el programa debe salir después de imprimir un mensaje de error
        )

        self.parser.add_argument(
            "-t",
            "--theme",
            nargs="*",
            default=None,
            type=str,
            required=False,
            help=f"{italic(t = 'Cambia el tema utilizado por alacritty', c = 'cyan')}",
        )

        self.parser.add_argument(
            "-P",
            "--theme-path",
            dest="themePath",
            type=str,
            default=False,  # Valor por defecto
            nargs="?",  #  Este valor significa que el argumento puede ser seguido por un valor opcional. Si el valor es proporcionado, se capturará; si no se proporciona, el valor predeterminado se utilizará si se ha especificado uno.
            required=False,
            help=f"{italic(t = 'Ruta absoluta o relativa del tema para aplicarlo en la terminal Alacritty', c = 'cyan')}",
        )

        self.parser.add_argument(
            "-f",
            "--font",
            nargs="*",
            default=None,
            type=str,
            required=False,
            help=f"{italic(t = 'Cambia la fuente utilizada por Alacritty', c = 'cyan')}",
        )

        self.parser.add_argument(
            "-F",
            "--font-size",
            dest="fontSize",
            type=str,  # Luego lo parseamos a `float`
            default=False,  # Valor por defecto
            nargs="?",  #  Este valor significa que el argumento puede ser seguido por un valor opcional. Si el valor es proporcionado, se capturará; si no se proporciona, el valor predeterminado se utilizará si se ha especificado uno.
            required=False,
            help=f"{italic(t = 'Cambia el tamaño de la fuente', c = 'cyan')}",
        )

        self.parser.add_argument(
            "-s",
            "--style",
            nargs="*",
            default=None,
            type=str,
            required=False,
            help=f"{italic(t = 'Cambia el estilo de la fuente: Normal | Bold | Italic | Underline', c = 'cyan')}",
        )

        self.parser.add_argument(
            "-o",
            "--opacity",
            nargs="*",
            type=str,  # Luego lo mapearemos a `float`
            default=None,
            required=False,
            help=f"{italic(t = 'Cambia la opacidad de la terminal de Alacritty', c = 'cyan')}",
        )

        self.parser.add_argument(
            "-p",
            "--padding",
            nargs="*",
            metavar=("X", "Y"),
            default=None,
            type=str,  # Luego lo mapeamos a int
            required=False,
            help=f"{italic(t = 'Cambia el padding de la terminal de Alacritty', c = 'cyan')}",
        )
        """
        shape = "Block" | "Underline" | "Beam"

        shape es una opción que define la forma del cursor y puede tomar uno de estos valores:

        "Block": El cursor es un bloque sólido.
        "Underline": El cursor es una línea horizontal bajo el texto.
        "Beam": El cursor es un rayo vertical que indica la posición entre caracteres.

        El valor predeterminado es "Block", lo que significa que si no se especifica ningún otro valor, el cursor será un bloque sólido.
        """
        self.parser.add_argument(
            "-S",
            "--cursor-shape",
            dest="cursorShape",
            type=str,
            default=False,  # Valor por defecto
            nargs="?",  #  Este valor significa que el argumento puede ser seguido por un valor opcional. Si el valor es proporcionado, se capturará; si no se proporciona, el valor predeterminado se utilizará si se ha especificado uno.
            required=False,
            help=f"{italic(t = 'shape es una opción que define la forma del cursor y puede tomar uno de estos valores: Block | Underline | Beam', c = 'cyan')}",
        )

        """
        blinking = "Never" | "Off" | "On" | "Always"
        blinking define si el cursor parpadea y puede tener uno de estos valores:

            "Never": El cursor nunca parpadea.
            "Off": El parpadeo del cursor está desactivado de manera predeterminada.
            "On": El parpadeo del cursor está activado de manera predeterminada.
            "Always": El cursor siempre está parpadeando.

        El valor predeterminado es "Off", lo que significa que si no se especifica otro valor, el parpadeo del cursor estará desactivado de manera predeterminada.
        """
        self.parser.add_argument(
            "-B",
            "--cursor-blinking",
            dest="cursorBlinking",
            type=str,
            default=False,  # Valor por defecto
            nargs="?",  #  Este valor significa que el argumento puede ser seguido por un valor opcional. Si el valor es proporcionado, se capturará; si no se proporciona, el valor predeterminado se utilizará si se ha especificado uno.
            required=False,
            help=f"{italic(t = 'Esta opcion define si el cursor parpadea y puede tener uno de estos valores: Never | Off | On | Always', c = 'cyan')}",
        )

        self.parser.add_argument(
            "-T",
            "--cursor-thickness",
            dest="cursorThickness",
            type=str,  # lo parseamo luego a float
            default=False,  # Valor por defecto
            nargs="?",  #  Este valor significa que el argumento puede ser seguido por un valor opcional. Si el valor es proporcionado, se capturará; si no se proporciona, el valor predeterminado se utilizará si se ha especificado uno.
            required=False,
            help=f"{italic(t = 'Esta opcion define el grosor del cursor', c = 'cyan')}",
        )

        # listar temas recomendados
        self.parser.add_argument(
            "-R",
            "--theme-recommendations",
            dest="themeRecommendations",
            action="store_true",
            required=False,
            help=f"{italic(t = 'Lista los temas recomendados para alacritty', c = 'cyan')}",
        )

        # Listar temas oscuros
        self.parser.add_argument(
            "-D",
            "--theme-dark",
            dest="themeDark",
            action="store_true",
            required=False,
            help=f"{italic(t = 'Lista los temas oscuros para alacritty', c = 'cyan')}",
        )

        # Listar temas claros
        self.parser.add_argument(
            "-L",
            "--theme-light",
            dest="themeLight",
            action="store_true",
            required=False,
            help=f"{italic(t = 'Lista los temas claros para alacritty', c = 'cyan')}",
        )

        # Añadir el argumento -v
        self.parser.add_argument(
            "-v",
            "--verbose",
            action="store_true",
            required=False,
            help=f"{italic(t = 'Activar modo detallado', c = 'cyan')}",
        )

        # Añadir el argumento --version
        self.parser.add_argument(
            "-V",
            "--version",
            action="store_true",  # Esto es necesario para que el argumento --version funcione
            required=False,
            help=f"{italic(t = 'Muestra la versión del programa y los datos del Autor', c = 'cyan')}",
        )

        # checkeamos que al menos haya un argumento
        if len(argv) == 1:
            self.parser.print_help(file=stderr)
            exit(1)
        return None

    @property
    async def version(self: "Cli") -> str:
        return self.__version__

    @version.setter
    async def version(self: "Cli", version: str) -> None:
        self.__version__ = version
        return None

    @version.deleter
    async def version(self: "Cli") -> None:
        del self.__version__
        return None

    async def parse_args(self: "Cli") -> Namespace:
        # Este método debería devolver los argumentos parseados
        return self.parser.parse_args()

    async def version_pycrypy(self: "Cli") -> str:
        """
        ### "Esta función devuelve la información del autor y la versión de pycrypy."
        """
        autor: str = bold(t="Autor: ", c="cyan") + italic(
            t="Daniel Benjamin Perez Morales\n", c="verde"
        )
        gitHub: str = bold(t="GitHub: ", c="cyan") + italic(
            t="https://github.com/DanielPerezMoralesDev13\n", c="verde"
        )
        email: str = bold(t="Email: ", c="cyan") + italic(
            t="danielperezdev@proton.me\n", c="verde"
        )
        version: str = bold(t="pycrypy Version: ", c="cyan") + italic(
            t=f"`v{self.__version__}`\n", c="verde"
        )
        return autor + gitHub + email + version

    async def validacion_flags_tema(self: "Cli", flag: str) -> None:
        """
        Imprime un mensaje de ayuda si no se proporciona correctamente
        un valor para la flags `-t` y `-P`
        """
        print(
            bold(
                t="Error: Tiene que proporcionar un tema cuando usa la opción ",
                c="rojo",
            ),
            end="",
            file=stderr,
        )
        print(italic(t=f"-{flag}.", c="verde"), end="\n", file=stderr)
        print(
            bold(
                t="Para ver los temas disponibles, use una de las siguientes flags:",
                c="cyan",
            ),
            end="\n",
            file=stderr,
        )
        print(bold(t="-R ", c="verde"), end="", file=stderr)
        print(
            italic(t="Muestra los temas Recomendados.", c="blanco"),
            end="\n",
            file=stderr,
        )
        print(bold(t="Ejemplo de uso: ", c="cyan"), end="", file=stderr)
        print(italic(t="pycrypy -R", c="blanco"), end="\n\n", file=stderr)

        print(bold(t="-D ", c="verde"), end="", file=stderr)
        print(italic(t="Muestra los temas Oscuros.", c="blanco"), end="\n", file=stderr)
        print(bold(t="Ejemplo de uso: ", c="cyan"), end="", file=stderr)
        print(italic(t="pycrypy -D", c="blanco"), end="\n\n", file=stderr)

        print(bold(t="-L ", c="verde"), end="", file=stderr)
        print(italic(t="Muestra los temas Claros.", c="blanco"), end="\n", file=stderr)
        print(bold(t="Ejemplo de uso: ", c="cyan"), end="", file=stderr)
        print(italic(t="pycrypy -L", c="blanco"), end="\n\n", file=stderr)

        print(bold(t="-P ", c="verde"), end="", file=stderr)
        print(
            italic(
                t="Ruta absoluta o relativa del tema para aplicarlo en la terminal Alacritty.",
                c="blanco",
            ),
            end="\n",
            file=stderr,
        )
        print(bold(t="Ejemplo de uso: ", c="cyan"), end="", file=stderr)
        print(
            italic(
                t="pycrypy -P /home/user/.config/alacritty/themes/mytheme.toml",
                c="blanco",
            ),
            end="\n",
            file=stderr,
        )
        return None

    async def validacion_flags_font(self: "Cli") -> None:
        """
        Imprime un mensaje de ayuda si no se proporciona correctamente
        un valor para la flag `-f`
        """
        print(
            bold(
                t="Error: Tiene que proporcionar el nombre de la fuente al usar la opción ",
                c="rojo",
            ),
            end="",
            file=stderr,
        )
        print(italic(t="-f.", c="verde"), end="\n", file=stderr)
        print(bold(t="Ejemplo de uso: ", c="cyan"), end="", file=stderr)
        print(
            italic(t="pycrypy -f Cascadia Code NF", c="blanco"), end="\n", file=stderr
        )
        return None

    async def validacion_flags_font_size(self: "Cli") -> None:
        """
        Imprime un mensaje de ayuda si no se proporciona correctamente
        un valor para la flag `-F`
        """
        print(
            bold(
                t="Error: Tiene que proporcionar el numero (float) para el tamaño de la fuente al usar la opción ",
                c="rojo",
            ),
            end="",
            file=stderr,
        )
        print(italic(t="-F.", c="verde"), end="\n", file=stderr)
        print(bold(t="Ejemplo de uso: ", c="cyan"), end="", file=stderr)
        print(italic(t="pycrypy -F 16.5", c="blanco"), end="\n", file=stderr)
        return None

    async def validacion_flags_font_style(self: "Cli") -> None:
        """
        Imprime un mensaje de ayuda si no se proporciona correctamente
        un valor para la flag `-s`
        """
        print(
            bold(
                t="Error: Tiene que proporcionar el nombre del estilo a aplicar para la fuente al usar la opción ",
                c="rojo",
            ),
            end="",
            file=stderr,
        )
        print(italic(t="-s.", c="verde"), end="\n", file=stderr)
        print(bold(t="Ejemplo de uso: ", c="cyan"), end="", file=stderr)
        print(italic(t="pycrypy -s Bold Italic", c="blanco"), end="\n", file=stderr)
        return None

    async def validacion_flags_opacity(self: "Cli") -> None:
        """
        Imprime un mensaje de ayuda si no se proporciona correctamente
        un valor para la flag `-o`
        """
        print(
            bold(
                t="Error: Tiene que proporcionar correctamente el numero (float) para aplicar opacidad al usar la opción ",
                c="rojo",
            ),
            end="",
            file=stderr,
        )
        print(italic(t="-o.", c="verde"), end="\n", file=stderr)
        print(bold(t="Ejemplo de uso: ", c="cyan"), end="", file=stderr)
        print(italic(t="pycrypy -o 0.7", c="blanco"), end="\n", file=stderr)
        return None

    async def string_mapeo_a_float_or_int(
        self, variable: Union[str, bool], tipo: Type[Union[float, int]]
    ) -> Union[float, int, bool, str, NoReturn]:
        """
        Convierte una cadena de caracteres a un tipo numérico (int o float).

        Parámetros:
        - variable (str): La cadena de caracteres a convertir.
        - tipo (Type[Union[float, int]]): El tipo de dato al que se desea convertir (int o float).

        Retorno:
        - Union[float, int, None]: El valor convertido si la conversión es exitosa. Retorna None si ocurre un error.

        Comportamiento:
        - Si 'tipo' es 'int', intenta convertir 'variable' a un entero.
        - Si 'tipo' es 'float', intenta convertir 'variable' a un flotante.
        - Si ocurre un ValueError, imprime un mensaje de error y retorna None.
        """
        try:
            # Verificamos que la el tipo sea int o false y que la variable no se de tipo False
            if tipo is int and variable:
                return int(variable)
            elif tipo is float and variable:
                return float(variable)
            else:
                return variable
        except ValueError:
            print(
                bold(
                    t=f"Error: El valor proporcionado `{variable}` tiene que ser de tipo ",
                    c="rojo",
                ),
                end="",
                file=stderr,
            )
            print(
                italic(t="int" if tipo is int else "float", c="verde"),
                end="\n",
                file=stderr,
            )
        exit(1)

    async def validacion_flags_padding(self: "Cli") -> None:
        """
        Imprime un mensaje de ayuda si no se proporciona correctamente
        un valor para la flag `-p`
        """
        print(
            bold(
                t="Error: Tiene que proporcionar correctamente los numero (int) `x` e `y` para aplicar el padding al usar la opción ",
                c="rojo",
            ),
            end="",
            file=stderr,
        )
        print(italic(t="-p.", c="verde"), end="\n", file=stderr)
        print(bold(t="Ejemplo de uso: ", c="cyan"), end="", file=stderr)
        print(italic(t="pycrypy -p 5 5", c="blanco"), end="\n", file=stderr)
        return None

    async def validacion_flags_cursor_shape(self: "Cli") -> None:
        """
        Imprime un mensaje de ayuda si no se proporciona correctamente
        un valor para la flag `-S`
        """
        print(
            bold(
                t="Error: Tiene que proporcionar correctamente uno de los siguientes valores ya sea: Block | Underline | Beam | al usar la opción ",
                c="rojo",
            ),
            end="",
            file=stderr,
        )
        print(italic(t="-S.", c="verde"), end="\n", file=stderr)
        print(bold(t="Ejemplo de uso: ", c="cyan"), end="", file=stderr)
        print(italic(t="pycrypy -S Beam", c="blanco"), end="\n", file=stderr)
        print(italic(t="\t\tpycrypy -S Underline", c="blanco"), end="\n", file=stderr)
        print(italic(t="\t\tpycrypy -S Block", c="blanco"), end="\n", file=stderr)
        return None

    async def validacion_flags_cursor_blinking(self: "Cli") -> None:
        """
        Imprime un mensaje de ayuda si no se proporciona correctamente
        un valor para la flag `-B`
        """
        print(
            bold(
                t="Error: Tiene que proporcionar correctamente uno de los siguientes valores ya sea: Never | Off | On | Always al usar la opción ",
                c="rojo",
            ),
            end="",
            file=stderr,
        )
        print(italic(t="-B.", c="verde"), end="\n", file=stderr)
        print(bold(t="Ejemplo de uso: ", c="cyan"), end="", file=stderr)
        print(italic(t="pycrypy -S Never", c="blanco"), end="\n", file=stderr)
        print(italic(t="\t\tpycrypy -B Off", c="blanco"), end="\n", file=stderr)
        print(italic(t="\t\tpycrypy -B On", c="blanco"), end="\n", file=stderr)
        print(italic(t="\t\tpycrypy -B Always", c="blanco"), end="\n", file=stderr)
        return None

    async def validacion_flags_cursor_thickness(self: "Cli") -> None:
        """
        Imprime un mensaje de ayuda si no se proporciona correctamente
        un valor para la flag `-T`
        """
        print(
            bold(
                t="Error: Tiene que proporcionar correctamente el numero (float) para el grosor del cursor al usar la opción ",
                c="rojo",
            ),
            end="",
            file=stderr,
        )
        print(italic(t="-T.", c="verde"), end="\n", file=stderr)
        print(bold(t="Ejemplo de uso: ", c="cyan"), end="", file=stderr)
        print(italic(t="pycrypy -T 0.3", c="blanco"), end="\n", file=stderr)
        return None

    # Retorna str o None
    async def execute(self: "Cli") -> Optional[str]:
        """
        Esta sección del código se encarga de procesar y validar las flags y argumentos proporcionados por el usuario para configurar diversas opciones en Alacritty. A continuación se describen los pasos realizados:

        1. Si se proporciona la flag `--version`, imprime la versión actual de pycrypy.
        2. Verifica si la ruta del fichero `alacritty.toml` existe; si no, ejecuta una función de verificación.
        3. Procesa la flag `--theme`, formateando y aplicando el nuevo tema.
        4. Procesa la flag `--font`, configurando la fuente especificada.
        5. Procesa la flag `--font-size`, configurando el tamaño de la fuente.
        6. Procesa la flag `--style`, configurando el estilo de la fuente.
        7. Procesa la flag `--padding`, configurando el padding.
        8. Procesa la flag `--cursor-shape`, configurando la forma del cursor.
        9. Procesa la flag `--cursor-blinking`, configurando el parpadeo del cursor.
        10. Procesa la flag `--opacity`, configurando la opacidad de la ventana.
        11. Procesa la flag `--theme-path`, configurando la ruta del tema.
        12. Procesa la flag `--cursor-thickness`, configurando el grosor del cursor.
        13. Procesa las flags de recomendación y configuración de temas (`--theme-recommendations`, `--theme-dark`, `--theme-light`).
        14. Si se proporciona la flag `--verbose`, imprime la lista de mensajes verbosos.

        Al final, limpia las listas temporales usadas para almacenar los temas claros, oscuros y recomendados.
        """
        args: Namespace = await self.parse_args()
        verboseList: List[str] = list()

        # Validamos si se proporciono un valor para la flag `t`
        if isinstance(args.theme, list) and len(args.theme) == 0:
            await self.validacion_flags_tema(flag="t")
            exit(1)

        # Validamos si se proporciono un valor para la flag `P`
        if args.themePath is None:
            await self.validacion_flags_tema(flag="P")
            exit(1)

        # Verificamos si no se proporciono ningun valor para la flag `-f`
        if args.font is not None and not args.font:
            await self.validacion_flags_font()
            exit(1)

        # Validamos si el valor proporcionado en la flag `-F` es de tipo float
        if args.fontSize is None:
            await self.validacion_flags_font_size()
            exit(1)

        # Verificamos si no se proporciono ningun valor para la flag `-F`
        if args.fontSize is not None:
            args.fontSize = await self.string_mapeo_a_float_or_int(
                variable=args.fontSize, tipo=float
            )

        # Verificamos si no se proporciono ningun valor para la flag `-s`
        if args.style is not None and not args.style:
            await self.validacion_flags_font_style()
            exit(1)

        # Verificamos si no se proporciono ningun valor para la flag `-o`
        if args.opacity is not None and not args.opacity:
            await self.validacion_flags_opacity()
            exit(1)

        # Mapeamos a float y verficamos que el valor proporcionado es valido
        if args.opacity:
            args.opacity = await self.string_mapeo_a_float_or_int(
                variable=" ".join(args.opacity), tipo=float
            )

        # Verificamos si la el valor de la flag `-p` son de tipo int y tiene 2 valore x e y
        if args.padding is not None and len(args.padding) != 2:
            await self.validacion_flags_padding()
            exit(1)

        if args.padding is not None and len(args.padding) == 2:
            for s, i in enumerate(iterable=args.padding, start=0):
                # s -> start: Para manejar el indice
                # i -> iterable: Para en cada iteracion tener el valor de un indice de la lista
                # await no puede ser incluido en una lambdafunción.
                args.padding[s] = await self.string_mapeo_a_float_or_int(
                    variable=i, tipo=int
                )

        # La primera condición verifica si la flag fue proporcionada por el usuario pero no se proporcionó ningún valor.
        # La segunda condición verifica que `args.cursorShape` no es una instancia de la clase bool,
        # lo que significa que la flag fue proporcionada por el usuario y tiene un valor.
        # La última condición valida que el valor proporcionado por el usuario,
        # después de aplicar el método title(), es uno de los valores permitidos: "Block", "Underline" o "Beam".
        if (
            args.cursorShape is None
            or not isinstance(args.cursorShape, bool)
            and args.cursorShape.title() not in ["Block", "Underline", "Beam"]
        ):
            await self.validacion_flags_cursor_shape()
            exit(1)

        # La primera condición verifica si la flag fue proporcionada por el usuario pero no se proporcionó ningún valor.
        # La segunda condición verifica que `args.cursorShape` no es una instancia de la clase bool,
        # lo que significa que la flag fue proporcionada por el usuario y tiene un valor.
        # La última condición valida que el valor proporcionado por el usuario,
        # después de aplicar el método title(), es uno de los valores permitidos: "Never", "Off", "On" o "Always".
        if (
            args.cursorBlinking is None
            or not isinstance(args.cursorBlinking, bool)
            and args.cursorBlinking.title() not in ["Never", "Off", "On", "Always"]
        ):
            await self.validacion_flags_cursor_blinking()
            exit(1)

        # Validamos si no se proporciono ningun valor al flag `-T`
        if args.cursorThickness is None:
            await self.validacion_flags_cursor_thickness()
            exit(1)

        # Validamos que el valor de la flag `-T` se pueda parsear a float
        if not isinstance(args.cursorThickness, bool):
            args.cursorThickness = await self.string_mapeo_a_float_or_int(
                variable=args.cursorThickness, tipo=float
            )

        # Validamos que estas flags se usen simultaneamente
        if args.theme and args.themePath:
            self.parser.error(
                bold(
                    t="Las opciones -t/--theme y -P/--theme-path no pueden usarse simultáneamente",
                    c="rojo",
                )
            )

        # * Procesamiento de las flags

        if args.version:
            print(await self.version_pycrypy(), end="\n", file=stdout)

        # Verificar si la ruta del directorio de alacritty.toml existe
        directoryRuta: Path = Path(rutaAlacrittyToml)
        if not directoryRuta.exists():
            await vsde(l=verboseList)

        # procesar los argumentos
        if args.theme:
            nuevoTema: str = " ".join(args.theme).lower()
            if " " in nuevoTema:
                nuevoTema = nuevoTema.replace(" ", "_")
            if "-" in nuevoTema:
                nuevoTema = nuevoTema.replace("-", "_")
            await cnt(nuevoTemaAlacritty=nuevoTema, l=verboseList)

        if args.font:
            await cf(nombreFuente=" ".join(args.font), l=verboseList)

        if isinstance(args.fontSize, float):
            await ctf(tamañoFuente=args.fontSize, l=verboseList)

        if args.style:
            await cef(estiloFuente=" ".join(args.style), l=verboseList)

        if args.padding:
            await cp(listaPadding=args.padding, l=verboseList)

        if args.cursorShape:
            await ccs(nombreShape=args.cursorShape.title(), l=verboseList)

        if args.cursorBlinking:
            await ccb(nombreBlinking=args.cursorBlinking.title(), l=verboseList)

        if isinstance(args.opacity, float):
            await co(opacidad=args.opacity, l=verboseList)

        if args.themePath:
            await ctr(rutaTema=args.themePath, l=verboseList)

        if isinstance(args.cursorThickness, float):
            await cct(grosorCursorThickness=args.cursorThickness, l=verboseList)

        if args.themeRecommendations:
            await ltr()
        if args.themeDark:
            await ltd()
        if args.themeLight:
            await ltl()

        if args.verbose:
            print("{l}".format(l="\n".join(verboseList)), end="\n", file=stdout)
            exit(0)

        # Borramos las lista que almacenanaban los modulos ya no son necesarios
        # del temasClaros
        # del temasOscuros
        # del temasRecomendados

        return None
