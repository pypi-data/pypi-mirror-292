import re
from enum import Enum


class NaturalRUCLetter(Enum):
    NO_LETTER = ("", "00", "00", "No letter")
    E = ("E", "5", "66", "Foreigner")
    PE = ("PE", "75", "82", "Panamanian Foreigner ")
    N = ("N", "4", "92", "Naturalized")
    AV = ("AV", "15", "9595", "Before the system")
    PI = ("PI", "79", "9595", "Indigenous People")

    def __init__(self, letter, code, validation_code, name) -> None:
        self.letter = letter
        self.code = code
        self.validation_code = validation_code
        self.code_name = name

    @classmethod
    def from_code(cls, letter: str):
        for member in cls:
            if member.letter == letter.upper():
                return member
        raise ValueError(f"Invalid RUC letter: {letter}")

    @classmethod
    def from_part(cls, part):
        regex = re.compile(r"(\d+)?(AV|PI)")
        match = regex.match(part)
        if match:
            return cls.from_code(match.group(2))
        raise ValueError(f"Invalid RUC part: {part}.")


class Province(Enum):
    EN_BLANCO = ("", "En Blanco")
    NO_ASIGNADA = ("00", "No Asignada")
    BOCAS_DEL_TORO = ("01", "Bocas Del Toro")
    COCLE = ("02", "Cocle")
    COLON = ("03", "Colon")
    CHIRIQUI = ("04", "Chiriqui")
    DARIEN = ("05", "Darien")
    HERRERA = ("06", "Herrera")
    LOS_SANTOS = ("07", "Los Santos")
    PANAMA = ("08", "Panama")
    VERAGUAS = ("09", "Veraguas")
    GUNA_YALA = ("10", "Guna Yala, Madugandí y Wargandí")
    EMBER_WOUNAAN = ("11", "Embera Wounaan")
    NGABE_BUGLE = ("12", "Ngabe Bugle")
    PANAMA_OESTE = ("13", "Panama Oeste")

    def __init__(self, code, description) -> None:
        self.code = code
        self.province_name = description

    @classmethod
    def from_code(cls, code):
        for member in cls:
            if member.code == code.zfill(2):
                return member
        raise ValueError(f"Invalid province code: {code}")

    @classmethod
    def from_part(cls, part: str):
        regex = re.compile(r"(\d+)?(AV|PI)")
        match = regex.match(part)
        if match:
            return cls.from_code(match.group(1))
        raise ValueError(f"Invalid province part: {part}")
