"""任务API
功能：提供任务管理相关的接口
作者：
创建时间：
"""
from fastapi import FastAPI, HTTPException, Request, Query
from typing import Optional

from service.task_service import task_service
from common_lib.logging.logger import get_logger, set_trace_id
from common_lib.metrics import count_request

logger = get_logger(__name__)

app = FastAPI()


@app.get("/v1/task/status/{task_id}")
async def get_task_status(request: Request, task_id: str):
    """获取任务状态
    接口名称：GET /v1/task/status/{task_id}
    实现功能：查询异步任务执行状态；返回任务ID、任务类型、处理进度、状态（等待/运行中/成功/失败）、失败原因、耗时、关联文档ID
    """
    # 设置trace_id
    trace_id = request.headers.get('X-Trace-Id', 'default')
    set_trace_id(trace_id)
    
    try:
        logger.info(f"接收获取任务状态请求: {task_id}")
        result = task_service.get_task_status(task_id)
        count_request("get_task_status", True)
        return {
            "code": 200,
            "message": "ok",
            "data": result
        }
    except Exception as e:
        logger.error(f"获取任务状态失败: {e}")
        count_request("get_task_status", False)
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/v1/task/list")
async def list_tasks(
    request: Request,
    status: Optional[str] = Query(None, description="任务状态"),
    task_type: Optional[str] = Query(None, description="任务类型"),
    doc_id: Optional[str] = Query(None, description="文档ID"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页大小")
):
    """列出任务
    接口名称：GET /v1/task/list
    实现功能：分页查询任务列表；支持按任务类型、状态、时间范围、文档ID筛选；返回任务集合、总数、分页信息
    """
    # 设置trace_id
    trace_id = request.headers.get('X-Trace-Id', 'default')
    set_trace_id(trace_id)
    
    try:
        filter = {}
        if status:
            filter['status'] = status
        if task_type:
            filter['type'] = task_type
        if doc_id:
            filter['doc_id'] = doc_id
        
        logger.info(f"接收列出任务请求，筛选条件: {filter}")
        result = task_service.list_tasks(filter, page, size)
        count_request("list_tasks", True)
        return {
            "code": 200,
            "message": "ok",
            "data": result
        }
    except Exception as e:
        logger.error(f"列出任务失败: {e}")
        count_request("list_tasks", False)
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/v1/task/retry/{task_id}")
async def retry_task(request: Request, task_id: str):
    """重试任务
    接口名称：POST /v1/task/retry/{task_id}
    实现功能：重试指定失败任务；仅支持状态为“失败”的任务；幂等安全，重新触发解析/入库/索引流程；更新任务状态为运行中
    """
    # 设置trace_id
    trace_id = request.headers.get('X-Trace-Id', 'default')
    set_trace_id(trace_id)
    
    try:
        logger.info(f"接收重试任务请求: {task_id}")
        new_task_id = task_service.retry_task(task_id)
        count_request("retry_task", True)
        return {
            "code": 200,
            "message": "ok",
            "data": {"task_id": new_task_id}
        }
    except Exception as e:
        logger.error(f"重试任务失败: {e}")
        count_request("retry_task", False)
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/v1/task/cancel/{task_id}")
async def cancel_task(request: Request, task_id: str):
    """取消任务
    接口名称：POST /v1/task/cancel/{task_id}
    实现功能：取消正在执行的异步任务；终止任务执行、释放内存与文件句柄；标记任务状态为已取消，不继续后续处理
    """
    # 设置trace_id
    trace_id = request.headers.get('X-Trace-Id', 'default')
    set_trace_id(trace_id)
    
    try:
        logger.info(f"接收取消任务请求: {task_id}")
        result = task_service.cancel_task(task_id)
        count_request("cancel_task", True)
        return {
            "code": 200,
            "message": "ok",
            "data": {"success": result}
        }
    except Exception as e:
        logger.error(f"取消任务失败: {e}")
        count_request("cancel_task", False)
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)