import os
import sys
import sqlite3
import gc
import unittest

# Asegurar que el path incluya src
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))
from db.orm import init_db, create_user, authenticate_user, create_conversation, add_message

class TestORM(unittest.TestCase):
    def setUp(self):
        self.db_path = "test_temp.db"
        init_db(self.db_path)

    def tearDown(self):
        # Forzar cierre de conexiones activas y recolección de basura
        try:
            sqlite3.connect(self.db_path).close()
        except Exception:
            pass
        gc.collect()
        if os.path.exists(self.db_path):
            try:
                os.remove(self.db_path)
            except PermissionError:
                # Reintentar tras pequeña espera
                import time
                time.sleep(0.1)
                os.remove(self.db_path)

    def test_user_flow(self):
        uid = create_user("demo", "pass123", self.db_path)
        self.assertIsNotNone(uid)
        user = authenticate_user("demo", "pass123", self.db_path)
        self.assertEqual(user['id'], uid)

    def test_chat_flow(self):
        uid = create_user("chat_user", "pass", self.db_path)
        cid = create_conversation(uid, "Test Topic", self.db_path)
        mid = add_message(cid, "user", "Hello World", self.db_path)
        self.assertIsNotNone(mid)

if __name__ == '__main__':
    unittest.main()
