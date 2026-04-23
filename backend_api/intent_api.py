from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from service.intent_service import IntentService
from service.operation_log_service import OperationLogService

router = APIRouter(prefix="/api/intent", tags=["intent"])

# 数据模型
class IntentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    parent_id: Optional[int] = None
    domain: str = Field(default="general", pattern="^(general|scientific)$")

class IntentUpdate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    parent_id: Optional[int] = None

class IntentStatus(BaseModel):
    status: str = Field(..., pattern="^(enabled|disabled)$")

class IntentResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    parent_id: Optional[int]
    created_by: str
    created_at: str
    updated_at: str
    status: str
    domain: str
    sort_order: int

class ApiResponse(BaseModel):
    code: int
    message: str
    data: Optional[Any] = None

# 模拟用户认证（实际项目中应使用真实的认证机制）
def get_current_user():
    # 这里应该从请求中获取用户信息，这里简化处理
    return "admin"

@router.post("/create", response_model=ApiResponse)
async def create_intent(intent: IntentCreate, current_user: str = Depends(get_current_user)):
    success, result = IntentService.create_intent(
        name=intent.name,
        description=intent.description,
        parent_id=intent.parent_id,
        created_by=current_user,
        domain=intent.domain
    )
    
    # 记录操作日志
    OperationLogService.log_operation(
        operator=current_user,
        operation_type="create",
        operation_content=f"创建意图: {intent.name}",
        operation_result="success" if success else "failure",
        target_type="intent",
        target_id=result if success else None
    )
    
    if success:
        return ApiResponse(code=200, message="创建成功", data=result)
    else:
        return ApiResponse(code=400, message=result, data=None)

@router.put("/update/{intent_id}", response_model=ApiResponse)
async def update_intent(intent_id: int, intent: IntentUpdate, current_user: str = Depends(get_current_user)):
    success, result = IntentService.update_intent(
        intent_id=intent_id,
        name=intent.name,
        description=intent.description,
        parent_id=intent.parent_id,
        updated_by=current_user
    )
    
    # 记录操作日志
    OperationLogService.log_operation(
        operator=current_user,
        operation_type="update",
        operation_content=f"更新意图: {intent.name}",
        operation_result="success" if success else "failure",
        target_type="intent",
        target_id=intent_id
    )
    
    if success:
        return ApiResponse(code=200, message="更新成功", data=None)
    else:
        return ApiResponse(code=400, message=result, data=None)

@router.delete("/delete/{intent_id}", response_model=ApiResponse)
async def delete_intent(intent_id: int, current_user: str = Depends(get_current_user)):
    success, result = IntentService.delete_intent(intent_id, current_user)
    
    # 记录操作日志
    OperationLogService.log_operation(
        operator=current_user,
        operation_type="delete",
        operation_content=f"删除意图 ID: {intent_id}",
        operation_result="success" if success else "failure",
        target_type="intent",
        target_id=intent_id
    )
    
    if success:
        return ApiResponse(code=200, message="删除成功", data=None)
    else:
        return ApiResponse(code=400, message=result, data=None)

@router.get("/get/{intent_id}", response_model=ApiResponse)
async def get_intent(intent_id: int):
    intent = IntentService.get_intent(intent_id)
    if intent:
        return ApiResponse(code=200, message="查询成功", data=intent)
    else:
        return ApiResponse(code=404, message="意图不存在", data=None)

@router.get("/list", response_model=ApiResponse)
async def get_intents(
    status: Optional[str] = None,
    domain: Optional[str] = None,
    parent_id: Optional[int] = None
):
    filters = {}
    if status:
        filters['status'] = status
    if domain:
        filters['domain'] = domain
    if parent_id is not None:
        filters['parent_id'] = parent_id
    
    intents = IntentService.get_intents(filters)
    return ApiResponse(code=200, message="查询成功", data=intents)

@router.put("/status/{intent_id}", response_model=ApiResponse)
async def update_status(intent_id: int, status: IntentStatus, current_user: str = Depends(get_current_user)):
    success, result = IntentService.toggle_status(intent_id, status.status, current_user)
    
    # 记录操作日志
    OperationLogService.log_operation(
        operator=current_user,
        operation_type="status_change",
        operation_content=f"更新意图状态为: {status.status}",
        operation_result="success" if success else "failure",
        target_type="intent",
        target_id=intent_id
    )
    
    if success:
        return ApiResponse(code=200, message="状态更新成功", data=None)
    else:
        return ApiResponse(code=400, message=result, data=None)

@router.put("/sort/{intent_id}", response_model=ApiResponse)
async def update_sort_order(intent_id: int, sort_order: int, current_user: str = Depends(get_current_user)):
    success = IntentService.update_sort_order(intent_id, sort_order)
    
    # 记录操作日志
    OperationLogService.log_operation(
        operator=current_user,
        operation_type="update",
        operation_content=f"更新意图排序: {sort_order}",
        operation_result="success" if success else "failure",
        target_type="intent",
        target_id=intent_id
    )
    
    if success:
        return ApiResponse(code=200, message="排序更新成功", data=None)
    else:
        return ApiResponse(code=400, message="排序更新失败", data=None)
