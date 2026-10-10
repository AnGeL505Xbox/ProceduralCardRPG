#VERSION 2.0b
import json
from pathlib import Path
from globals import Elements, SkillTypes, GlobalCharacters, GlobalSupportGroups
from templates import CharacterVariantTemplate, Catalogs, SupportTemplate, SkillTemplate, StatRange, WeightedSkill
from json_validator import main_json_validator, support_json_validator

SUPPORTED_CHARACTER_VERSION = 1
SUPPORTED_SUPPORT_VERSION = 1
SUPPORTED_SKILL_VERSION = 1
SUPPORTED_ELEMENT_MATRIX_VERSION = 1

BASE_DIR = Path(__file__).parent
SKILL_FILE_PATH = BASE_DIR / "data" / "skill_data.json"
MAIN_FILE_PATH = BASE_DIR / "data" / "main_data.json"
SUPPORT_FILE_PATH = BASE_DIR / "data" / "support_data.json"
SUPPORT_ELEMENT_PATH = BASE_DIR / "data" / "element_data.json"

def open_path(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def open_data(type_data: str):
    if type_data == "skill":
        return open_path(SKILL_FILE_PATH)
    elif type_data == "main":
        return open_path(MAIN_FILE_PATH)
    elif type_data == "support":
        return open_path(SUPPORT_FILE_PATH)
    else:
        raise ValueError(f"Tipo de datos no válido: {type_data}")

def verify_schema(document: dict, expected: int) -> dict:
    recieved = document.get("schema_version")

    if recieved != expected: raise ValueError(f"Esquema incompatible: esperado {expected}, recibido {recieved}")
    return document["data"]

def validate_catalog_references(characters, supports, skills) -> None:
    for character_name, variants in characters.items():
        for variant_name, variant in variants.items():
            for weighted_skill in variant.ultimate_skill:
                skill_obj = weighted_skill.skill
                if skill_obj.name not in skills and skill_obj not in skills.values():
                    raise ValueError(
                        f"Ultimate desconocida '{skill_obj.name}' en "
                        f"{character_name}/{variant_name}"
                    )

    for group_name, group in supports.items():
        for support_name, support in group.items():
            for skill_name in support.skills:
                if skill_name.name not in skills and skill_name not in skills.values():
                    raise ValueError(
                        f"Skill desconocida '{skill_name.name}' en "
                        f"{group_name}/{support_name}"
                    )

def create_main_catalog(data: dict, skills: dict[str, SkillTemplate]) -> dict[str, dict[str, CharacterVariantTemplate]]:
    variants: dict[str, dict[str, CharacterVariantTemplate]] = {}
    
    for character in data: #Primer niel (Personajes)
        variant_dict = data[character]

        if character not in variants: variants[character] = {}

        for variant_name in variant_dict:
            raw_variant_data = variant_dict[variant_name] #{datos de la variante (weight, desc, etc)}

            weight = raw_variant_data["weight"]
            description = raw_variant_data["desc"]
            main_element = Elements(raw_variant_data["main_element"])
            second_element = Elements(raw_variant_data["second_element"])
            health = StatRange(minimum=raw_variant_data["health"]["min"], maximum=raw_variant_data["health"]["max"])
            attack = StatRange(minimum=raw_variant_data["attack"]["min"], maximum=raw_variant_data["attack"]["max"])
            defense = StatRange(minimum=raw_variant_data["defense"]["min"], maximum=raw_variant_data["defense"]["max"])
            weighted_skills = []
            for skill_name, skill_weight in raw_variant_data["ultimate_skill"].items():
                skill_template = skills[skill_name]
                weighted_skills.append(WeightedSkill(skill=skill_template, weight=skill_weight))
            
            ultimate_skills_tuple = tuple(weighted_skills)

            template = CharacterVariantTemplate(
                weight=weight, desc=description,
                main_element=main_element, second_element=second_element,
                health=health, attack=attack, defense=defense,
                ultimate_skill=ultimate_skills_tuple
            )

            variants[character][variant_name] = template
    return variants

def create_support_catalog(data: dict, skills: dict[str, SkillTemplate]) -> dict[str, dict[str, SupportTemplate]]:
    supports: dict[str, dict[str, SupportTemplate]] = {}

    for group in data:
        support_dict = data[group]

        if group not in supports: supports[group] = {}

        for support_name in support_dict:
            raw_support_data = support_dict[support_name]

            name = support_name
            weight = raw_support_data["weight"]
            description = raw_support_data["desc"]
            element = Elements(raw_support_data["element"])
            health = StatRange(minimum=raw_support_data["health"]["min"], maximum=raw_support_data["health"]["max"])
            attack = StatRange(minimum=raw_support_data["attack"]["min"], maximum=raw_support_data["attack"]["max"])
            defense = StatRange(minimum=raw_support_data["defense"]["min"], maximum=raw_support_data["defense"]["max"])
            skill_list = tuple(
                skills[skill_name]
                for skill_name in raw_support_data["skill_list"]
            )

            template = SupportTemplate(
                name=name, weight=weight, desc=description,
                element=element, health=health, attack=attack, defense=defense,
                skills=skill_list
            )

            supports[group][support_name] = template
    return supports

def create_skill_catalog(data) -> dict[str, SkillTemplate]:
    skills: dict[str, SkillTemplate] = {}

    for skill_name in data:

        skill_raw_data = data[skill_name]

        name = skill_raw_data["name"]
        description = skill_raw_data["desc"]
        element = Elements(skill_raw_data["element"])
        base_power = skill_raw_data["base_power"]
        skill_type = SkillTypes(skill_raw_data["skill_type"])

        template = SkillTemplate(
            name=name, desc=description, element=element,
            base_power=base_power, skill_type=skill_type
        )

        skills[skill_name] = template
    return skills

def verify_main_data():
    raw_data = open_data("main")
    data = verify_schema(raw_data, SUPPORTED_CHARACTER_VERSION)
    main_json_validator(data=data)
    return data

def verify_support_data():
    raw_data = open_data("support")
    data = verify_schema(raw_data, SUPPORTED_SUPPORT_VERSION)
    support_json_validator(data=data)
    return data

def verify_skill_data():
    raw_data = open_data("skill")
    data = verify_schema(raw_data, SUPPORTED_SKILL_VERSION)
    #main_json_validator(data=data)
    return data

def load_catalogs() -> Catalogs:
    #Verificacion de JSONs
    main_data = verify_main_data()
    support_data = verify_support_data()
    skill_data = verify_skill_data()
    #Creador de catalogos
    skill = create_skill_catalog(skill_data)
    main = create_main_catalog(main_data, skill)
    support = create_support_catalog(support_data, skill)
    validate_catalog_references(main, support, skill)
    return Catalogs(main, support, skill)

#Debug
if __name__ == "__main__":
    #Verificacion de JSONs
        main_data = verify_main_data()
        support_data = verify_support_data()
        skill_data = verify_skill_data()
        #Creador de catalogos
        skill = create_skill_catalog(skill_data)
        main = create_main_catalog(main_data, skill)
        support = create_support_catalog(support_data, skill)
        validate_catalog_references(main, support, skill)
        catalog = Catalogs(main, support, skill)
        #print(f"Estos son los personajes en catalogo: {catalog.characters}")
        print(f"Estos son los soportes en catalogo: {catalog.supports}")
        #print(f"Estos son las habilidades en catalogo: {catalog.skills}")