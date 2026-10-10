#VERSION 1.0
"""Script principal del generador de cartas y personajes.

Este módulo inicializa la carga de datos del catálogo (personajes, soportes y habilidades),
valida la estructura de los archivos de origen y proporciona una interfaz de consola de comandos 
interactiva para generar cartas sembradas (deterministas) a través de semillas del sistema.
"""
import random
from generator import generate_support, generate_main
from loader import load_catalogs
from templates import Catalogs
from inventory import save_bundle, load_bundle

def selector(catalogs: Catalogs):
    print("Bienvenido al generador de personajes y soportes.")
    print("Seleccione una opcion:")
    print("1. Generar personaje y soporte")
    print("2. Generar solo personaje")
    print("3. Generar solo soporte")
    print("4. Generar personaje por categoria")
    print("5. Generar soporte por grupo")
    print("6. Cargar cartas (DEBUG)")
    print("7. Salir")
    option = input("Opcion: ")
    match option:
        case "1":
            seed = int(input("Introduce la semilla principal: "))
            second_seed = int(input("Introduce la semilla secundaria: "))
            main(seed, second_seed, 1, catalog=catalogs)
        case "2":
            seed = int(input("Introduce la semilla principal: "))
            main(seed, None, 2, catalog=catalogs)
        case "3":
            second_seed = int(input("Introduce la semilla secundaria: "))
            main(None, second_seed, 3, catalog=catalogs)
        case "4":
            return None
        case "5":
            return None
        case "6":
            print(load_bundle())
        case "7":
            print("Saliendo...")
            exit()
        case _:
            print("Opcion no valida.")
            selector(catalogs=catalogs)

def main(character_seed: int | None, support_seed: int | None, option: int, catalog: Catalogs):
    if (character_seed is None):
        character_seed = 0
    if (support_seed is None):
        support_seed = 0
    character_rng = random.Random(character_seed)
    support_rng = random.Random(support_seed)
    special_number = round((character_seed + support_seed) / random.randint(1, 20))
    third_rng = random.Random(special_number)

    print("Numero Especial: ", special_number)
    match option:
        case 1:
            print("Generando Personaje y soporte...")
            main_card = generate_main(character_rng=character_rng, support_rng=support_rng, special_rng=third_rng,special_character=None, catalog=catalog, isCombo=True)
            print(main_card)
            save_bundle(main=main_card)
        case 2:
            print("Generando Personaje...")
            main_card = generate_main(character_rng=character_rng, support_rng=support_rng, special_rng=third_rng,special_character=None, catalog=catalog, isCombo=False)
            print(main_card)
        case 3:
            print("Generando Soporte...")
            support_card = generate_support(support_rng=support_rng, special_rng=third_rng, supports=catalog.supports, special_support_group=None)
            print(support_card)
            print("Datos DEBUG del soporte")
            print(support_card.debug_json_support())

if __name__ == "__main__":
    catalogs = load_catalogs()
    selector(catalogs)