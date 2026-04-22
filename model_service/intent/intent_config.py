# 意图识别模型配置

class IntentConfig:
    # 本地模型路径
    MODEL_PATH = "/models/intent/"
    # 置信度阈值
    CONFIDENCE_THRESHOLD = 0.7
    # 推理超时时间（毫秒）
    INFERENCE_TIMEOUT = 50
    # 批量大小
    BATCH_SIZE = 8
    # 最大文本长度
    MAX_LENGTH = 64
    # 默认兜底意图
    DEFAULT_INTENT = "rag_query"
    # 意图类别列表
    INTENT_CLASSES = [
        "rag_query",  # 检索问答
        "chat",       # 闲聊
        "command",    # 指令执行
        "sensitive",  # 违规内容
        "unknown"     # 未知意图
    ]
