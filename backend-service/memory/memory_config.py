# 对话记忆模块配置

class MemoryConfig:
    # 最大短期轮数
    MAX_SHORT_TERM_TURNS = 10
    # 短期过期时间（分钟）
    SHORT_TERM_EXPIRY = 30
    # 新对话间隔阈值（分钟）
    NEW_CONVERSATION_THRESHOLD = 10
    # 总结触发轮数
    SUMMARY_TRIGGER_TURNS = 8
    # 最大记忆token
    MAX_MEMORY_TOKENS = 800
    # 存储路径
    REDIS_URL = "redis://localhost:6379/0"
    DATABASE_URL = "postgresql://user:password@localhost:5432/alvarag"
