"""Persistencia de cartas y soportes vinculados mediante UUID."""
import json
import os
import tempfile
from pathlib import Path
from uuid import UUID

from main_card import MainCard
from support_card import SupportCard

CURRENT_SCHEMA_VERSION = 1
DEFAULT_FILE_PATH = Path(__file__).resolve().parent / "datafile.json"


def _read_bundle(file_path: Path) -> dict:
    try:
        document = json.loads(file_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ValueError(f"Inventario JSON inválido: {file_path}") from exc
    if not isinstance(document, dict):
        raise ValueError("El inventario debe ser un objeto JSON")
    version = document.get("schema_version")
    if type(version) is not int or version != CURRENT_SCHEMA_VERSION:
        raise ValueError(f"Esquema incompatible: {version}")
    for key in ("main_cards", "support_cards"):
        if not isinstance(document.get(key), dict):
            raise ValueError(f"El inventario requiere un diccionario '{key}'")
    return document


def _restore_cards(document: dict) -> list[MainCard]:
    supports = {}
    cards = []
    try:
        for key, data in document["support_cards"].items():
            support = SupportCard.from_json(data)
            if key != support.id.hex:
                raise ValueError(f"UUID de soporte incompatible con su clave: {key}")
            supports[support.id] = support
        for key, data in document["main_cards"].items():
            support_id = data["support"]
            support = None if support_id is None else supports[UUID(support_id)]
            card = MainCard.from_json(data, support)
            if key != card.id.hex:
                raise ValueError(f"UUID de carta incompatible con su clave: {key}")
            cards.append(card)
    except (KeyError, TypeError, AttributeError, ValueError) as exc:
        raise ValueError(f"Datos o referencias inválidas en el inventario: {exc}") from exc
    return cards


def save_bundle(main: MainCard, file_path: str | Path = DEFAULT_FILE_PATH) -> None:
    """Añade o actualiza una carta, con soporte opcional, sin borrar las demás.

    Un inventario existente inválido se rechaza. El reemplazo atómico evita
    dejar un JSON parcial si falla la escritura.
    """
    file_path = Path(file_path)
    if file_path.exists():
        document = _read_bundle(file_path)
        _restore_cards(document)
    else:
        document = {"schema_version": CURRENT_SCHEMA_VERSION,
                    "main_cards": {}, "support_cards": {}}
    document["main_cards"][main.id.hex] = main.to_json()
    if main.support is not None:
        document["support_cards"][main.support.id.hex] = main.support.to_json()
    _restore_cards(document)
    serialized = json.dumps(document, indent=4, ensure_ascii=False, allow_nan=False)
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=file_path.parent,
            prefix=f".{file_path.name}.", suffix=".tmp", delete=False,
        ) as temporary:
            temporary_path = Path(temporary.name)
            temporary.write(serialized)
            temporary.flush()
            os.fsync(temporary.fileno())
        os.replace(temporary_path, file_path)
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def load_bundle(file_path: str | Path = DEFAULT_FILE_PATH) -> list[MainCard]:
    """Carga cartas, conserva sus UUID y resuelve soportes compartidos.

    Las estadísticas temporales se inicializan para un combate nuevo.
    """
    return _restore_cards(_read_bundle(Path(file_path)))
