"""聊天API
功能：提供RAG聊天相关的接口
作者：
创建时间：
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Any

from service.rag_service import rag_service
from common_lib.logging.logger import get_logger, set_trace_id
from common_lib.metrics import count_request

logger = get_logger(__name__)

app = FastAPI()


class ChatRequest(BaseModel):
    """聊天请求"""
    query: str
    kb_id: str
    retrieve_params: Dict[str, Any] = {}


class ChatHistoryRequest(BaseModel):
    """带历史对话的聊天请求"""
    history: List[Dict[str, str]]
    query: str
    kb_id: str
    retrieve_params: Dict[str, Any] = {}


@app.post("/v1/rag/chat")
async def chat(request: Request, req: ChatRequest):
    """非流式RAG问答接口
    接口名称：POST /v1/rag/chat
    实现功能：非流式RAG问答接口；接收用户问题、知识库ID、检索参数；执行问题优化、Embedding、向量检索、Rerank重排、上下文拼接、LLM生成；一次性返回回答文本、参考文档列表、检索元信息
    """
    # 设置trace_id
    trace_id = request.headers.get('X-Trace-Id', 'default')
    set_trace_id(trace_id)
    
    try:
        logger.info(f"接收非流式RAG问答请求: {req.query}")
        result = rag_service.chat(req.query, req.kb_id, req.retrieve_params)
        count_request("chat", True)
        return {
            "code": 200,
            "message": "ok",
            "data": result
        }
    except Exception as e:
        logger.error(f"非流式RAG问答失败: {e}")
        count_request("chat", False)
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/v1/rag/chat/stream")
async def chat_stream(request: Request, req: ChatRequest):
    """流式RAG问答接口
    接口名称：POST /v1/rag/chat/stream
    实现功能：流式RAG问答接口；基于SSE协议实时推送回答内容；支持前端逐字接收输出；结束帧返回完整参考文档；支持中断信号、超时控制、异常兜底返回
    """
    # 设置trace_id
    trace_id = request.headers.get('X-Trace-Id', 'default')
    set_trace_id(trace_id)
    
    logger.info(f"接收流式RAG问答请求: {req.query}")
    
    def generate():
        try:
            for chunk in rag_service.chat_stream(req.query, req.kb_id, req.retrieve_params):
                import json
                yield f"data: {json.dumps(chunk)}\n\n"
            count_request("chat_stream", True)
        except Exception as e:
            logger.error(f"流式RAG问答失败: {e}")
            count_request("chat_stream", False)
            import json
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")


@app.post("/v1/rag/chat/with_history")
async def chat_with_history(request: Request, req: ChatHistoryRequest):
    """带多轮对话历史的RAG问答
    接口名称：POST /v1/rag/chat/with_history
    实现功能：带多轮对话历史的RAG问答；接收历史消息列表+当前问题；自动对历史对话进行压缩、去噪、摘要；基于完整上下文做检索与生成；保持对话连贯性
    """
    # 设置trace_id
    trace_id = request.headers.get('X-Trace-Id', 'default')
    set_trace_id(trace_id)
    
    try:
        logger.info(f"接收带历史对话的RAG问答请求")
        result = rag_service.chat_with_history(req.history, req.query, req.kb_id, req.retrieve_params)
        count_request("chat_with_history", True)
        return {
            "code": 200,
            "message": "ok",
            "data": result
        }
    except Exception as e:
        logger.error(f"带历史对话的RAG问答失败: {e}")
        count_request("chat_with_history", False)
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)