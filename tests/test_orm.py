import os
import sys
import sqlite3
import gc
import tempfile
import unittest

# Asegurar que el path incluya src
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))
from db.orm import init_db, create_user, authenticate_user, create_conversation, add_message

class TestORM(unittest.TestCase):
    def setUp(self):
        # Crear un archivo de BD temporal único por test
        fd, path = tempfile.mkstemp(prefix="test_db_", suffix=".db")
        os.close(fd)  # cerramos descriptor, SQLite abrirá el archivo
        self.db_path = path
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
                import time
                time.sleep(0.1)
                os.remove(self.db_path)

    def test_user_flow(self):
        uid = create_user("demo_" + os.urandom(4).hex(), "pass123", self.db_path)
        self.assertIsNotNone(uid)
        user = authenticate_user("demo_" + os.path.basename(self.db_path)[-8:], "pass123", self.db_path)
        # Nota: autenticación debe usar el mismo username; mejor comprobamos que create_user crea id
        # y que authenticate_user devuelve algo al usar la username correcta.
        # Para evitar ambigüedades usaremos el mismo username:
        uname = "demo_" + os.urandom(4).hex()
        uid2 = create_user(uname, "pass123", self.db_path)
        self.assertIsNotNone(uid2)
        user2 = authenticate_user(uname, "pass123", self.db_path)
        self.assertEqual(user2['id'], uid2)

    def test_chat_flow(self):
        uname = "chat_" + os.urandom(4).hex()
        uid = create_user(uname, "pass", self.db_path)
        cid = create_conversation(uid, "Test Topic", self.db_path)
        mid = add_message(cid, "user", "Hello World", self.db_path)
        self.assertIsNotNone(mid)

if __name__ == '__main__':
    unittest.main()
