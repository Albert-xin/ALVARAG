from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from service.sample_service import SampleService
from service.operation_log_service import OperationLogService
import os

router = APIRouter(prefix="/api/sample", tags=["sample"])

# 数据模型
class SampleCreate(BaseModel):
    content: str = Field(..., min_length=1)
    intent_id: int
    annotator: Optional[str] = None

class SampleUpdate(BaseModel):
    content: str = Field(..., min_length=1)
    intent_id: int
    annotator: Optional[str] = None

class SampleReview(BaseModel):
    status: str = Field(..., pattern="^(approved|rejected)$")
    reject_reason: Optional[str] = None

class BatchAnnotate(BaseModel):
    sample_ids: List[int]
    intent_id: int

class ApiResponse(BaseModel):
    code: int
    message: str
    data: Optional[Any] = None

# 模拟用户认证
def get_current_user():
    return "admin"

@router.post("/create", response_model=ApiResponse)
async def create_sample(sample: SampleCreate, current_user: str = Depends(get_current_user)):
    success, result = SampleService.create_sample(
        content=sample.content,
        intent_id=sample.intent_id,
        annotator=sample.annotator or current_user
    )
    
    # 记录操作日志
    OperationLogService.log_operation(
        operator=current_user,
        operation_type="create",
        operation_content=f"创建样本: {sample.content[:50]}...",
        operation_result="success" if success else "failure",
        target_type="sample",
        target_id=result if success else None
    )
    
    if success:
        return ApiResponse(code=200, message="创建成功", data=result)
    else:
        return ApiResponse(code=400, message=result, data=None)

@router.put("/update/{sample_id}", response_model=ApiResponse)
async def update_sample(sample_id: int, sample: SampleUpdate, current_user: str = Depends(get_current_user)):
    success, result = SampleService.update_sample(
        sample_id=sample_id,
        content=sample.content,
        intent_id=sample.intent_id,
        annotator=sample.annotator or current_user
    )
    
    # 记录操作日志
    OperationLogService.log_operation(
        operator=current_user,
        operation_type="update",
        operation_content=f"更新样本 ID: {sample_id}",
        operation_result="success" if success else "failure",
        target_type="sample",
        target_id=sample_id
    )
    
    if success:
        return ApiResponse(code=200, message="更新成功", data=None)
    else:
        return ApiResponse(code=400, message=result, data=None)

@router.delete("/delete/{sample_id}", response_model=ApiResponse)
async def delete_sample(sample_id: int, current_user: str = Depends(get_current_user)):
    success, result = SampleService.delete_sample(sample_id)
    
    # 记录操作日志
    OperationLogService.log_operation(
        operator=current_user,
        operation_type="delete",
        operation_content=f"删除样本 ID: {sample_id}",
        operation_result="success" if success else "failure",
        target_type="sample",
        target_id=sample_id
    )
    
    if success:
        return ApiResponse(code=200, message="删除成功", data=None)
    else:
        return ApiResponse(code=400, message=result, data=None)

@router.get("/get/{sample_id}", response_model=ApiResponse)
async def get_sample(sample_id: int):
    sample = SampleService.get_sample(sample_id)
    if sample:
        return ApiResponse(code=200, message="查询成功", data=sample)
    else:
        return ApiResponse(code=404, message="样本不存在", data=None)

@router.get("/list", response_model=ApiResponse)
async def get_samples(
    intent_id: Optional[int] = None,
    annotation_status: Optional[str] = None,
    duplicate_flag: Optional[bool] = None
):
    filters = {}
    if intent_id:
        filters['intent_id'] = intent_id
    if annotation_status:
        filters['annotation_status'] = annotation_status
    if duplicate_flag is not None:
        filters['duplicate_flag'] = duplicate_flag
    
    samples = SampleService.get_samples(filters)
    return ApiResponse(code=200, message="查询成功", data=samples)

@router.post("/import", response_model=ApiResponse)
async def batch_import(file: UploadFile = File(...), current_user: str = Depends(get_current_user)):
    # 保存上传的文件
    file_path = f"temp_{file.filename}"
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
    
    # 导入样本
    success, result = SampleService.batch_import(file_path)
    
    # 清理临时文件
    if os.path.exists(file_path):
        os.remove(file_path)
    
    # 记录操作日志
    OperationLogService.log_operation(
        operator=current_user,
        operation_type="import",
        operation_content=f"批量导入样本文件: {file.filename}",
        operation_result="success" if success else "failure",
        target_type="sample"
    )
    
    if success:
        return ApiResponse(code=200, message="导入成功", data=result)
    else:
        return ApiResponse(code=400, message=result, data=None)

@router.get("/export", response_model=ApiResponse)
async def batch_export(intent_id: Optional[int] = None, current_user: str = Depends(get_current_user)):
    success, result = SampleService.batch_export(intent_id)
    
    # 记录操作日志
    OperationLogService.log_operation(
        operator=current_user,
        operation_type="export",
        operation_content=f"批量导出样本，意图ID: {intent_id}",
        operation_result="success" if success else "failure",
        target_type="sample"
    )
    
    if success:
        return ApiResponse(code=200, message="导出成功", data={"file_path": result})
    else:
        return ApiResponse(code=400, message=result, data=None)

@router.post("/check_duplicate", response_model=ApiResponse)
async def check_duplicate(content: str):
    duplicates = SampleService.check_duplicates(content)
    return ApiResponse(code=200, message="检查完成", data=duplicates)

@router.post("/batch_annotate", response_model=ApiResponse)
async def batch_annotate(batch: BatchAnnotate, current_user: str = Depends(get_current_user)):
    success, result = SampleService.batch_annotate(
        sample_ids=batch.sample_ids,
        intent_id=batch.intent_id,
        annotator=current_user
    )
    
    # 记录操作日志
    OperationLogService.log_operation(
        operator=current_user,
        operation_type="update",
        operation_content=f"批量标注 {len(batch.sample_ids)} 个样本",
        operation_result="success" if success else "failure",
        target_type="sample"
    )
    
    if success:
        return ApiResponse(code=200, message="批量标注成功", data=None)
    else:
        return ApiResponse(code=400, message=result, data=None)

@router.put("/review/{sample_id}", response_model=ApiResponse)
async def review_sample(sample_id: int, review: SampleReview, current_user: str = Depends(get_current_user)):
    success, result = SampleService.review_sample(
        sample_id=sample_id,
        status=review.status,
        reject_reason=review.reject_reason
    )
    
    # 记录操作日志
    OperationLogService.log_operation(
        operator=current_user,
        operation_type="update",
        operation_content=f"审核样本 ID: {sample_id}，状态: {review.status}",
        operation_result="success" if success else "failure",
        target_type="sample",
        target_id=sample_id
    )
    
    if success:
        return ApiResponse(code=200, message="审核成功", data=None)
    else:
        return ApiResponse(code=400, message=result, data=None)
