from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# Chat API 相关请求模型
class ChatRequest(BaseModel):
    """非流式和流式 RAG 问答请求"""
    question: str = Field(..., description="用户问题")
    knowledge_base_id: str = Field(..., description="知识库 ID")
    top_k: Optional[int] = Field(3, ge=1, le=50, description="检索结果数量")


class ChatWithHistoryRequest(BaseModel):
    """带历史对话的 RAG 问答请求"""
    question: str = Field(..., description="用户问题")
    knowledge_base_id: str = Field(..., description="知识库 ID")
    history: List[Dict[str, str]] = Field(default_factory=list, description="历史对话")
    top_k: Optional[int] = Field(3, ge=1, le=50, description="检索结果数量")


# Document API 相关请求模型
class DocumentUploadRequest(BaseModel):
    """文档上传请求"""
    knowledge_base_id: str = Field(..., description="知识库 ID")
    file_name: str = Field(..., description="文件名")
    file_size: int = Field(..., ge=1, le=104857600, description="文件大小（最大 100MB）")
    file_type: str = Field(..., description="文件类型")


class DocumentListRequest(BaseModel):
    """文档列表请求"""
    knowledge_base_id: Optional[str] = Field(None, description="知识库 ID")
    status: Optional[str] = Field(None, description="文档状态")
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(10, ge=1, le=100, description="每页数量")


# Retrieve API 相关请求模型
class RetrieveQueryRequest(BaseModel):
    """纯向量检索请求"""
    query: str = Field(..., description="查询语句")
    knowledge_base_id: str = Field(..., description="知识库 ID")
    top_k: Optional[int] = Field(3, ge=1, le=50, description="检索结果数量")


class RetrieveRerankRequest(BaseModel):
    """检索+重排请求"""
    query: str = Field(..., description="查询语句")
    knowledge_base_id: str = Field(..., description="知识库 ID")
    top_k: Optional[int] = Field(3, ge=1, le=50, description="检索结果数量")


class BatchRetrieveRequest(BaseModel):
    """批量检索请求"""
    queries: List[str] = Field(..., min_items=1, max_items=10, description="查询语句列表")
    knowledge_base_id: str = Field(..., description="知识库 ID")
    top_k: Optional[int] = Field(3, ge=1, le=50, description="检索结果数量")


# Task API 相关请求模型
class TaskListRequest(BaseModel):
    """任务列表请求"""
    status: Optional[str] = Field(None, description="任务状态")
    task_type: Optional[str] = Field(None, description="任务类型")
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(10, ge=1, le=100, description="每页数量")
