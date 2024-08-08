from base64 import b64decode, b64encode
import base64
import json
import duckdb
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from ..model.user_session_model import UserSession
from ..model.chat_list_model import ChatListModel
from ..utils.single_ton import Singleton
from ..utils.log import logger
import os
import msgpack

class SessionDb(metaclass=Singleton):
    def __init__(self):
        try:
            database_dir = './database'
            if not os.path.exists(database_dir):
                os.makedirs(database_dir)
            self.conn = duckdb.connect(database='./database/sessions.db', read_only=False)
            self._create_tables()
        except Exception as e:
            logger.error(f"Error initializing SessionDb: {e}")
            # Instead of raising an exception, we'll set self.conn to None
            self.conn = None

    def _create_tables(self):
        try:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS user_sessions (
                    session_id VARCHAR PRIMARY KEY,
                    created_at TIMESTAMP,
                    expires_at TIMESTAMP,
                    last_request_time TIMESTAMP,
                    chat_history VARCHAR,
                    current_plan VARCHAR,
                    step_codes VARCHAR,
                    data VARCHAR,
                    chat_list_id VARCHAR
                )
            """)
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS chat_list (
                    session_id VARCHAR,
                    chat_list_id VARCHAR PRIMARY KEY,
                    created_at TIMESTAMP,
                    expires_at TIMESTAMP,
                    last_request_time TIMESTAMP,
                    chat_history VARCHAR,
                    current_plan VARCHAR,
                    step_codes VARCHAR,
                    data VARCHAR,
                    name VARCHAR
                )
            """)
        except Exception as e:
            logger.error(f"Error creating tables: {e}")
            raise

    def _safe_serialize(self, data: Any) -> str:
        try:
            packed = msgpack.packb(data, use_bin_type=True)
            return base64.urlsafe_b64encode(packed).decode('ascii')
        except Exception as e:
            logger.warning(f"MessagePack serialization failed, falling back to JSON: {e}")
            try:
                return json.dumps(data)
            except Exception as e:
                logger.error(f"JSON serialization also failed: {e}")
                # Instead of raising an exception, return a safe default
                return json.dumps({})

    def _safe_deserialize(self, data: Union[str, bytes, None]) -> Any:
        if data is None:
            return None
        
        if isinstance(data, bytes):
            try:
                data = data.decode('ascii', errors='replace')
            except Exception as e:
                logger.error(f"Error decoding bytes: {e}")
                return None
        
        if not isinstance(data, str):
            logger.error(f"Expected str or bytes, got {type(data)}")
            return None
        
        try:
            # Try to decode base64 and then unpack with msgpack
            decoded = base64.urlsafe_b64decode(data)
            return msgpack.unpackb(decoded, raw=False)
        except Exception as e:
            logger.warning(f"MessagePack deserialization failed, trying JSON: {e}")
            try:
                return json.loads(data)
            except json.JSONDecodeError as je:
                logger.error(f"JSON deserialization also failed: {je}")
                return None

    def _execute_query(self, query, params=None):
        if self.conn is None:
            logger.error("Database connection is not initialized")
            return None
        try:
            return self.conn.execute(query, params) if params else self.conn.execute(query)
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            return None
        
    def add_session(self, session: UserSession):
        if self.conn is None:
            logger.error("Database connection is not initialized")
            return

        with self.conn.cursor() as cursor:
            cursor.execute("BEGIN")
            try:
                cursor.execute("SELECT session_id FROM user_sessions WHERE session_id = ?", (session.session_id,))
                existing_session = cursor.fetchone()

                if existing_session:
                    cursor.execute(
                        "UPDATE user_sessions SET created_at = ?, expires_at = ?, last_request_time = ?, "
                        "chat_history = ?, current_plan = ?, step_codes = ?, data = ?, chat_list_id = ? "
                        "WHERE session_id = ?",
                        (
                            session.created_at,
                            session.expires_at,
                            session.last_request_time,
                            self._safe_serialize(session.chat_history),
                            self._safe_serialize(session.current_plan),
                            self._safe_serialize(session.step_codes),
                            self._safe_serialize(session.data),
                            session.chat_list_id,
                            session.session_id,
                        ),
                    )
                else:
                    cursor.execute(
                        "INSERT INTO user_sessions (session_id, created_at, expires_at, last_request_time, chat_history, current_plan, step_codes, data, chat_list_id) "
                        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (
                            session.session_id,
                            session.created_at,
                            session.expires_at,
                            session.last_request_time,
                            self._safe_serialize(session.chat_history),
                            self._safe_serialize(session.current_plan),
                            self._safe_serialize(session.step_codes),
                            self._safe_serialize(session.data),
                            session.chat_list_id,
                        ),
                    )
                cursor.execute("COMMIT")
            except Exception as e:
                cursor.execute("ROLLBACK")
                logger.error(f"Error in add_session: {e}")


    def get_session(self, session_id: str) -> Optional[UserSession]:
        result = self._execute_query(
            "SELECT session_id, created_at, expires_at, last_request_time, chat_history, current_plan, step_codes, data, chat_list_id FROM user_sessions WHERE session_id = ?",
            (session_id,)
        )
        if result:
            result = result.fetchone()
            if result:
                session_data = {
                    "session_id": result[0],
                    "created_at": result[1],
                    "expires_at": result[2],
                    "last_request_time": result[3],
                    "chat_history": self._safe_deserialize(result[4]),
                    "current_plan": self._safe_deserialize(result[5]),
                    "step_codes": self._safe_deserialize(result[6]),
                    "data": self._safe_deserialize(result[7]),
                    "chat_list_id": result[8]
                }
                
                try:
                    return UserSession(**session_data)
                except Exception as e:
                    logger.error(f"Error creating UserSession: {e}")
                    logger.error(f"Session data: {session_data}")
        return None

    def update_session(self, session: UserSession):
        try:
            self.conn.execute(
                "UPDATE user_sessions SET created_at = ?, expires_at = ?, last_request_time = ?, chat_history = ?, current_plan = ?, step_codes = ?, data = ?, chat_list_id = ? WHERE session_id = ?",
                (
                    session.created_at, 
                    session.expires_at, 
                    session.last_request_time, 
                    self._safe_serialize(session.chat_history), 
                    self._safe_serialize(session.current_plan), 
                    self._safe_serialize(session.step_codes), 
                    self._safe_serialize(session.data), 
                    session.chat_list_id,
                    session.session_id
                )
            )
        except Exception as e:
            logger.error(f"Error in update_session: {e}")
            raise

    def update_last_request_time(self, session_id: str, last_request_time: datetime):
        self.conn.execute(
            "UPDATE user_sessions SET last_request_time = ? WHERE session_id = ?",
            (last_request_time, session_id)
        )

    def update_chat_history(self, session_id: str, chat_history: List[dict]):
        self.conn.execute(
            "UPDATE user_sessions SET chat_history = ? WHERE session_id = ?",
            (self._safe_serialize(chat_history), session_id)
        )

    def update_current_plan(self, session_id: str, current_plan: Dict):
        self.conn.execute(
            "UPDATE user_sessions SET current_plan = ? WHERE session_id = ?",
            (self._safe_serialize(current_plan), session_id)
        )

    def update_step_codes(self, session_id: str, step_codes: Dict):
        self.conn.execute(
            "UPDATE user_sessions SET step_codes = ? WHERE session_id = ?",
            (self._safe_serialize(step_codes), session_id)
        )

    def update_data(self, session_id: str, data: Dict):
        self.conn.execute(
            "UPDATE user_sessions SET data = ? WHERE session_id = ?",
            (self._safe_serialize(data), session_id)
        )

    def get_chat_history(self, session_id: str) -> List[dict]:
        result = self.conn.execute(
            "SELECT chat_history FROM user_sessions WHERE session_id = ?",
            (session_id,)
        ).fetchone()

        if result:
            return self._safe_deserialize(result[0])
        return []

    def delete_session(self, session_id: str):
        self.conn.execute("DELETE FROM user_sessions WHERE session_id = ?", (session_id,))

    def session_exists(self, session_id: str) -> bool:
        result = self.conn.execute("SELECT 1 FROM user_sessions WHERE session_id = ?", (session_id,)).fetchone()
        return result is not None

    def cleanup_sessions(self):
        now = datetime.now()
        self.conn.execute("DELETE FROM user_sessions WHERE expires_at < ?", (now,))

    def delete_all_sessions(self):
        self.conn.execute("DELETE FROM user_sessions")

    def get_data(self, session_id: str) -> Dict[str, Any]:
        result = self.conn.execute(
            "SELECT data FROM user_sessions WHERE session_id = ?",
            (session_id,)
        ).fetchone()

        if result and result[0]:
            return self._safe_deserialize(result[0])
        return {}

    def chat_list_add_new(self, chat_list: ChatListModel):
        self.conn.execute(
            "INSERT INTO chat_list (session_id, chat_list_id, created_at, expires_at, last_request_time, chat_history, current_plan, step_codes, data, name) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                chat_list.session_id,
                chat_list.chat_list_id,
                chat_list.created_at,
                chat_list.expires_at,
                chat_list.last_request_time,
                self._safe_serialize(chat_list.chat_history),
                self._safe_serialize(chat_list.current_plan),
                self._safe_serialize(chat_list.step_codes),
                self._safe_serialize(chat_list.data),
                chat_list.name
            )
        )

    def chat_list_update(self, chat_list: ChatListModel):
        self.conn.execute(
            "UPDATE chat_list SET name = ?, created_at = ?, expires_at = ?, last_request_time = ?, chat_history = ?, current_plan = ?, step_codes = ?, data = ? WHERE chat_list_id = ?",
            (
                chat_list.name,
                chat_list.created_at,
                chat_list.expires_at,
                chat_list.last_request_time,
                self._safe_serialize(chat_list.chat_history),
                self._safe_serialize(chat_list.current_plan),
                self._safe_serialize(chat_list.step_codes),
                self._safe_serialize(chat_list.data),
                chat_list.chat_list_id
            )
        )
        
    def chat_list_save_or_update(self, chat_list: ChatListModel):
        if self.conn.execute("SELECT 1 FROM chat_list WHERE chat_list_id = ?", (chat_list.chat_list_id,)).fetchone():
            self.conn.execute(
                "UPDATE chat_list SET name = ?, created_at = ?, expires_at = ?, last_request_time = ?, chat_history = ?, current_plan = ?, step_codes = ?, data = ? WHERE chat_list_id = ?",
                (
                    chat_list.name,
                    chat_list.created_at,
                    chat_list.expires_at,
                    chat_list.last_request_time,
                    self._safe_serialize(chat_list.chat_history),
                    self._safe_serialize(chat_list.current_plan),
                    self._safe_serialize(chat_list.step_codes),
                    self._safe_serialize(chat_list.data),
                    chat_list.chat_list_id
                )
            )
        else:
            self.chat_list_add_new(chat_list)

    def chat_list_delete(self, chat_list_id: str):
        self.conn.execute("DELETE FROM chat_list WHERE chat_list_id = ?", (chat_list_id,))

    def chat_list_get_list(self, session_id: str, limit: int = 25, offset: int = 0) -> List[ChatListModel]:
        # Validate input parameters
        limit = max(1, min(limit, 100))  # Ensure limit is between 1 and 100
        offset = max(0, offset)  # Ensure offset is non-negative

        try:
            results = self._execute_query(
                """
                SELECT session_id, chat_list_id, name, created_at, expires_at, last_request_time, 
                    chat_history, current_plan, step_codes, data 
                FROM chat_list 
                WHERE session_id = ? 
                ORDER BY last_request_time DESC 
                LIMIT ? OFFSET ?
                """,
                (session_id, limit, offset)
            )
            if results:
                results = results.fetchall()
                return [
                    ChatListModel(
                        session_id=row[0],
                        chat_list_id=row[1],
                        name=row[2],
                        created_at=row[3],
                        expires_at=row[4],
                        last_request_time=row[5],
                        chat_history=self._safe_deserialize(row[6]),
                        current_plan=self._safe_deserialize(row[7]),
                        step_codes=self._safe_deserialize(row[8]),
                        data=self._safe_deserialize(row[9])
                    ) for row in results
                ]
        except Exception as e:
            logger.error(f"Error in chat_list_get_list: {e}")
        return []  # Return an empty list in case of error
    
    def chat_list_get_one(self, chat_list_id: str) -> Optional[ChatListModel]:
        result = self.conn.execute(
            "SELECT session_id, chat_list_id, name, created_at, expires_at, last_request_time, chat_history, current_plan, step_codes, data FROM chat_list WHERE chat_list_id = ?",
            (chat_list_id,)
        ).fetchone()

        if result:
            return ChatListModel(
                session_id=result[0],
                chat_list_id=result[1],
                name=result[2],
                created_at=result[3],
                expires_at=result[4],
                last_request_time=result[5],
                chat_history=self._safe_deserialize(result[6]),
                current_plan=self._safe_deserialize(result[7]),
                step_codes=self._safe_deserialize(result[8]),
                data=self._safe_deserialize(result[9])
            )
        return None
    
    def chat_list_is_id_exists(self, chat_list_id: str) -> bool:
        result = self.conn.execute("SELECT 1 FROM chat_list WHERE chat_list_id = ?", (chat_list_id,)).fetchone()
        return result is not None

    def close_connection(self):
        if self.conn:
            try:
                self.conn.close()
            except Exception as e:
                logger.error(f"Error closing database connection: {e}")
            finally:
                self.conn = None