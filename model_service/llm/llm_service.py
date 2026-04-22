"""大模型生成服务
功能：提供文本生成功能
作者：
创建时间：
"""
import time
from typing import Dict, Any, Generator, List

from model_service.common.model_loader import model_loader
from model_service.common.model_config import get_model_config
from common_lib.logging.logger import get_logger

logger = get_logger(__name__)


class LLMService:
    """大模型生成服务"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LLMService, cls).__new__(cls)
        return cls._instance
    
    def init(self):
        """初始化LLM服务"""
        config = get_model_config('llm')
        self.model = model_loader.load_model('llm', config['model_path'], config['device'])
        self.max_length = config['max_length']
        logger.info("LLM服务初始化完成")
    
    def generate(self, prompt: str, params: Dict[str, Any]) -> str:
        """生成回答
        参数：prompt - 提示词；params - 生成参数
        返回：生成的回答
        被调用：rag_service.chat()
        """
        # 模拟生成过程
        time.sleep(1)  # 模拟处理时间
        answer = f"基于提示词生成的回答: {prompt[:50]}..."
        logger.info("非流式生成完成")
        return answer
    
    def generate_stream(self, prompt: str, params: Dict[str, Any]) -> Generator[str, None, None]:
        """流式生成回答
        参数：prompt - 提示词；params - 生成参数
        返回：生成的回答流
        被调用：rag_service.chat_stream()
        """
        # 模拟流式生成
        answer = f"基于提示词生成的流式回答: {prompt[:50]}..."
        for char in answer:
            yield char
            time.sleep(0.05)  # 模拟逐字生成
        logger.info("流式生成完成")
    
    def chat_completion(self, history: List[Dict[str, str]], query: str, context: str) -> str:
        """对话补全
        参数：history - 历史对话；query - 当前查询；context - 上下文
        返回：生成的回答
        被调用：rag_service.chat_with_history()
        """
        # 构建对话历史
        messages = []
        for msg in history:
            messages.append({'role': msg['role'], 'content': msg['content']})
        messages.append({'role': 'user', 'content': query})
        
        # 模拟生成
        time.sleep(1.5)
        answer = f"基于历史对话和上下文的回答: {query[:50]}..."
        logger.info("对话补全完成")
        return answer


# 全局LLM服务实例
llm_service = LLMService()