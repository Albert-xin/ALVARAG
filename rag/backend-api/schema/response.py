from typing import List, Optional, Dict, Any, Generic, TypeVar
from pydantic import BaseModel, Field

T = TypeVar('T')


class BaseResponse(BaseModel, Generic[T]):
    """统一返回格式"""
    code: int = Field(200, description="状态码")
    msg: str = Field("success", description="消息")
    data: Optional[T] = Field(None, description="数据")
    request_id: str = Field(..., description="请求 ID")


# Chat API 相关响应模型
class ReferenceDocument(BaseModel):
    """参考文档"""
    doc_id: str = Field(..., description="文档 ID")
    doc_name: str = Field(..., description="文档名称")
    content: str = Field(..., description="文档内容")
    score: float = Field(..., description="相关性分数")
    page_num: Optional[int] = Field(None, description="页码")


class ChatResponse(BaseModel):
    """非流式 RAG 问答响应"""
    answer: str = Field(..., description="回答内容")
    references: List[ReferenceDocument] = Field(default_factory=list, description="参考文档列表")


class StreamChatResponse(BaseModel):
    """流式 RAG 问答响应"""
    answer_chunk: str = Field(..., description="回答片段")
    is_finished: bool = Field(False, description="是否结束")
    references: Optional[List[ReferenceDocument]] = Field(None, description="参考文档列表")


# Document API 相关响应模型
class DocumentMeta(BaseModel):
    """文档元信息"""
    doc_id: str = Field(..., description="文档 ID")
    doc_name: str = Field(..., description="文档名称")
    knowledge_base_id: str = Field(..., description="知识库 ID")
    status: str = Field(..., description="文档状态")
    file_size: int = Field(..., description="文件大小")
    chunk_count: int = Field(..., description="分块数")
    vector_status: str = Field(..., description="向量状态")
    created_at: str = Field(..., description="创建时间")


class DocumentListResponse(BaseModel):
    """文档列表响应"""
    documents: List[DocumentMeta] = Field(default_factory=list, description="文档列表")
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")


class DocumentDetailResponse(BaseModel):
    """文档详情响应"""
    doc_id: str = Field(..., description="文档 ID")
    doc_name: str = Field(..., description="文档名称")
    knowledge_base_id: str = Field(..., description="知识库 ID")
    status: str = Field(..., description="文档状态")
    file_size: int = Field(..., description="文件大小")
    chunk_count: int = Field(..., description="分块数")
    vector_status: str = Field(..., description="向量状态")
    created_at: str = Field(..., description="创建时间")
    processed_at: Optional[str] = Field(None, description="处理时间")
    logs: List[str] = Field(default_factory=list, description="处理日志")


# Retrieve API 相关响应模型
class RetrieveResult(BaseModel):
    """检索结果"""
    content: str = Field(..., description="内容")
    score: float = Field(..., description="分数")
    doc_id: str = Field(..., description="文档 ID")
    doc_name: str = Field(..., description="文档名称")
    page_num: Optional[int] = Field(None, description="页码")


class BatchRetrieveResult(BaseModel):
    """批量检索结果"""
    query: str = Field(..., description="查询语句")
    results: List[RetrieveResult] = Field(default_factory=list, description="检索结果")


# Task API 相关响应模型
class TaskInfo(BaseModel):
    """任务信息"""
    task_id: str = Field(..., description="任务 ID")
    task_type: str = Field(..., description="任务类型")
    status: str = Field(..., description="任务状态")
    created_at: str = Field(..., description="创建时间")
    started_at: Optional[str] = Field(None, description="开始时间")
    completed_at: Optional[str] = Field(None, description="完成时间")
    error_message: Optional[str] = Field(None, description="错误信息")


class TaskListResponse(BaseModel):
    """任务列表响应"""
    tasks: List[TaskInfo] = Field(default_factory=list, description="任务列表")
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")


# Health API 相关响应模型
class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str = Field(..., description="服务状态")


class HealthDetailResponse(BaseModel):
    """依赖检查响应"""
    model: Dict[str, Any] = Field(..., description="模型状态")
    vector_db: Dict[str, Any] = Field(..., description="向量库状态")
    storage: Dict[str, Any] = Field(..., description="存储状态")
    queue: Dict[str, Any] = Field(..., description="队列状态")


class VersionResponse(BaseModel):
    """版本信息响应"""
    version: str = Field(..., description="版本号")
    build_time: str = Field(..., description="构建时间")
    environment: str = Field(..., description="环境")
