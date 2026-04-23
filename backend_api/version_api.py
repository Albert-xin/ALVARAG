from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional, List, Any
from service.version_service import VersionService
from service.operation_log_service import OperationLogService

router = APIRouter(prefix="/api/version", tags=["version"])

class ApiResponse(BaseModel):
    code: int
    message: str
    data: Optional[Any] = None

# 模拟用户认证
def get_current_user():
    return "admin"

@router.get("/list/{intent_id}", response_model=ApiResponse)
async def get_versions(intent_id: int):
    versions = VersionService.get_versions(intent_id)
    return ApiResponse(code=200, message="查询成功", data=versions)

@router.get("/get/{version_id}", response_model=ApiResponse)
async def get_version(version_id: int):
    version = VersionService.get_version(version_id)
    if version:
        return ApiResponse(code=200, message="查询成功", data=version)
    else:
        return ApiResponse(code=404, message="版本不存在", data=None)

@router.get("/compare", response_model=ApiResponse)
async def compare_versions(version_id1: int, version_id2: int):
    success, result = VersionService.compare_versions(version_id1, version_id2)
    if success:
        return ApiResponse(code=200, message="对比成功", data=result)
    else:
        return ApiResponse(code=400, message=result, data=None)

@router.post("/rollback/{version_id}", response_model=ApiResponse)
async def rollback_to_version(version_id: int, current_user: str = Depends(get_current_user)):
    success, result = VersionService.rollback_to_version(version_id, current_user)
    
    # 记录操作日志
    OperationLogService.log_operation(
        operator=current_user,
        operation_type="update",
        operation_content=f"回滚到版本 ID: {version_id}",
        operation_result="success" if success else "failure",
        target_type="version",
        target_id=version_id
    )
    
    if success:
        return ApiResponse(code=200, message="回滚成功", data=None)
    else:
        return ApiResponse(code=400, message=result, data=None)

@router.post("/publish/{version_id}", response_model=ApiResponse)
async def publish_version(version_id: int, current_user: str = Depends(get_current_user)):
    success, result = VersionService.publish_version(version_id, current_user)
    
    # 记录操作日志
    OperationLogService.log_operation(
        operator=current_user,
        operation_type="update",
        operation_content=f"发布版本 ID: {version_id}",
        operation_result="success" if success else "failure",
        target_type="version",
        target_id=version_id
    )
    
    if success:
        return ApiResponse(code=200, message="发布成功", data=None)
    else:
        return ApiResponse(code=400, message=result, data=None)
