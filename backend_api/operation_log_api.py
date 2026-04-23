from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import Optional, List, Any
from service.operation_log_service import OperationLogService
from datetime import datetime

router = APIRouter(prefix="/api/log", tags=["operation_log"])

class ApiResponse(BaseModel):
    code: int
    message: str
    data: Optional[Any] = None

@router.get("/list", response_model=ApiResponse)
async def get_operation_logs(
    operator: Optional[str] = None,
    operation_type: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    target_type: Optional[str] = None,
    target_id: Optional[int] = None
):
    filters = {}
    if operator:
        filters['operator'] = operator
    if operation_type:
        filters['operation_type'] = operation_type
    if start_time:
        filters['start_time'] = start_time
    if end_time:
        filters['end_time'] = end_time
    if target_type:
        filters['target_type'] = target_type
    if target_id:
        filters['target_id'] = target_id
    
    logs = OperationLogService.get_operation_logs(filters)
    return ApiResponse(code=200, message="查询成功", data=logs)
