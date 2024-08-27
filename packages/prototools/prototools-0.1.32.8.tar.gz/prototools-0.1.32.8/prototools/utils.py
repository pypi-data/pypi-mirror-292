import functools
import json
import os
import re
import timeit
import sys
import warnings
from collections import deque
from itertools import chain, cycle, tee, zip_longest, filterfalse
from random import randint, random, Random
from textwrap import dedent
from typing import (
    Any,
    Callable,
    Dict,
    Generator,
    Iterable,
    List,
    Optional,
    Tuple,
    Union,
)

from prototools.colorize import create_colors
from prototools.config import TERMINAL_WIDTH, BORDER
from prototools.letters import CHARACTERS, MATRIX_PANEL

ComposableFunction = Callable[[Any], Any]


def _(s: str, lang: str = "en") -> str:
    """Translate a string to another language.
    
    Args:
        s (str): String to be translated.
        lang (str, optional): Language to be translated. Defaults
            to "en".
    
    Returns:
        str: Translated string.
    """
    if lang not in ("en", "es"):
        lang = "en"
    spanish = {
        "Continue? (y/n)": "Continuar? (s/n)",
        "y": "s",
        "took": "tardó",
        "secs": "s",
    }
    if lang == "es":
        return spanish[s]
    else:
        return s


class RangeDict(dict):
    """Custom range.

    Example:
        Script::

            from prototools import RangeDict

            table = RangeDict({
                (1, 4): "a",
                (5, 8): "b",
                (9, 12): "c",
            })

            print(table[3])  # a
            print(table[6])  # b
            print(table[11])  # c
    """

    def __missing__(self, key):
        for (start, end), value in (
            (key, value) for key, value in self.items()
            if isinstance(key, tuple)
        ):
            if start <= key <= end:
                return value
        raise KeyError("{} not found.".format(key))


def clear_screen() -> None:
    """Clear the screen."""
    os.system("cls" if os.name == "nt" else "clear")


def hide_cursor() -> None:
    """Hide console cursor."""
    print("\033[?25l", end="")


def show_cursor() -> None:
    """Show console cursor."""
    print("\033[?25h", end="")


def terminal_size() -> int:
    """Returns the width of the terminal.

    Returns:
        int: Terminal's widht.
    """
    if sys.platform in ("win32", "linux", "darwin"):
        return os.get_terminal_size()[0]
    else:
        return TERMINAL_WIDTH


def strip_ansi(string: str):
    """Strips ansi string."""
    t = re.compile(r"""\x1b\[[;\d]*[A-Za-z]""", re.VERBOSE).sub
    return t("", string)


def strip_ansi_width(string: str) -> int:
    """Gets ansi string widht.
    
    Args:
        s (str): String of characters.

    Returns:
        int: Width of string (stripped ansi).
    """
    return len(string) - len(strip_ansi(string))


def strip_string(value: str, strip: Union[None, str, bool]) -> str:
    """Strips a string, the argument defines the behaviour.

    Args:
        value: String of characters to be stripped.
        strip: If None, whitespace is stripped; if is a string, the
            characters in the string are stripped; if False, nothing
            is stripped.
    
    Returns:
        str: Stripped version of value.
    """
    if strip is None:
        value = value.strip()
    elif isinstance(strip, str):
        value = value.strip(strip)
    elif strip is False:
        pass
    return value


def chunker(sequence, size) -> Generator:
    """Simple chunker.
    
    Returns:
        Generator: A generator.

    Example:

        >>> list(chunker(list(range(10)), 3))
        [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9]]
    """
    return (sequence[pos:pos + size] for pos in range(0, len(sequence), size))


def pairs(iterable):
    """s -> (s0, s1), (s1, s2), (s2, s3), ...
    
    Example:

        >>> list(pairs([1, 2, 3, 4]))
        [(1, 2), (2, 3), (3, 4)]
    """
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


def tail(n, iterable):
    """Return an iterator over the last *n* items of *iterable*.
    
    Example:

        >>> t = tail(3, 'ABCDEFG')
        >>> list(t)
        ['E', 'F', 'G']
    """
    return iter(deque(iterable, maxlen=n))


def flatten(list_of_lists):
    """Return an iterator flattening one level of nesting in a
    list of lists.

    Example:

        >>> list(flatten([[0, 1], [2, 3]]))
        [0, 1, 2, 3]
    """
    return chain.from_iterable(list_of_lists)


def grouper(iterable, n, fillvalue=None):
    """Collect data into fixed-length chunks or blocks.
    
    Example:

        >>> list(grouper('ABCDEFG', 3, 'x'))
        [('A', 'B', 'C'), ('D', 'E', 'F'), ('G', 'x', 'x')]
    """
    if isinstance(iterable, int):
        warnings.warn(
            "grouper expects iterable as first parameter",
            DeprecationWarning
        )
        n, iterable = iterable, n
    args = [iter(iterable)] * n
    return zip_longest(fillvalue=fillvalue, *args)


def partition(pred, iterable):
    """Use a predicate to partition entries into false entries and true
    entries
    """
    # partition(is_odd, range(10)) --> 0 2 4 6 8   and  1 3 5 7 9
    t1, t2 = tee(iterable)
    return filterfalse(pred, t1), filter(pred, t2)


def main_loop(
    function: Callable,
    args: List[Any] = None,
    kwargs: Dict[Any, None] = None,
    validation: Optional[Callable] = None,
    custom_function: Optional[Callable] = None,
    lang: Optional[str] = "en",
) -> None:
    """Call a function until validation is False.

    Args:
        function (Callable): Function to iterate.
        args (Optional[List[Any]]): Arguments to pass to function.
        kwargs (Optional[Dict[Any, None]]): Keyword arguments to
            pass to function.
        validation (Callable): If False, ends the loop.
        custom_function (Callable): Function that determines if the
            loop should continue. If False, ends the loop.
    
    Returns:
        Union[Any, None]: Result of function.
    """
    if args is None:
        args = []
    if kwargs is None:
        kwargs = {}
    if validation is None:
        validation = ask_to_finish
    result = None
    while True:
        try:
            result = function(*args, **kwargs)
            if custom_function is not None:
                if not custom_function():
                    break
            else:
                if not validation(lang=lang):
                    break
        except Exception as e:
            print(e)
            continue
    return result


def ask_to_finish(
    prompt: Optional[str] = "_default",
    yes: Optional[str] = "_default",
    input_prompt: Optional[str] = "> ",
    lang: Optional[str] = "en",
) -> bool:
    """Ask the user to finish a loop.

    Args:
        prompt (str, optional): Prompt the user to finish or not the
            loop.
        yes (str, optional): Value of affirmative response.
        lang (str, optional): Establish the language.

    Returns:
        bool: True if the user wants to continue, False otherwise.
    """
    if prompt == "_default":
        prompt = _("Continue? (y/n)", lang)
    if yes == "_default":
        yes = _("y", lang)
    print(prompt)
    return input(input_prompt).lower().startswith(yes)


def text_align(
    text: str,
    width: Optional[int] = 80,
    style: Optional[str] = None,
    align: Optional[str] = "right",
) -> None:
    """Similar to Python rjust, ljust and center methods.

    Args:
        text (str): Text.
        width (int): Width.
        style (str, optional): Border style.
        align (str, optional): Alignment of the text.
    
    Example:

        >>> text_align("Test")
        ======= Test =======
    """
    extra = strip_ansi_width(text)
    style = style if style is not None else "double"
    width = width if width is not None else 40
    border = BORDER["horizontal"][style]
    if align == "center":
        extra += 1
        print(u"{izquierda} {contenido} {derecha}".format(
            izquierda=border * (
                (width - int(round(len(text))))//2 - 1 + extra//2
                ),
            contenido=text,
            derecha=border * (
                (width - int(round(len(text))))//2 - 1 + extra//2
                ),
        ))
    elif align == "left":
        print(u"{contenido} {derecha}".format(
            contenido=text,
            derecha=border * (width - len(text) -1 + extra),
        ))
    elif align == "right":
        print(u"{izquierda} {contenido}".format(
            contenido=text,
            izquierda=border * (width - len(text) -1 + extra),
        ))


def time_functions(
    functions: Union[List[Callable], Dict[str, Callable]],
    args: Optional[Tuple[Any, ...]] = (),
    kwargs: Optional[Dict[str, Any]] = None,
    number: int = 1_000_000,
    lang: str = "en"
) -> None:
    """Time the execution of multiple functions.

    Args:
        functions (Union[List[Callable], Dict[str, Callable]]):
            Functions to be timed. Can be a list of functions or a
            dictionary with function names as keys.
        args (Optional[Tuple[Any, ...]]): Positional arguments to pass
            to the functions.
        kwargs (Optional[Dict[str, Any]]): Keyword arguments to pass to
            the functions.
        setup (str, optional): Setup code for necessary imports.
            Defaults to an empty string.
        globals (dict, optional): Global namespace. Defaults to None.
        number (int, optional): Number of iterations for timing.
            Defaults to 1,000,000.
        lang (str, optional): Language for the output. Defaults to "en".

    Example:
        >>> def f(n):
        ...     return [x for x in range(n)]
        >>> def g(n):
        ...     r = []
        ...     for x in range(n):
        ...         r.append(x)
        ...     return r
        >>> time_functions([f, g], args=(100,))
        
        Output:
            'f' took 0.255712 secs
            'g' took 0.421514 secs
    """
    if kwargs is None:
        kwargs = {}

    def time_function(func: Callable, name: str) -> float:
        """Helper function to time a single function."""
        timer = timeit.Timer(lambda: func(*args, **kwargs))
        t = timer.timeit(number=number)
        print(f"'{name}' {_('took', lang=lang)} {t:.6f} {_('secs', lang=lang)}")
        return t

    if isinstance(functions, dict):
        for name, func in functions.items():
            time_function(func, name)
    else:
        for func in functions:
            time_function(func, func.__name__)



def time_functions_globals(
    functions: Union[List[Callable], Dict[str, Callable]],
    args: Optional[Tuple[Any, ...]] = (),
    kwargs: Optional[Dict[str, Any]] = None,
    setup: Optional[str] = "",
    globals: Optional[dict] = None,
    number: int = 1_000_000,
    lang: str = "en"
) -> None:
    """Time the execution of multiple functions.

    Args:
        functions (Union[List[Callable], Dict[str, Callable]]):
            Functions to be timed. Can be a list of functions or a
            dictionary with function names as keys.
        args (Optional[Tuple[Any, ...]]): Positional arguments to pass
            to the functions.
        kwargs (Optional[Dict[str, Any]]): Keyword arguments to pass to
            the functions.
        setup (str, optional): Setup code for necessary imports.
            Defaults to an empty string.
        globals (dict, optional): Global namespace. Defaults to None.
        number (int, optional): Number of iterations for timing.
            Defaults to 1,000,000.
        lang (str, optional): Language for the output. Defaults to "en".

    Example:
        >>> def f(n):
        ...     return [x for x in range(n)]
        >>> def g(n):
        ...     r = []
        ...     for x in range(n):
        ...         r.append(x)
        ...     return r
        >>> time_functions_globals([f, g], args=(100,), globals=globals())
        
        Output:
            'f' took 0.255712 secs
            'g' took 0.421514 secs
    """
    if kwargs is None:
        kwargs = {}

    def format_arguments(args: Tuple[Any, ...], kwargs: Dict[str, Any]) -> str:
        """Format positional and keyword arguments for function calls."""
        args_str = ", ".join(repr(arg) for arg in args)
        kwargs_str = ", ".join(f"{k}={repr(v)}" for k, v in kwargs.items())
        return f"({args_str}" + (f", {kwargs_str}" if kwargs else "") + ")"

    formatted_args = format_arguments(args, kwargs)

    if isinstance(functions, dict):
        timed_functions = [(name, func) for name, func in functions.items()]
    else:
        timed_functions = [(func.__name__, func) for func in functions]

    for name, func in timed_functions:
        func_call = f"{name}{formatted_args}"
        t = timeit.timeit(
            setup=setup,
            stmt=f"{name}{formatted_args}",
            number=number,
            globals=globals
        )
        print(
            f"'{name}' {_('took', lang=lang)} {t:.6f} {_('secs', lang=lang)}"
        )


def time_functions_custom(
    functions: Any,
    args: Tuple[Any],
    setup: Optional[str] = None,
    globals: Optional[Callable] = None,
    number: Optional[int] = 1_000_000,
    lang: Optional[str] = "en"
) -> None:
    """Time functions.

    Args:
        functions (Any): Tuple or Dictionary of functions to be timed.
        args (Tuple[Any]): Tuple of arguments.
        setup (str, optional): Setup code to import needed modules.
        globals (Callable, optional): Current globla namespace.
        number (int, optional): Number of iterations.
        lang (str, optional): Establish the language.

    Example:
        Script::

            def f(n):
                return [x for x in range(n)]

            def g(n):
                r = []
                for x in range(n):
                    r.append(x)
                return r

            if __name__ == "__main__":
                fs = {"f": f, "g": g}
                time_functions_custom(fs, args=(100), globals=globals())

        Output::

            'f' took 2.2157 secs
            'g' took 6.7192 secs
    """
    if isinstance(args, (list, tuple)):
        arguments = "("
        for arg in args:
            if isinstance(arg, str):
                arguments += f"'{arg}', "
            else:
                arguments += f"{arg}, "
        arguments += ")"
    else:
        if isinstance(args, str):
            arguments = f"('{args}')"
        elif isinstance(args, (int, float)):
            arguments = f"({str(args)})"

    if isinstance(functions, dict):
        functions = [k+arguments for k, v in functions.items()]
    else:
        functions = [
            str(function.__name__)+arguments for function in functions
        ]
    for function in functions:
        t = timeit.timeit(
            setup=setup if setup is not None else "",
            stmt=function,
            number=number,
            globals=globals,
        )
        print(
            f"'{function.split('(')[0]}' {_('took', lang=lang)} "\
            f"{t:.6f} {_('secs', lang=lang)}"
        )


def create_f(name: str, args: Any, body: str) -> Callable:
    """Create a function.

    Args:
        name (str): Name of the function.
        args (Any): Arguments.
        unique (str): Body of the function.

    Returns:
        Callable: Function.
    
    Example:
        Script::

            t = '''
                    for i in range(3):
                        r = (x + y) * i
                    print(f"({x} + {y}) * {i} = {r}")
            '''
            f = create_f("g", "x=2 y=3", t)
            f()

        Output::

            (2 + 3) * 0 = 0
            (2 + 3) * 1 = 5
            (2 + 3) * 2 = 10
    """
    template = dedent(f"""
    def {name}({', '.join(args.split())}):
        {body}
    """).strip()
    ns = {}
    exec(template, ns)
    return ns[name]


def compose(*functions: ComposableFunction) -> ComposableFunction:
    """Compose functions.

    Args:
        functions (ComposableFunction): Bunch of functions.

    Returns:
        Callable: Composed function.

    Example:
        >>> def f(x):
        ...     return x * 2
        >>> def g(x):
        ...     return x + 1
        >>> h = compose(f, g)
        >>> h(3)
        7
        >>> h(4)
        9
    """
    return functools.reduce(lambda f, g: lambda x: g(f(x)), functions)


def print_chars(line_length: int = 32, max_char: int = 0x20000) -> None:
    """Print all chars in the terminal, to help you find that cool one
    to put in your customized spinner or bar. Also useful to determine
    if your terminal do support them.

    Args:
        line_length (int): the desired characters per line
        max_char (int): the last character in the unicode table to show
            this goes up to 0x10ffff, but after the default value it
            seems to return only question marks, increase it if would
            like to see more.
    """
    max_char = min(0x10ffff, max(0, max_char))
    for i in range(0x20, max_char + line_length, line_length):
        print(f'0x{i:05x}', end=': ')
        for j in range(line_length):
            if j & 0xf == 0:
                print(' ', end='')
            try:
                print(chr(i + j), end=' ')
            except UnicodeEncodeError:
                print('?', end=' ')
        print()


def progress_bar(
    count: int,
    total: int,
    width: Optional[int] = 40,
    prefix: Optional[str] = "",
    spinbar: Optional[bool] = False,
    ss = cycle([
        u"\u2581"+u"\u2583"+u"\u2585",
        u"\u2583"+u"\u2581"+u"\u2583",
        u"\u2585"+u"\u2583"+u"\u2581",
        u"\u2583"+u"\u2585"+u"\u2583",
    ])

) -> None:
    """Display a progress bar.

    Args:
        count (int): Current count.
        total (int): Total count.
        width (int, optional): Width of the progress bar.
        prefix (str, optional): Prefix of the progress bar.
        spinbar (bool, optional): Display a spinner.
    """
    x = cycle(ss)
    if (count + 1) == total:
        x = iter(["   " for _ in range(4)])
    fullbar = int(round(width * (count + 1) / float(total)))
    per = round(100.0 * (count + 1) / float(total) , 1)
    bar = u'\u2588' * fullbar + u'\u2591' * (width - fullbar)
    if spinbar:
        sys.stdout.write(f"{prefix}{bar}| [{per:02.0f}]% {next(x)}\r")
    else:
        sys.stdout.write(f"{prefix}{bar}| [{per:02.0f}]%\r")
    sys.stdout.flush()


def progressbar(
    iterable,
    width: Optional[int] = 40,
    prefix: Optional[str] = "",
    spinvar: Optional[bool] = True,
    spinvar_color: Optional[Callable] = None,
    bg: Optional[Callable] = None,
    fg: Optional[Callable] = None,
    per: Optional[bool] = True,
    units: Optional[bool] = True,

) -> Generator:
    """Display a progress bar.

    Args:
        iterable (Iterable): Iterable to iterate.
        width (int, optional): Width of the progress bar.
        prefix (str, optional): Prefix of the progress bar.
        spinvar (bool, optional): Display a spinner.
        per (bool, optional): Display the percentage.
        units (bool, optional): Display the units.
    
    Example:
        
        >>> for _ in progressbar(range(50)):
        ...     [x for x in range(1_000_000)]
        ████████████████████████████████░░░░░░░░| 41/50 [82]% ▃▁▃
    """
    count = len(iterable)
    def _c(s, colors_s):
        if colors_s is not None:
            return colors_s(s)
        return s

    ss = [
        _c(u"\u2581"+u"\u2583"+u"\u2585", spinvar_color),
        _c(u"\u2583"+u"\u2581"+u"\u2583", spinvar_color),
        _c(u"\u2585"+u"\u2583"+u"\u2581", spinvar_color),
        _c(u"\u2583"+u"\u2585"+u"\u2583", spinvar_color),
    ]

    s = cycle(ss)
    
    def show(i):
        x = int(width * i / count)
        percentage = int(100 * i / count) if per else ""
        animation = next(s) if spinvar else ""
        if i == count:
            animation = "   "
        fullbar_no_units = "{pre}{block}{empty}| [{per:02}]% {ani}\r"
        fullbar_no_per = "{pre}{block}{empty}| {ani}\r"
        fullbar = "{pre}{block}{empty}| {i:02}/{total:02} [{per:02}]% {ani}\r"
        
        if per and not units:
            sys.stdout.write(
                fullbar_no_units.format(
                    pre=prefix,
                    block=_c(u'\u2588', fg) * x,
                    empty=_c(u'\u2591', bg) * (width - x),
                    per=percentage,
                    ani=animation,
                )
            )
            sys.stdout.flush()
        elif not per and not units:
            sys.stdout.write(
                fullbar_no_per.format(
                    pre=prefix,
                    block=_c(u'\u2588', fg) * x,
                    empty=_c(u'\u2591', bg) * (width - x),
                    ani=animation,
                )
            )
            sys.stdout.flush()
        else:
            sys.stdout.write(
                fullbar.format(
                    pre=prefix,
                    block=_c(u'\u2588', fg) * x,
                    empty=_c(u'\u2591', bg) * (width - x),
                    i=i,
                    total=count,
                    per=percentage,
                    ani=animation,
                )
            )
            sys.stdout.flush()        
    
    show(0)
    for i, item in enumerate(iterable):
        yield item
        show(i+1)
    sys.stdout.write("\n")
    sys.stdout.flush()


def matrix(
    i: int,
    j: int,
    rng: Optional[Tuple[int, int]] = None,
    char: Optional[str] = None,
    rnd: Optional[bool] = False,
    precision: Optional[int] = None
) -> List[List[float]]:
    """Create a matrix.

    Args:
        i (int): Number of rows.
        j (int): Number of columns.
        rng (Tuple[int, int], optional): Range of the matrix.
        char (str, optional): Character to fill the matrix.
        rnd (bool, optional): Randomize the matrix.
        precision (int, optional): Number of decimals.
    
    Returns:
        List[List[float]]: Matrix.

    Example:

        >>> matrix(3, 3)
        [[1, 1, 1], [0, 1, 0], [1, 0, 0]]
    """
    if rng:
        return [[randint(*rng) for _ in range(j)] for _ in range(i)]
    if precision is None:
        return [[randint(0, 1) for _ in range(j)] for _ in range(i)]
    if rnd and isinstance(precision, int):
        return [
            [round(random(), precision) for _ in range(j)] for _ in range(i)
        ]
    return [
        [0 if char is None else char for _ in range(j)] for _ in range(i)
    ]


def show_matrix(
    m: List[List[float]],
    width: Optional[int] = 4,
    style: Optional[str] = None,
    borderless: Optional[bool] = False,
    index: Optional[bool] = False,
    neg_index: Optional[bool] = False,
    sep: Optional[int] = 1,
    color: Optional[Callable] = None,
) -> None:
    """Prints a matrix.

    Args:
        m (List[List[float]]): Matrix to be shown.
        width (int, optional): Width of the matrix. Defaults to 4.
        style (str, optional): Style of the matrix. Defaults to None.
        borderless (bool, optional): Show the matrix without borders.
            Defaults to False.
        index (bool, optional): Show the index of the matrix.
            Defaults to False.
        neg_index (bool, optional): Show the negative index of the matrix.
        sep (int, optional): Separation between the columns. Defaults
            to 1.
        color (Callable, optional): Color of the matrix. Defaults to None.
    
    >>> matrix = [[1, 2, 3], [4, 5, 6]]
    >>> show_matrix(matrix)
    ┌────┬────┬────┐
    │ 1  │ 2  │ 3  │
    ├────┼────┼────┤
    │ 4  │ 5  │ 6  │
    └────┴────┴────┘
    >>> show_matrix(matrix, borderless=True, width=1)
    1 2 3 
    4 5 6
    """
    def _c(s: str, color: Callable) -> str:
        if color is not None:
            return color(s)
        return s
    
    if style is None:
        style = "light"
    Border = type("Borde", (), {k:v[style] for k, v in BORDER.items()})
    border = Border()
    try:
        tmp_width = len(str(m[0][0])) - strip_ansi_width(str(m[0][0]))
    except TypeError:
        m = [m]
        tmp_width = len(m)
    if width < tmp_width:
        width = tmp_width + 4
    if not borderless:
        if index:
            idx = [str(i) for i in range(len(m[0]))]
            print(" "*width, end="")
            print(*idx, sep=" "*((width)))
        if neg_index:
            idx = reversed([str(i) for i in range(-1, -len(m[0])-1, -1)])
            print(" "*width, end="")
            print(*idx, sep=" "*((width-1)))
        for i in range(len(m)):
            r = f"{i} {_c(border.vertical, color)}" if index or neg_index else _c(border.vertical, color)
            first_line = _c(border.top_left, color) if i == 0 else _c(border.vertical_left, color)
            line = "{}{}".format(
                _c(border.horizontal, color) * (width),
                _c(border.intersection, color) if i != 0 else _c(border.horizontal_top, color)
            ) * (len(m[i])-1)
            last_line = "{}{}".format(
                _c(border.horizontal, color) * (width),
                _c(border.vertical_right, color) if i != 0 else _c(border.top_right, color)
            )
            if index or neg_index:
                print(f"  {first_line}{line}{last_line}")
            else:
                print(f"{first_line}{line}{last_line}")
            for j in range(len(m[i])):
                extra = strip_ansi_width(str(m[i][j]))
                r += "{v:^{al}}{l}".format(
                    v=(m[i][j]),
                    al=width + extra,
                    l=_c(border.vertical, color)
                )
            print(r)
        line = "{}{}".format(
            _c(border.horizontal, color) * (width),
            _c(border.horizontal_bottom, color)
        ) * (len(m[i]) - 1)
        last_line = "{}{}".format(
            _c(border.horizontal, color) * (width),
            _c(border.bottom_right, color)
        )
        if index or neg_index:
            print(f"  {_c(border.bottom_left, color)}{line}{last_line}")
        else:
            print(f"{_c(border.bottom_left, color)}{line}{last_line}")
    else:
        for i in range(len(m)):
            r = ''
            for j in range(len(m[i])):
                r += f'{m[i][j]:^{width}}{" " * sep}'
            print(r)
        print('')


def textbox(
    text: str,
    width: Optional[int] = 80,
    style: Optional[str] = None,
    align: Optional[str] = "center",
    bcolor: Optional[str] = None,
    ml: Optional[int] = 0,
    light: Optional[bool] = True,
) -> str:
    """Draw a box with a text in it.

    Args:
        text (str): Text.
        width (int): Width.
        style (str, optional): Border style.
        align (str, optional): Alignment of the text.
        bcolor (str, optional): Border color.
        ml (int, optional): Margin left.
        light (bool, optional): Adds padding top and bottom.

    Returns:
        str: Box.

    Example:

        >>> textbox(green("ProtoTools"), width=30, bcolor="red")
        ┌────────────────────────────┐
        │         ProtoTools         │
        └────────────────────────────┘
    """
    def color(s):
        if bcolor is not None:
            return _color(s)
        return s

    _align = {"center": "^", "left": "<", "right": ">"}
    extra = strip_ansi_width(text)
    style = style if style is not None else "light"
    width = width if width is not None else 40
    _color = create_colors(fg=bcolor)

    lines = text.splitlines()
    processed_lines = []
    for line in lines:
        while strip_ansi_width(line) > (width - 4):
            split_point = (width - 4)
            processed_lines.append(line[:split_point])
            line = line[split_point:]
        processed_lines.append(line)

    top = u"{ml}{left}{center}{right}".format(
        left=color(BORDER["top_left"][style]),
        center=color(BORDER["horizontal"][style]) * (width - 2),
        right=color(BORDER["top_right"][style]),
        ml=" "*ml,
    )
    inner_top = u"{ml}{left}{center}{right}".format(
        left=color(BORDER["vertical"][style]),
        center=" "*(width - 2),
        right=color(BORDER["vertical"][style]),
        ml=" "*ml,
    )
    middle = [
        u"{ml}{left} {content:{al}{w}} {right}".format(
            left=color(BORDER["vertical"][style]),
            content=line,
            al=_align[align],
            w=(width - 4) + strip_ansi_width(line),
            right=color(BORDER["vertical"][style]),
            ml=" "*ml,
        ) for line in processed_lines
    ]
    inner_bottom = u"{ml}{left}{center}{right}".format(
        left=color(BORDER["vertical"][style]),
        center=" "*(width - 2),
        right=color(BORDER["vertical"][style]),
        ml=" "*ml,
    )
    bottom = u"{ml}{left}{center}{right}".format(
        left=color(BORDER["bottom_left"][style]),
        center=color(BORDER["horizontal"][style]) * (width - 2),
        right=color(BORDER["bottom_right"][style]),
        ml=" "*ml,
    )
    if light:
        print(top, *middle, bottom, sep="\n")
    else:
        print(top, inner_top, *middle, inner_bottom, bottom, sep="\n")


def __generate_bytes_for_seed(seed: int, message: str) -> bytearray:
    data = Random(seed)
    garbage = Random(34988394)

    data.seed(seed)
    result = bytearray()
    i = 0
    while i < len(message):
        c = message[i]
        if data.randrange(2):
            result.append(data.randrange(256) ^ ord(c))
            i += 1
        else:
            result.append(garbage.randrange(256))
    return result


def secret_message(message: str = "prototools 0.1.22") -> str:
    """Generates code that has a secret message when executed. To used
    it, copy the generated code and execute it in another file.

    Args:
        message (str, optional): Secret message.
    
    Returns:
        str: Code.

    Example:

        >>> secret_message("Hello World!")

        Output::

                import random

                random.seed(69420)
                print(''.join(chr(random.randrange(256) ^ c)
                    for c in bytes.fromhex(
                        'EA8760D97CD68CB754E490D68D376C1997BBF9BD363BCE05CD85'
                        )
                    if random.randrange(2))
                )
    
    """
    seed = 69420
    print(dedent(f"""\
    import random

    random.seed({seed})
    print(''.join(chr(random.randrange(256) ^ c)
        for c in bytes.fromhex(
            {repr(__generate_bytes_for_seed(seed, message).hex().upper())}
            )
        if random.randrange(2)))"""
    ))


def write_letters(text: str) -> None:
    """
    Example:

        >>> write_letters("Hello World!")
         _____            _         _              _
        |  _  | ___  ___ | |_  ___ | |_  ___  ___ | | ___
        |   __||  _|| . ||  _|| . ||  _|| . || . || ||_ -|
        |__|   |_|  |___||_|  |___||_|  |___||___||_||___|

    """
    result = ""
    for i in range(6):
        for char in text:
            result += CHARACTERS[char][i]
        result += "\n"
    print(result)


def write_letters_custom(text: str, n: int, color: Callable) -> None:
    result = ""
    for i in range(6):
        for j, char in enumerate(text):
            if j == n:
                result += color(CHARACTERS[char][i])
            else:
                result += CHARACTERS[char][i]
        result += "\n"
    print(result)


def matrix_panel(text: str, fg: str = None, bg: str = None) -> None:
    """
    Example:

        >>> matrix_panel("ABC")
        ░░██████░░░░████████░░░░░░████████░░
        ██░░░░░░██░░██░░░░░░██░░██░░░░░░░░░░
        ██░░░░░░██░░██░░░░░░██░░██░░░░░░░░░░
        ██░░░░░░██░░████████░░░░██░░░░░░░░░░
        ██████████░░██░░░░░░██░░██░░░░░░░░░░
        ██░░░░░░██░░██░░░░░░██░░██░░░░░░░░░░
        ██░░░░░░██░░████████░░░░░░████████░░
    """
    text = text.lower()
    fg = "██" if fg is None else fg
    bg = "░░" if bg is None else bg
    display = [
        [bg for _ in range(5 * len(text) + len(text))]
        for _ in range(7)
    ]
    for i, s in enumerate(text):
        for j, row in enumerate(MATRIX_PANEL[s]):
            for k, col in enumerate(row):
                if col == 1:
                    display[j][i * 6 + k] = fg
    print("\n".join(["".join(x) for x in display]))


def mvc_setup(
    mode: str,
    cli: Tuple[object, object], 
    gui: Tuple[object, object],
    web: Tuple[object, object],
    web_name: Optional[str] = "WEB",
    cli_name: Optional[str] = "CLI",
    gui_name: Optional[str] = "GUI",
) -> Tuple[bool, Optional[object], Optional[object]]:
    """Setup the MVC architecture.

    Args:
        mode (str): Mode.
        cli (Tuple[object, object]): CLI.
        gui (Tuple[object, object]): GUI.
        web (Tuple[object, object]): WEB.
        web_name (str, optional): WEB name.
        cli_name (str, optional): CLI name.
        gui_name (str, optional): GUI name.
    """
    if mode == web_name:
        controller, view = web
        return True, controller, view
    elif mode == cli_name:
        controller, view = cli
    elif mode == gui_name:
        controller, view = gui
    return False, controller, view


def mvc_launcher(
    mode: str,
    model: object,
    cli: Tuple[object, object],
    gui: Tuple[object, object],
    web: Tuple[object, object],
    name: Optional[str] = None,
    url: Optional[str] = "http://127.0.0.1:5000/",
) -> None:
    """A simple MVC Launcher.

    Args:
        mode (str): Mode.
        model (object): Model.
        cli (Tuple[object, object]): CLI controller, CLI view.
        gui (Tuple[object, object]): GUI controller, GUI view.
        web (Tuple[object, object]): Web controller, Web view.
        name (str, optional): Name of the application. Defaults to None.
        url (str, optional): URL. Defaults to
            "http://127.0.0.1:5000/".
    """
    response, controller, view = mvc_setup(
        mode=mode,
        cli=cli,
        gui=gui,
        web=web
    )
    if response: 
        import webbrowser
        
        webbrowser.open(url)
        app = controller(model, view, name=name)
    else:
        app = controller(model, view)
    app.run()


def make_grid(
    iterable: Iterable[Any],
    group: int,
    function: Optional[Callable] = str,
    reversed: bool = True
) -> List[List[Any]]:
    """Generates a grid.

    Args:
        iterable (Iterable[Any]): Iterable.
        function (Callable): Function to apply to each element.
        group (int): Group size.
        reversed (bool, optional): If True, the grid is reversed.
            Defaults to False.
    
    Returns:
        List[List[Any]]: Grid.

    Example:

        >>> make_grid(range(1, 10), 3)
        [('7', '8', '9'), ('4', '5', '6'), ('1', '2', '3')]
    """
    grid = list(grouper(map(function, iterable), group))
    if reversed:
        grid.reverse()
    return grid


def get_data(
    filename: str,
    mode: str = "lines",
    encoding: str = "utf-8",
) -> Union[List[str], str, Any]:
    """Get data.

    Args:
        filename (str): The name of the file to read.
        mode (str, optional): The mode to read the file. Options are:
            - "lines" (default): Returns a list of lines.
            - "text": Returns the entire content as a single string.
            - "json": Returns the parsed JSON data.
        encoding (str, optional): The encoding used to read the file.
            Default is "utf-8".

    Returns:
        Union[List[str], str, Any]: The file content based on the selected mode.

    Raises:
        ValueError: If the specified mode is not supported.
    
    Example:
        >>> # Reading lines from a text file
        >>> lines = get_data("data.txt")
        >>> print(lines)
        ['line 1', 'line 2', 'line 3']
        
        >>> # Reading the entire content as a single string
        >>> text = get_data("data.txt", mode="text")
        >>> print(text)
        'line 1\\nline 2\\nline 3'
        
        >>> # Reading and parsing a JSON file
        >>> data = get_data("data.json", mode="json")
        >>> print(data)
        {'key1': 'value1', 'key2': 'value2'}
    """
    with open(filename, "r", encoding=encoding) as f:
        if mode == "lines":
            return f.read().splitlines()
        elif mode == "text":
            return f.read()
        elif mode == "json":
            return json.load(f)
        else:
            raise ValueError(f"Unsupported mode: {mode}")
