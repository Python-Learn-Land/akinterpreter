import json
import duckdb
from datetime import datetime
from typing import Any, Dict, List, Optional
from ..model.user_session_model import UserSession
from ..utils.single_ton import Singleton
import os

class SessionDb(metaclass=Singleton):
    def __init__(self):
        # Check if the database directory exists, if not, create it
        database_dir = './database'
        if not os.path.exists(database_dir):
            os.makedirs(database_dir)
        self.conn = duckdb.connect(database='./database/sessions.db', read_only=False)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS user_sessions (
                session_id VARCHAR PRIMARY KEY,
                created_at TIMESTAMP,
                expires_at TIMESTAMP,
                last_request_time TIMESTAMP,
                chat_history JSON,
                current_plan JSON,
                step_codes JSON,
                data JSON
            )
        """)

    def _encode_json(self, data):
        """Ensure the JSON data is properly encoded."""
        return json.dumps(data, ensure_ascii=False)

    def _decode_json(self, data):
        return json.loads(data)

    def add_session(self, session: UserSession):
        self.conn.execute(
            "INSERT INTO user_sessions (session_id, created_at, expires_at, last_request_time, chat_history, current_plan, step_codes, data) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                session.session_id,
                session.created_at,
                session.expires_at,
                session.last_request_time,
                self._encode_json(session.chat_history),
                self._encode_json(session.current_plan),
                self._encode_json(session.step_codes),
                self._encode_json(session.data)
            )
        )

    def get_session(self, session_id: str) -> Optional[UserSession]:
        result = self.conn.execute(
            "SELECT session_id, created_at, expires_at, last_request_time, chat_history, current_plan, step_codes, data FROM user_sessions WHERE session_id = ?",
            (session_id,)
        ).fetchone()

        if result:
            return UserSession(
                session_id=result[0],
                created_at=result[1],
                expires_at=result[2],
                last_request_time=result[3],
                chat_history=self._decode_json(result[4]),  # 解码 JSON 字符串
                current_plan=self._decode_json(result[5]),  # 解码 JSON 字符串
                step_codes=self._decode_json(result[6]),  # 解码 JSON 字符串
                data=self._decode_json(result[7])  # 解码 JSON 字符串
            )
        return None

    def update_session(self, session: UserSession):
        self.conn.execute(
            "UPDATE user_sessions SET created_at = ?, expires_at = ?, last_request_time = ?, chat_history = ?, current_plan = ?, step_codes = ?, data = ? WHERE session_id = ?",
            (
                session.created_at, 
                session.expires_at, 
                session.last_request_time, 
                self._encode_json(session.chat_history), 
                self._encode_json(session.current_plan), 
                self._encode_json(session.step_codes), 
                self._encode_json(session.data), 
                session.session_id
            )
        )

    def update_last_request_time(self, session_id: str, last_request_time: datetime):
        self.conn.execute(
            "UPDATE user_sessions SET last_request_time = ? WHERE session_id = ?",
            (last_request_time, session_id)
        )

    def update_chat_history(self, session_id: str, chat_history: List[dict]):
        self.conn.execute(
            "UPDATE user_sessions SET chat_history = ? WHERE session_id = ?",
            (self._encode_json(chat_history), session_id)
        )

    def update_current_plan(self, session_id: str, current_plan: Dict):
        self.conn.execute(
            "UPDATE user_sessions SET current_plan = ? WHERE session_id = ?",
            (self._encode_json(current_plan), session_id)
        )

    def update_step_codes(self, session_id: str, step_codes: Dict):
        self.conn.execute(
            "UPDATE user_sessions SET step_codes = ? WHERE session_id = ?",
            (self._encode_json(step_codes), session_id)
        )

    def update_data(self, session_id: str, data: Dict):
        self.conn.execute(
            "UPDATE user_sessions SET data = ? WHERE session_id = ?",
            (self._encode_json(data), session_id)
        )

    def get_data(self, session_id: str) -> Dict[str, Any]:
        result = self.conn.execute(
            "SELECT data FROM user_sessions WHERE session_id = ?",
            (session_id,)
        ).fetchone()

        if result:
            return self._decode_json(result[0])
        return {}
    
    def delete_session(self, session_id: str):
        self.conn.execute("DELETE FROM user_sessions WHERE session_id = ?", (session_id,))

    def session_exists(self, session_id: str) -> bool:
        result = self.conn.execute("SELECT 1 FROM user_sessions WHERE session_id = ?", (session_id,)).fetchone()
        return result is not None

    def cleanup_sessions(self):
        now = datetime.now()
        self.conn.execute("DELETE FROM user_sessions WHERE expires_at < ?", (now,))

    def get_chat_history(self, session_id: str) -> List[dict]:
        result = self.conn.execute(
            "SELECT chat_history FROM user_sessions WHERE session_id = ?",
            (session_id,)
        ).fetchone()

        if result:
            return self._decode_json(result[0])
        return []

    def delete_all_sessions(self):
        """Delete all sessions from the database."""
        self.conn.execute("DELETE FROM user_sessions")