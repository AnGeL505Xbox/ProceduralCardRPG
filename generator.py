#VERSION 2.0
"""Modulo de generacion de cartas (MainCard y SupportCard)."""
import random
from globals import GlobalCharacters, GlobalSupportGroups, select_rarity, apply_modifier, select_weighted_skill, select_weighted_template
from main_card import MainCard
from support_card import SupportCard
from templates import Catalogs, SupportTemplate, CharacterVariantTemplate

def generate_support(support_rng: random.Random, special_rng: random.Random, supports: dict, special_support_group: GlobalSupportGroups | None) -> SupportCard:
    if special_support_group: group_name = special_support_group
    else: group_name = support_rng.choice(list(GlobalSupportGroups))

    rarity = select_rarity(support_rng)
    modifier = rarity.modifier
    modifier_extra = special_rng.uniform(0.00, 0.16)

    group_selected = supports[group_name.name]
    name = select_weighted_template(support_rng, group_selected)
    template: SupportTemplate = group_selected[name]

    name = template.name
    description = template.desc
    element = template.element
    base_health = support_rng.uniform(template.health.minimum, template.health.maximum)
    base_attack = support_rng.randint(int(template.attack.minimum), int(template.attack.maximum))
    base_defense = support_rng.randint(int(template.defense.minimum), int(template.defense.maximum))

    mod_health = apply_modifier(base_health, modifier, modifier_extra)
    mod_attack = apply_modifier(base_attack, modifier, modifier_extra)
    mod_defense = apply_modifier(base_defense, modifier, modifier_extra)

    skill_list = template.skills

    support = SupportCard(
        name=name, desc=description, element=element,
        rarity=rarity, stat_variation=modifier_extra,
        base_health=base_health, base_attack=base_attack, base_defense=base_defense,
        mod_health=mod_health, mod_attack=mod_attack, mod_defense=mod_defense,
        skill_list=skill_list
    )
    return support

def generate_main(character_rng: random.Random, support_rng: random.Random, special_rng: random.Random, special_character: GlobalCharacters | None, catalog: Catalogs, isCombo: bool) -> MainCard:
    if special_character: group_name = special_character
    else: group_name = character_rng.choice(list(GlobalCharacters))

    rarity = select_rarity(character_rng)
    modifier = rarity.modifier
    modifier_extra = special_rng.uniform(0.00, 0.32)

    templates = catalog.characters[group_name.name]
    name = select_weighted_template(character_rng, templates)
    template: CharacterVariantTemplate = templates[name]

    description = template.desc
    main_element = template.main_element
    second_element = template.second_element

    if isCombo: support = generate_support(support_rng=support_rng, special_rng=special_rng, supports=catalog.supports,special_support_group=None)
    else: support = None

    base_health = character_rng.uniform(template.health.minimum, template.health.maximum)
    base_attack = character_rng.randint(int(template.attack.minimum), int(template.attack.maximum))
    base_defense = character_rng.randint(int(template.defense.minimum), int(template.defense.maximum))

    mod_health = apply_modifier(base_health, modifier, modifier_extra)
    mod_attack = apply_modifier(base_attack, modifier, modifier_extra)
    mod_defense = apply_modifier(base_defense, modifier, modifier_extra)

    ultimate_skill = select_weighted_skill(character_rng, template.ultimate_skill)

    card = MainCard(
        name=(group_name.name+" - "+name), desc=description,
        main_element=main_element, second_element=second_element, rarity=rarity,
        support=support, stat_variation=modifier_extra, 
        base_health=base_health, base_attack=base_attack, base_defense=base_defense,
        mod_health=mod_health, mod_attack=mod_attack, mod_defense=mod_defense,
        ultimate_skill=ultimate_skill
    )
    return card