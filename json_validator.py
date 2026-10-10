#VERISION 2.0
"""
"""

from globals import Elements, GlobalCharacters, GlobalSupportGroups

def support_json_validator(data: dict):
    required_keys = list(GlobalSupportGroups.__members__.keys())
    for key in required_keys:
        if key not in data:
            raise ValueError(f"Este soporte no fue encontrado: {key}")

    for group, supports in data.items():
        if not isinstance(supports, dict):
            raise ValueError(f"El grupo '{group}' debe de tener un diccionario de soportes valido")

        for support_name, support_data in supports.items():
            if not isinstance(support_data, dict):
                raise ValueError(f"El soporte '{support_name}' del grupo '{group}' debe de ser un diccionario")
            elif "weight" not in support_data:
                raise ValueError(f"El soporte '{support_name}' del grupo '{group}' debe de tener una clave 'weight'")
            elif not isinstance(support_data['weight'], (int,float)) or support_data["weight"] <= 0:
                raise ValueError(f"El soporte '{support_name}' del grupo '{group}' debe de tener un peso positivo")

def main_json_validator(data: dict):
    required_keys = list(GlobalCharacters.__members__.keys())
    #required_keys = ["LISBETH", "LEAH"]
    for key in required_keys:
        if key not in data:
            raise ValueError(f"Este personaje no fue encontrado: {key}")

    for character, variants in data.items():
        if not isinstance(variants, dict):
            raise ValueError(f"El personaje '{character}' debe tener un diccionario de variantes valido.")

        for variant_name, variant_data in variants.items():
            if not isinstance(variant_data, dict):
                raise ValueError(f"La variante '{variant_name}' del personaje '{character}' debe ser un diccionario.")
            elif "weight" not in variant_data:
                raise ValueError(f"La variante '{variant_name}' del personaje '{character}' debe tener una clave 'weight'.")
            elif not isinstance(variant_data["weight"], (int, float)) or variant_data["weight"] <= 0:
                raise ValueError(f"La variante '{variant_name}' del personaje '{character}' debe tener un peso positivo.")

            # Check for required keys in each variant
            required_variant_keys = ["weight", "desc", "main_element", "second_element", "health", "attack", "defense", "ultimate_skill"]
            for key in required_variant_keys:
                if key not in variant_data:
                    raise ValueError(f"La clave requerida '{key}' no se encuentra en la variante '{variant_name}' del personaje '{character}'.")

            # Validate health, attack, and defense ranges
            for stat in ["health", "attack", "defense"]:
                stat_data = variant_data[stat]
                if not isinstance(stat_data, dict) or "min" not in stat_data or "max" not in stat_data:
                    raise ValueError(f"'{stat}' en la variante '{variant_name}' del personaje '{character}' debe ser un diccionario con las claves 'min' y 'max'.")
                if stat_data["min"] > stat_data["max"]:
                    raise ValueError(f"En la variante '{variant_name}' del personaje '{character}', el valor minimo no puede ser mayor que el valor maximo para '{stat}'.")

            for skill_name, weight in variant_data["ultimate_skill"].items():
                if not isinstance(weight, (int, float)) or weight <= 0:
                    raise ValueError(f"La habilidad final '{skill_name}' en la variante '{variant_name}' del personaje '{character}' debe de tener un peso positivo.")

            for element_key in ["main_element", "second_element"]:
                element_value = variant_data[element_key]
                if not isinstance(element_value, str):
                    raise ValueError(f"EL '{element_key}' en la variante '{variant_name}' del personaje '{character}' debe ser una cadena de texto.")
                elif element_value.upper() not in [e.name for e in Elements] or element_value not in [e.name for e in Elements]:
                    raise ValueError(f"El '{element_key}' en la variante '{variant_name}' del personaje '{character}' tiene un valor invalido '{element_value}'. Debe ser uno de {[e.name for e in Elements]}.")