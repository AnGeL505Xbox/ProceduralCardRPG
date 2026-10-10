#VERSION 1.0
from dataclasses import dataclass
from globals import Elements, SkillTypes

@dataclass(frozen=True)
class StatRange:
    minimum: int | float
    maximum: int | float

@dataclass (frozen=True)
class SkillTemplate:
    name: str
    desc: str
    element: Elements
    skill_type: SkillTypes
    base_power: int

    def to_json(self):
        name: str = self.name
        description: str = self.desc
        element: str = self.element.name
        skill_type: str = self.skill_type.name
        base_power: int = self.base_power

        data = {
            "name": name,
            "description": description,
            "element": element,
            "skill_type": skill_type,
            "base_power": base_power
        }
        
        return data


@dataclass(frozen=True)
class WeightedSkill:
    skill: SkillTemplate
    weight: float

@dataclass(frozen=True)
class CharacterVariantTemplate:
    weight: float
    desc: str
    main_element: Elements
    second_element: Elements
    health: StatRange
    attack: StatRange
    defense: StatRange
    ultimate_skill: tuple[WeightedSkill, ...]

@dataclass(frozen=True)
class SupportTemplate:
    name: str
    weight: float
    desc: str
    element: Elements
    health: StatRange
    attack: StatRange
    defense: StatRange
    skills: tuple[SkillTemplate, ...]

@dataclass (frozen=True)
class Catalogs:
    characters: dict[str, dict[str, CharacterVariantTemplate]]
    supports: dict[str, dict[str, SupportTemplate]]
    skills: dict[str,SkillTemplate]
    #elements: dict[Elements, dict[Elements, float]]