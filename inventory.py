#VERSION 0.1
import json
from uuid import UUID, uuid4
from pathlib import Path

from globals import Elements, Rarity
from main_card import MainCard

CURRENT_SCHEMA_VERSION = 1

def save_bundle(main: MainCard):
    if main.support == None: raise ValueError("save_bundle necesita tener un soporte para poder funcionar.")

    file_path = Path("datafile.json")
    card_data = main.to_json()
    support_data = main.support.to_json()
    support_id = main.support.id.hex
    card_id = main.id.hex
    
    if file_path.exists() and file_path.stat().st_size > 0:
        try:
            existing_data = json.loads(file_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            existing_data = {}
    else:
        existing_data = {}

    if "schema_version" not in existing_data:
        existing_data = {
            "schema_version": CURRENT_SCHEMA_VERSION,
            "main_cards": {},
            "support_cards": {}
        }
    
    if "main_cards" not in existing_data:
        existing_data["main_cards"] = {}

    if "support_cards" not in existing_data:
        existing_data["support_cards"] = {}
    
    existing_data["schema_version"] = CURRENT_SCHEMA_VERSION
    existing_data["main_cards"][card_id] = card_data
    existing_data["support_cards"][support_id] = support_data 

    file_path.write_text(
        json.dumps(existing_data, indent=4, ensure_ascii=False), 
        encoding="utf-8"
    )

def load_bundle():
    file_path = Path("datafile.json")

    if file_path.exists() and file_path.stat().st_size > 0:
        try:
            existing_data = json.loads(file_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            raise ValueError("Los datos no se pudieron cargar")
    else: raise ValueError(f"El archivo {file_path} no existe o no tiene ningun dato")

    card_list: list[MainCard] = []

    for card in existing_data["main_cards"]: #card = str
        card_data = existing_data["main_cards"][card]
        
        id: UUID = card_data["id"]
        print(id)
        name: str = card_data["name"]
        print(name)
        desc: str = card_data["description"]
        print(desc)
        main_element: Elements = Elements(card_data["main_element"])
        print(main_element)
        second_element: Elements = Elements(card_data["second_element"])
        print(second_element)
        rarity: Rarity = Rarity(card_data["rarity"])
        print(rarity)
        stat_variation: float = card_data["stat_variation"]
        print(stat_variation)
        base_health: float = card_data["base_health"]
        print(base_health)
        base_attack: int = card_data["base_attack"]
        print(base_attack)
        base_defense: int = card_data["base_defense"]
        print(base_defense)
        mod_health: float = card_data["mod_health"]
        mod_attack: int = card_data["mod_attack"]
        mod_defense: int = card_data["mod_defense"]

        support_id: UUID = card_data["support"]

        for support in existing_data["support_cards"]:
            support_data = existing_data["support_cards"][support]
            if support_data["id"] == support_id:
                print("Viva, funciona")
                s_id: UUID = support_data["id"]
            else:
                print("Boo, no funciona")

        

    return card_list