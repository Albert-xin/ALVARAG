from .short_term_memory import ShortTermMemory
from .long_term_memory import LongTermMemory
from .memory_config import MemoryConfig

class MemoryFuser:
    def __init__(self):
        self.config = MemoryConfig()
        self.short_term_memory = ShortTermMemory()
        self.long_term_memory = LongTermMemory()
    
    def fuse_memory(self, session_id, user_id, intent):
        """融合短期和长期记忆
        
        Args:
            session_id: 会话ID
            user_id: 用户ID
            intent: 当前意图
            
        Returns:
            融合后的记忆段
        """
        # 获取短期记忆
        session_data = self.short_term_memory.get_session(session_id)
        short_term_context = []
        
        if session_data:
            # 检查对话间隔
            current_time = int(time.time())
            time_diff = (current_time - session_data["last_time"]) / 60  # 转换为分钟
            
            if time_diff <= self.config.NEW_CONVERSATION_THRESHOLD:
                # 加载短期上下文
                for message in session_data["message_list"]:
                    short_term_context.append(f"{message['role']}: {message['content']}")
        
        # 获取长期记忆
        long_term_memories = self.long_term_memory.get_user_memories(user_id, intent)
        long_term_context = []
        
        for memory in long_term_memories:
            key_info = memory.get("key_info", {})
            if key_info:
                long_term_context.append(f"用户信息: {key_info}")
        
        # 融合记忆
        fused_context = []
        if long_term_context:
            fused_context.append("【长期记忆】")
            fused_context.extend(long_term_context)
        
        if short_term_context:
            fused_context.append("【短期对话】")
            fused_context.extend(short_term_context)
        
        # 控制总长度
        fused_text = "\n".join(fused_context)
        if len(fused_text) > self.config.MAX_MEMORY_TOKENS:
            # 截断处理
            fused_text = fused_text[:self.config.MAX_MEMORY_TOKENS]
        
        return fused_text
