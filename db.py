import sqlite3

class ChatHistory:
    def __init__(self):
        self.conn = sqlite3.connect('chat_history.db', check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                role TEXT,
                content TEXT
            )
        ''')
        self.conn.commit()

    def save_message(self, session_id, role, content):
        self.cursor.execute('INSERT INTO history (session_id, role, content) VALUES (?, ?, ?)',
                            (session_id, role, content))
        self.conn.commit()

    def get_history(self, session_id):
        self.cursor.execute('SELECT role, content FROM history WHERE session_id = ? ORDER BY id ASC',
                            (session_id,))
        return self.cursor.fetchall()