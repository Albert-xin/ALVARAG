import threading
import time
from .intent_model import IntentModel

class IntentService:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(IntentService, cls).__new__(cls)
                    cls._instance._init_service()
        return cls._instance
    
    def _init_service(self):
        self.model = IntentModel()
    
    def get_intent(self, query):
        """获取用户查询的意图
        
        Args:
            query: 用户问题
            
        Returns:
            结构化意图结果
        """
        try:
            return self.model.predict(query)
        except Exception as e:
            # 异常时返回默认意图
            return {
                "intent": "rag_query",
                "score": 0.0,
                "model_use": False,
                "timestamp": int(time.time())
            }
