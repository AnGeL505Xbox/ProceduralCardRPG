import json
import random
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from generator import generate_main
from inventory import load_bundle, save_bundle
from loader import load_catalogs
from main_card import MainCard
from support_card import SupportCard
from templates import SkillTemplate


class SerializationTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / 'inventory.json'
        self.catalog = load_catalogs()

    def card(self, combo=True, seed=1):
        return generate_main(random.Random(seed), random.Random(seed+1),
                             random.Random(seed+2), None, self.catalog, combo)

    def test_serializers(self):
        card = self.card()
        skill = card.ultimate_skill
        self.assertEqual(skill, SkillTemplate.from_json(json.loads(json.dumps(skill.to_json()))))
        support = SupportCard.from_json(json.loads(json.dumps(card.support.to_json())))
        self.assertEqual(card.support, support)
        restored = MainCard.from_json(json.loads(json.dumps(card.to_json())), support)
        self.assertEqual(card, restored)
        with self.assertRaises(ValueError):
            MainCard.from_json(card.to_json())

    def test_append_update_shared_support_and_no_support(self):
        first, second, third = self.card(), self.card(seed=5), self.card(False)
        second.support = first.support
        second.apply_support()
        for card in (first, second, third, first):
            save_bundle(card, self.path)
        loaded = load_bundle(self.path)
        self.assertEqual([first, second, third], loaded)
        self.assertIs(loaded[0].support, loaded[1].support)
        self.assertIsNone(loaded[2].support)
        self.assertEqual(len(json.loads(self.path.read_text())['support_cards']), 1)

    def test_invalid_inventory_is_preserved(self):
        card = self.card()
        save_bundle(card, self.path)
        valid = json.loads(self.path.read_text())
        incompatible = dict(valid, schema_version=999)
        missing_support = dict(valid, support_cards={})
        wrong_id = json.loads(json.dumps(valid))
        wrong_id['main_cards']['wrong-key'] = wrong_id['main_cards'].pop(card.id.hex)
        for contents in ('{broken', '', json.dumps(incompatible),
                         json.dumps(missing_support), json.dumps(wrong_id)):
            with self.subTest(contents=contents):
                self.path.write_text(contents)
                with self.assertRaises(ValueError):
                    load_bundle(self.path)
                with self.assertRaises(ValueError):
                    save_bundle(card, self.path)
                self.assertEqual(contents, self.path.read_text())

    def test_failed_replace_preserves_file_and_cleans_temporary(self):
        card = self.card()
        save_bundle(card, self.path)
        original = self.path.read_bytes()
        with patch('inventory.os.replace', side_effect=OSError('write failed')):
            with self.assertRaises(OSError):
                save_bundle(self.card(seed=8), self.path)
        self.assertEqual(original, self.path.read_bytes())
        self.assertEqual([self.path], list(self.path.parent.iterdir()))

    def test_combat_state_resets_on_load(self):
        card = self.card()
        initial_health = card.temp_health
        card.take_damage(1000, 1)
        save_bundle(card, self.path)
        self.assertEqual(load_bundle(self.path)[0].temp_health, initial_health)

    def test_missing_file(self):
        with self.assertRaises(FileNotFoundError):
            load_bundle(self.path)


if __name__ == '__main__':
    unittest.main()
