"""检索API
功能：提供向量检索相关的接口
作者：
创建时间：
"""
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import List, Dict, Any

from service.rag_service import rag_service
from common_lib.logging.logger import get_logger, set_trace_id
from common_lib.metrics import count_request

logger = get_logger(__name__)

app = FastAPI()


class RetrieveRequest(BaseModel):
    """检索请求"""
    query: str
    kb_id: str
    top_k: int = 5


class RetrieveBatchRequest(BaseModel):
    """批量检索请求"""
    queries: List[str]
    kb_id: str
    top_k: int = 5


@app.post("/v1/retrieve/query")
async def retrieve_query(request: Request, req: RetrieveRequest):
    """纯向量检索接口
    接口名称：POST /v1/retrieve/query
    实现功能：纯向量检索接口；接收用户查询词、知识库ID、召回数量；生成Embedding向量并从向量库召回相关文本块；返回分块内容、来源文档、页码、相似度分数
    """
    # 设置trace_id
    trace_id = request.headers.get('X-Trace-Id', 'default')
    set_trace_id(trace_id)
    
    try:
        logger.info(f"接收纯向量检索请求: {req.query}")
        results = rag_service.retrieve(req.query, req.kb_id, req.top_k)
        count_request("retrieve_query", True)
        return {
            "code": 200,
            "message": "ok",
            "data": results
        }
    except Exception as e:
        logger.error(f"纯向量检索失败: {e}")
        count_request("retrieve_query", False)
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/v1/retrieve/rerank")
async def retrieve_rerank(request: Request, req: RetrieveRequest):
    """检索+重排接口
    接口名称：POST /v1/retrieve/rerank
    实现功能：检索+重排接口；先执行向量粗排，再调用Rerank模型精排；按相关性分数从高到低排序；支持配置返回Top-K数量，结果更精准
    """
    # 设置trace_id
    trace_id = request.headers.get('X-Trace-Id', 'default')
    set_trace_id(trace_id)
    
    try:
        logger.info(f"接收检索+重排请求: {req.query}")
        results = rag_service.retrieve_rerank(req.query, req.kb_id, req.top_k)
        count_request("retrieve_rerank", True)
        return {
            "code": 200,
            "message": "ok",
            "data": results
        }
    except Exception as e:
        logger.error(f"检索+重排失败: {e}")
        count_request("retrieve_rerank", False)
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/v1/retrieve/batch")
async def retrieve_batch(request: Request, req: RetrieveBatchRequest):
    """批量检索接口
    接口名称：POST /v1/retrieve/batch
    实现功能：批量检索接口；支持传入多个查询词并行检索；每个查询词独立执行检索+重排流程；批量返回结果，提升多query处理效率
    """
    # 设置trace_id
    trace_id = request.headers.get('X-Trace-Id', 'default')
    set_trace_id(trace_id)
    
    try:
        logger.info(f"接收批量检索请求，共{len(req.queries)}个查询")
        results = rag_service.retrieve_batch(req.queries, req.kb_id, req.top_k)
        count_request("retrieve_batch", True)
        return {
            "code": 200,
            "message": "ok",
            "data": results
        }
    except Exception as e:
        logger.error(f"批量检索失败: {e}")
        count_request("retrieve_batch", False)
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)