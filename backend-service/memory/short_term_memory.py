import redis
import json
import time
from .memory_config import MemoryConfig

class ShortTermMemory:
    def __init__(self):
        self.config = MemoryConfig()
        try:
            self.redis_client = redis.from_url(self.config.REDIS_URL)
        except Exception as e:
            # Redis连接失败时使用内存存储作为降级
            self.redis_client = None
            self.memory_store = {}
    
    def _get_session_key(self, session_id):
        return f"session:{session_id}"
    
    def add_message(self, session_id, user_id, role, content):
        """添加消息到短期记忆
        
        Args:
            session_id: 会话ID
            user_id: 用户ID
            role: 角色（user/assistant）
            content: 消息内容
        """
        message = {
            "role": role,
            "content": content,
            "timestamp": int(time.time())
        }
        
        session_data = self.get_session(session_id)
        if not session_data:
            session_data = {
                "session_id": session_id,
                "user_id": user_id,
                "message_list": [],
                "last_time": int(time.time()),
                "max_turns": self.config.MAX_SHORT_TERM_TURNS
            }
        
        # 检查对话间隔
        current_time = int(time.time())
        time_diff = (current_time - session_data["last_time"]) / 60  # 转换为分钟
        if time_diff > self.config.NEW_CONVERSATION_THRESHOLD:
            # 超过阈值，视为新对话
            session_data["message_list"] = []
        
        # 添加新消息
        session_data["message_list"].append(message)
        session_data["last_time"] = current_time
        
        # 截断超过最大轮数的旧消息
        if len(session_data["message_list"]) > self.config.MAX_SHORT_TERM_TURNS:
            session_data["message_list"] = session_data["message_list"][-self.config.MAX_SHORT_TERM_TURNS:]
        
        # 保存到Redis
        if self.redis_client:
            try:
                session_key = self._get_session_key(session_id)
                self.redis_client.setex(
                    session_key,
                    self.config.SHORT_TERM_EXPIRY * 60,  # 转换为秒
                    json.dumps(session_data)
                )
            except Exception:
                # Redis保存失败，使用内存存储
                self.memory_store[session_id] = session_data
        else:
            self.memory_store[session_id] = session_data
    
    def get_session(self, session_id):
        """获取会话数据
        
        Args:
            session_id: 会话ID
            
        Returns:
            会话数据
        """
        if self.redis_client:
            try:
                session_key = self._get_session_key(session_id)
                data = self.redis_client.get(session_key)
                if data:
                    return json.loads(data)
            except Exception:
                pass
        
        # 从内存存储获取
        return self.memory_store.get(session_id)
    
    def clear_session(self, session_id):
        """清空会话数据
        
        Args:
            session_id: 会话ID
        """
        if self.redis_client:
            try:
                session_key = self._get_session_key(session_id)
                self.redis_client.delete(session_key)
            except Exception:
                pass
        
        # 从内存存储删除
        if session_id in self.memory_store:
            del self.memory_store[session_id]
