#VERSION 1.2
"""Módulo de configuraciones globales, enumeradores y utilidades de cálculo.

Define los elementos fundamentales del juego, el sistema de rarezas,
los tipos de habilidades disponibles y las funciones matemáticas/probabilísticas
para la selección y modificación de estadísticas.
"""

from enum import Enum
from dataclasses import dataclass
import random

class Elements(Enum):
    """Elementos elementales que definen los tipos de afinidad en el juego."""
    LUMINE = "LUMINE"
    OBSCUR = "OBSCUR"
    AQUA = "AQUA"
    IGNI = "IGNI"
    TERRA = "TERRA"
    VENTUS = "VENTUS"
    PSI = "PSI"
    NONE = "NONE"
    CRYO = "CRYO"
    ELECTRO = "ELECTRO"
    TOKSIC = "TOKSIC"
    PLASMA = "PLASMA"
    METALI = "METALI"
    NATURA = "NATURA"
    NEUTRAL = "NEUTRAL"

class Rarity(Enum):
    """Niveles de rareza del juego con sus respectivos multiplicadores base."""
    COMMON = 1       # +0%
    UNCOMMON = 1.1   # +10%
    RARE = 1.15      # +15%
    EPIC = 1.35      # +35%
    LEGENDARY = 1.65 # +65%

    @property
    def modifier(self) -> float:
        """float: Devuelve el valor multiplicador asociado a la rareza."""
        return self.value

class SkillTypes(Enum):
    """Categorías funcionales de las habilidades en combate."""
    ATTACK = "ATTACK"
    DEFENSE = "DEFENSE"
    HEALING = "HEALING"
    BUFF = "BUFF"
    DEBUFF = "DEBUFF"
    ULTIMATE = "ULTIMATE"

class GlobalCharacters(Enum):
    """Registro global de los personajes principales disponibles."""
    LISBETH = 1
    LEAH = 2
    # ARIS = 3
    # TAKINA = 4
    # LEONARDO = 5

class GlobalSupportGroups(Enum):
    """Facciones o grupos globales a los que pertenecen las cartas de soporte."""
    CHRISTIANITY = "CHRISTIANITY"
    CELTIC = "CELTIC"

class GlobalCharacterGroup(Enum):
    TEST = "TEST"

def select_rarity(rng: random.Random):
    """Selecciona una rareza de forma aleatoria basada en porcentajes fijos de aparición.

    Probabilidades: Common (50%), Uncommon (25%), Rare (15%), Epic (8%), Legendary (2%).

    Args:
        rng (random.Random): Instancia del generador aleatorio a utilizar.

    Returns:
        Rarity: Miembro de la enumeración Rarity seleccionado.
    """
    return rng.choices(
        population=list(Rarity),
        weights=[0.5, 0.25, 0.15, 0.08, 0.02], 
        k=1
    )[0]

def apply_modifier(stat: int | float, modifier: float, extra: float) -> int:
    """Aplica los multiplicadores de rareza y variación extra a una estadística base.

    Args:
        stat (int | float): Valor de la estadística inicial (vida, ataque, etc.).
        modifier (float): Multiplicador base otorgado por la rareza de la carta.
        extra (float): Porcentaje de variación aleatoria adicional.

    Returns:
        int: El valor de la estadística final redondeado al entero más cercano.
    """
    return round(stat * (modifier + extra))

def select_weighted_skill(rng, weighted_skills):
    return rng.choices(
        population=[entry.skill for entry in weighted_skills],
        weights=[entry.weight for entry in weighted_skills],
        k=1,
    )[0]

def select_weighted_template(rng, catalog):
    names = list(catalog)
    templates = [catalog[name] for name in names]

    return rng.choices(
        population=names,
        weights=[template.weight for template in templates],
        k=1,
    )[0]