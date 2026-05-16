import sys, os
sys.path.insert(0, os.path.join(os.getcwd(),'src'))
from src.db.orm import init_db, create_user, create_conversation, add_message, get_messages

init_db()
uid = create_user('testuser','secreto123')
print('user_id', uid)
cid = create_conversation(uid, 'Prueba')
print('conv_id', cid)
mid = add_message(cid, 'user', 'Hola, esto es una prueba')
print('msg_id', mid)
print(get_messages(cid))
