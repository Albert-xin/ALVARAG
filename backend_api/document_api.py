"""文档API
功能：提供文档管理相关的接口
作者：
创建时间：
"""
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Query, Request
from pydantic import BaseModel
from typing import List, Optional

from service.document_service import document_service
from common_lib.logging.logger import get_logger, set_trace_id
from common_lib.metrics import count_request

logger = get_logger(__name__)

app = FastAPI()


@app.post("/v1/document/upload")
async def upload_document(request: Request, files: List[UploadFile] = File(...)):
    """上传文档
    接口名称：POST /v1/document/upload
    实现功能：支持单文档+多文档批量上传，支持PDF/DOCX/XLSX/PPTX/TXT/MD格式；上传前校验文件格式、大小、完整性、合法性；批量文件异步并发提交解析任务，返回统一任务ID与文件处理列表
    """
    # 设置trace_id
    trace_id = request.headers.get('X-Trace-Id', 'default')
    set_trace_id(trace_id)
    
    try:
        file_paths = []
        for file in files:
            # 保存文件到临时目录
            import os
            temp_dir = os.path.join(os.path.dirname(__file__), '..', 'temp')
            os.makedirs(temp_dir, exist_ok=True)
            file_path = os.path.join(temp_dir, file.filename)
            with open(file_path, 'wb') as f:
                f.write(await file.read())
            file_paths.append(file_path)
        
        logger.info(f"接收文档上传请求，共{len(file_paths)}个文件")
        result = document_service.upload(file_paths)
        count_request("upload_document", True)
        return {
            "code": 200,
            "message": "ok",
            "data": result
        }
    except Exception as e:
        logger.error(f"上传文档失败: {e}")
        count_request("upload_document", False)
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/v1/document/list")
async def list_documents(
    request: Request,
    kb_id: Optional[str] = Query(None, description="知识库ID"),
    status: Optional[str] = Query(None, description="文档状态"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页大小")
):
    """列出文档
    接口名称：GET /v1/document/list
    实现功能：分页获取知识库内所有文档，支持按知识库ID、文档状态、上传时间、文件名筛选；返回文档ID、名称、状态、页数、分块数、入库时间、处理耗时
    """
    # 设置trace_id
    trace_id = request.headers.get('X-Trace-Id', 'default')
    set_trace_id(trace_id)
    
    try:
        filter = {}
        if kb_id:
            filter['kb_id'] = kb_id
        if status:
            filter['status'] = status
        
        logger.info(f"接收列出文档请求，筛选条件: {filter}")
        result = document_service.list_documents(filter, page, size)
        count_request("list_documents", True)
        return {
            "code": 200,
            "message": "ok",
            "data": result
        }
    except Exception as e:
        logger.error(f"列出文档失败: {e}")
        count_request("list_documents", False)
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/v1/document/detail/{doc_id}")
async def get_document_detail(request: Request, doc_id: str):
    """获取文档详情
    接口名称：GET /v1/document/detail/{doc_id}
    实现功能：查询单个文档完整详情，包含文档元数据、解析状态、分块数量、向量入库状态、解析日志、失败原因、处理节点耗时
    """
    # 设置trace_id
    trace_id = request.headers.get('X-Trace-Id', 'default')
    set_trace_id(trace_id)
    
    try:
        logger.info(f"接收获取文档详情请求: {doc_id}")
        result = document_service.get_document_detail(doc_id)
        count_request("get_document_detail", True)
        return {
            "code": 200,
            "message": "ok",
            "data": result
        }
    except Exception as e:
        logger.error(f"获取文档详情失败: {e}")
        count_request("get_document_detail", False)
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/v1/document/{doc_id}")
async def delete_document(request: Request, doc_id: str):
    """删除文档
    接口名称：DELETE /v1/document/{doc_id}
    实现功能：删除指定文档，同步删除原始文件、文本分块、向量库索引、元数据；保证数据一致性，支持幂等删除
    """
    # 设置trace_id
    trace_id = request.headers.get('X-Trace-Id', 'default')
    set_trace_id(trace_id)
    
    try:
        logger.info(f"接收删除文档请求: {doc_id}")
        result = document_service.delete_document(doc_id)
        count_request("delete_document", True)
        return {
            "code": 200,
            "message": "ok",
            "data": {"success": result}
        }
    except Exception as e:
        logger.error(f"删除文档失败: {e}")
        count_request("delete_document", False)
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/v1/document/reprocess/{doc_id}")
async def reprocess_document(request: Request, doc_id: str, file: UploadFile = File(...)):
    """重新处理文档
    接口名称：POST /v1/document/reprocess/{doc_id}
    实现功能：对指定文档重新执行全流程处理：校验→解析→分块→向量化→入库；覆盖原有向量与分块数据，更新文档状态为处理中
    """
    # 设置trace_id
    trace_id = request.headers.get('X-Trace-Id', 'default')
    set_trace_id(trace_id)
    
    try:
        # 保存文件到临时目录
        import os
        temp_dir = os.path.join(os.path.dirname(__file__), '..', 'temp')
        os.makedirs(temp_dir, exist_ok=True)
        file_path = os.path.join(temp_dir, file.filename)
        with open(file_path, 'wb') as f:
            f.write(await file.read())
        
        logger.info(f"接收重新处理文档请求: {doc_id}")
        task_id = document_service.reprocess_document(doc_id, file_path)
        count_request("reprocess_document", True)
        return {
            "code": 200,
            "message": "ok",
            "data": {"task_id": task_id}
        }
    except Exception as e:
        logger.error(f"重新处理文档失败: {e}")
        count_request("reprocess_document", False)
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)