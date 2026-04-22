"""RAG服务
功能：提供RAG相关的核心业务逻辑
作者：
创建时间：
"""
from typing import List, Dict, Any, Generator

from model_service.embedding.embedding_service import embedding_service
from model_service.rerank.rerank_service import rerank_service
from model_service.llm.llm_service import llm_service
from model_service.llm.prompt_template import build_rag_prompt, build_chat_history_prompt
from storage.vector_store import vector_store
from common_lib.logging.logger import get_logger
from common_lib.exceptions.base_exceptions import BusinessException

logger = get_logger(__name__)


class RAGService:
    """RAG服务"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RAGService, cls).__new__(cls)
            cls._instance._init_service()
        return cls._instance
    
    def _init_service(self):
        """初始化服务"""
        # 初始化模型服务
        embedding_service.init()
        rerank_service.init()
        llm_service.init()
        logger.info("RAG服务初始化完成")
    
    def chat(self, query: str, kb_id: str, retrieve_params: Dict[str, Any]) -> Dict[str, Any]:
        """非流式RAG问答
        参数：query - 用户问题；kb_id - 知识库ID；retrieve_params - 检索参数
        返回：回答结果
        被调用：chat_api.chat()
        """
        try:
            # 1. 生成问题向量
            query_embedding = embedding_service.generate_single(query)
            
            # 2. 向量检索
            top_k = retrieve_params.get('top_k', 5)
            search_results = vector_store.search(query_embedding, top_k, [kb_id])
            
            # 3. 重排
            if retrieve_params.get('rerank', True):
                docs = [result['content'] for result in search_results]
                reranked = rerank_service.rerank(query, docs, top_k)
                search_results = [search_results[r['index']] for r in reranked]
            
            # 4. 构建上下文
            context_list = [result['content'] for result in search_results]
            prompt = build_rag_prompt(query, context_list)
            
            # 5. 生成回答
            params = {'temperature': 0.7, 'top_p': 0.9}
            answer = llm_service.generate(prompt, params)
            
            # 6. 构建返回结果
            references = []
            for result in search_results:
                references.append({
                    'doc_id': result['doc_id'],
                    'chunk_id': result['chunk_id'],
                    'content': result['content'],
                    'score': result['score'],
                    'page': result['page']
                })
            
            logger.info("非流式RAG问答完成")
            return {
                'answer': answer,
                'references': references,
                'retrieve_meta': {
                    'top_k': top_k,
                    'rerank': retrieve_params.get('rerank', True)
                }
            }
        except Exception as e:
            logger.error(f"RAG问答失败: {e}")
            raise BusinessException(f"RAG问答失败: {str(e)}")
    
    def chat_stream(self, query: str, kb_id: str, retrieve_params: Dict[str, Any]) -> Generator[Dict[str, Any], None, None]:
        """流式RAG问答
        参数：query - 用户问题；kb_id - 知识库ID；retrieve_params - 检索参数
        返回：流式回答
        被调用：chat_api.chat_stream()
        """
        try:
            # 1. 生成问题向量
            query_embedding = embedding_service.generate_single(query)
            
            # 2. 向量检索
            top_k = retrieve_params.get('top_k', 5)
            search_results = vector_store.search(query_embedding, top_k, [kb_id])
            
            # 3. 重排
            if retrieve_params.get('rerank', True):
                docs = [result['content'] for result in search_results]
                reranked = rerank_service.rerank(query, docs, top_k)
                search_results = [search_results[r['index']] for r in reranked]
            
            # 4. 构建上下文
            context_list = [result['content'] for result in search_results]
            prompt = build_rag_prompt(query, context_list)
            
            # 5. 流式生成
            params = {'temperature': 0.7, 'top_p': 0.9}
            for chunk in llm_service.generate_stream(prompt, params):
                yield {'type': 'text', 'content': chunk}
            
            # 6. 发送参考文档
            references = []
            for result in search_results:
                references.append({
                    'doc_id': result['doc_id'],
                    'chunk_id': result['chunk_id'],
                    'content': result['content'],
                    'score': result['score'],
                    'page': result['page']
                })
            yield {'type': 'references', 'content': references}
            
            logger.info("流式RAG问答完成")
        except Exception as e:
            logger.error(f"流式RAG问答失败: {e}")
            yield {'type': 'error', 'content': f"RAG问答失败: {str(e)}"}
    
    def chat_with_history(self, history: List[Dict[str, str]], query: str, kb_id: str, retrieve_params: Dict[str, Any]) -> Dict[str, Any]:
        """带历史对话的RAG问答
        参数：history - 历史对话；query - 当前问题；kb_id - 知识库ID；retrieve_params - 检索参数
        返回：回答结果
        被调用：chat_api.chat_with_history()
        """
        try:
            # 1. 生成问题向量（基于历史+当前问题）
            # 简化处理，实际应生成优化后的检索query
            query_embedding = embedding_service.generate_single(query)
            
            # 2. 向量检索
            top_k = retrieve_params.get('top_k', 5)
            search_results = vector_store.search(query_embedding, top_k, [kb_id])
            
            # 3. 重排
            if retrieve_params.get('rerank', True):
                docs = [result['content'] for result in search_results]
                reranked = rerank_service.rerank(query, docs, top_k)
                search_results = [search_results[r['index']] for r in reranked]
            
            # 4. 构建上下文
            context_list = [result['content'] for result in search_results]
            prompt = build_chat_history_prompt(history, query, context_list)
            
            # 5. 生成回答
            answer = llm_service.chat_completion(history, query, '\n'.join(context_list))
            
            # 6. 构建返回结果
            references = []
            for result in search_results:
                references.append({
                    'doc_id': result['doc_id'],
                    'chunk_id': result['chunk_id'],
                    'content': result['content'],
                    'score': result['score'],
                    'page': result['page']
                })
            
            logger.info("带历史对话的RAG问答完成")
            return {
                'answer': answer,
                'references': references,
                'retrieve_meta': {
                    'top_k': top_k,
                    'rerank': retrieve_params.get('rerank', True)
                }
            }
        except Exception as e:
            logger.error(f"带历史对话的RAG问答失败: {e}")
            raise BusinessException(f"RAG问答失败: {str(e)}")
    
    def retrieve(self, query: str, kb_id: str, top_k: int) -> List[Dict[str, Any]]:
        """纯向量检索
        参数：query - 查询词；kb_id - 知识库ID；top_k - 返回数量
        返回：检索结果
        被调用：retrieve_api.retrieve_query()
        """
        try:
            # 生成问题向量
            query_embedding = embedding_service.generate_single(query)
            # 向量检索
            results = vector_store.search(query_embedding, top_k, [kb_id])
            logger.info("纯向量检索完成")
            return results
        except Exception as e:
            logger.error(f"向量检索失败: {e}")
            raise BusinessException(f"向量检索失败: {str(e)}")
    
    def retrieve_rerank(self, query: str, kb_id: str, top_k: int) -> List[Dict[str, Any]]:
        """检索+重排
        参数：query - 查询词；kb_id - 知识库ID；top_k - 返回数量
        返回：重排后的结果
        被调用：retrieve_api.retrieve_rerank()
        """
        try:
            # 生成问题向量
            query_embedding = embedding_service.generate_single(query)
            # 向量检索（高召回）
            search_results = vector_store.search(query_embedding, top_k * 2, [kb_id])
            # 重排
            docs = [result['content'] for result in search_results]
            reranked = rerank_service.rerank(query, docs, top_k)
            # 构建结果
            results = [search_results[r['index']] for r in reranked]
            logger.info("检索+重排完成")
            return results
        except Exception as e:
            logger.error(f"检索+重排失败: {e}")
            raise BusinessException(f"检索+重排失败: {str(e)}")
    
    def retrieve_batch(self, queries: List[str], kb_id: str, top_k: int) -> Dict[str, List[Dict[str, Any]]]:
        """批量检索
        参数：queries - 查询词列表；kb_id - 知识库ID；top_k - 返回数量
        返回：批量检索结果
        被调用：retrieve_api.retrieve_batch()
        """
        try:
            results = {}
            for query in queries:
                # 为每个查询执行检索+重排
                query_results = self.retrieve_rerank(query, kb_id, top_k)
                results[query] = query_results
            logger.info(f"批量检索完成，共{len(queries)}个查询")
            return results
        except Exception as e:
            logger.error(f"批量检索失败: {e}")
            raise BusinessException(f"批量检索失败: {str(e)}")


# 全局RAG服务实例
rag_service = RAGService()