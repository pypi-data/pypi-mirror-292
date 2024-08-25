# tests/test_lite_json_db.py

import unittest
from LiteJsonDb.LiteJsonDb import JsonDB

class TestLiteJsonDb(unittest.TestCase):

    def setUp(self):
        # Initialiser la base de données avec le chiffrement activé
        self.db = JsonDB(crypted=True)

        # Ajouter des données initiales
        self.db.set_data("posts")  # Définir des données sans extra-data
        self.db.set_data("users/1", {"name": "Aliou", "age": 20})
        self.db.set_data("users/2", {"name": "Coder", "age": 25})

    def test_edit_data(self):
        # Modifier des données existantes
        self.db.edit_data("users/1", {"name": "Alex"})
        result = self.db.get_data("users/1")
        self.assertEqual(result, {"name": "Alex", "age": 20})

    def test_remove_data(self):
        # Supprimer des données
        self.db.remove_data("users/2")
        result = self.db.get_data("users/2")
        self.assertIsNone(result)

    def test_search_data_basic(self):
        results = self.db.search_data("Alex")
        self.assertIsInstance(results, list)  # Vérifiez que les résultats sont une liste
        self.assertIn({"name": "Alex", "age": 20}, results)

    def test_search_data_key_specific(self):
        results = self.db.search_data("Alex", key="users")
        self.assertIsInstance(results, list)  # Vérifiez que les résultats sont une liste
        self.assertIn({"name": "Alex", "age": 20}, results)

    def test_get_db(self):
        # Récupérer la base de données complète
        full_db = self.db.get_db(raw=True)
        self.assertIn("users", full_db)
        self.assertIn("posts", full_db)

    def test_subcollections(self):
        self.db.set_subcollection("groups", "1", {"name": "Admins"})
        self.db.edit_subcollection("groups", "1", {"description": "Admin group"})
        subcollection = self.db.get_subcollection("groups")
        self.assertIsInstance(subcollection, dict)  # Vérifiez que c'est un dictionnaire
        self.assertIn("1", subcollection)  # Vérifiez que la clé existe
        self.assertEqual(subcollection["1"], {"name": "Admins", "description": "Admin group"})
        self.db.remove_subcollection("groups", "1")
        subcollection = self.db.get_subcollection("groups")
        self.assertNotIn("1", subcollection)


if __name__ == "__main__":
    unittest.main()
