from .intent_config import IntentConfig

class IntentRouter:
    def __init__(self):
        self.config = IntentConfig()
    
    def route(self, intent_result):
        """根据意图结果执行路由
        
        Args:
            intent_result: 意图识别结果
            
        Returns:
            路由执行策略
        """
        intent = intent_result.get("intent", self.config.DEFAULT_INTENT)
        score = intent_result.get("score", 0.0)
        
        routes = {
            "rag_query": {
                "action": "execute_rag",
                "description": "执行完整RAG检索生成流程",
                "use_knowledge": True,
                "use_llm": True
            },
            "chat": {
                "action": "direct_chat",
                "description": "跳过向量检索，直接LLM对话生成",
                "use_knowledge": False,
                "use_llm": True
            },
            "command": {
                "action": "execute_command",
                "description": "调用任务调度模块，不触发知识库",
                "use_knowledge": False,
                "use_llm": False
            },
            "sensitive": {
                "action": "block",
                "description": "直接拦截并返回标准安全提示",
                "use_knowledge": False,
                "use_llm": False
            },
            "unknown": {
                "action": "execute_rag",
                "description": "默认进入RAG检索兜底",
                "use_knowledge": True,
                "use_llm": True
            }
        }
        
        route_info = routes.get(intent, routes[self.config.DEFAULT_INTENT])
        
        return {
            "intent": intent,
            "score": score,
            "action": route_info["action"],
            "description": route_info["description"],
            "use_knowledge": route_info["use_knowledge"],
            "use_llm": route_info["use_llm"],
            "timestamp": intent_result.get("timestamp", 0)
        }
