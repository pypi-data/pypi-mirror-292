#from __future__ import annotations
import re

ABC: str = "abcdefghijklmnñopqrstuvwxyz"
ABC123: str = "abcdefghijklmnñopqrstuvwxyz1234567890"

EMAIL_REGEX = re.compile(
    r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
)
URL_REGEX = re.compile(
    r"""(http(s)?:\/\/.)?(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)"""
)
NUMBER_REGEX = re.compile(
    r"[-+]?\d*\.?\d+|[-+]?\d+" #r"[-+]?\d*\.\d+|\d+" #r'\d+(?:\.\d+)?'
)
ROMAN_REGEX = re.compile("""
    ^M{0,3}
    (CM|CD|D?C{0,3})?
    (XC|XL|L?X{0,3})?
    (IX|IV|V?I{0,3})?$
""", re.VERBOSE)

DIAS: tuple = (
    "lunes",
    "martes",
    "miércoles",
    "jueves",
    "viernes",
    "sábado",
    "domingo",
)

DAYS: tuple = (
    "Sunday",
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
)

MESES: tuple = (
    "enero",
    "febrero",
    "marzo",
    "abril",
    "mayo",
    "junio",
    "julio",
    "agosto",
    "septiembre",
    "octubre",
    "noviembre",
    "diciembre",
)

MONTHS: tuple = (
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
)
