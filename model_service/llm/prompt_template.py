"""提示词模板
功能：提供RAG和对话提示词模板
作者：
创建时间：
"""
from typing import List, Dict, Any


def build_rag_prompt(query: str, context_list: List[str]) -> str:
    """构建RAG提示词
    参数：query - 用户问题；context_list - 上下文列表
    返回：完整提示词
    被调用：rag_service.chat()
    """
    context = "\n".join([f"[{i+1}] {ctx}" for i, ctx in enumerate(context_list)])
    prompt = f"""你是一个基于文档的智能助手，请根据以下参考内容回答用户问题。

参考内容：
{context}

用户问题：{query}

要求：
1. 严格基于参考内容回答，不要添加额外信息
2. 回答要准确、简洁、有条理
3. 引用参考内容时，请标注来源编号
4. 如果参考内容中没有相关信息，请回答"根据参考内容无法回答该问题"
"""
    return prompt


def build_chat_history_prompt(history: List[Dict[str, str]], query: str, context_list: List[str]) -> str:
    """构建带历史对话的提示词
    参数：history - 历史对话；query - 当前问题；context_list - 上下文列表
    返回：完整提示词
    被调用：rag_service.chat_with_history()
    """
    # 构建历史对话
    history_str = ""
    for msg in history:
        role = "用户" if msg['role'] == 'user' else "助手"
        history_str += f"{role}: {msg['content']}\n"
    
    # 构建上下文
    context = "\n".join([f"[{i+1}] {ctx}" for i, ctx in enumerate(context_list)])
    
    prompt = f"""你是一个基于文档和历史对话的智能助手，请根据以下历史对话和参考内容回答用户的最新问题。

历史对话：
{history_str}

参考内容：
{context}

用户最新问题：{query}

要求：
1. 结合历史对话和参考内容，保持对话连贯性
2. 严格基于参考内容回答，不要添加额外信息
3. 回答要准确、简洁、有条理
4. 引用参考内容时，请标注来源编号
5. 如果参考内容中没有相关信息，请回答"根据参考内容无法回答该问题"
"""
    return prompt