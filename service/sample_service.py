import pandas as pd
import numpy as np
from difflib import SequenceMatcher
from common_lib.database import execute_query, fetch_all, fetch_one
from datetime import datetime

class SampleService:
    @staticmethod
    def create_sample(content, intent_id, annotator=None):
        try:
            # 检查意图是否存在
            intent = fetch_one("SELECT id FROM intent WHERE id = %s", (intent_id,))
            if not intent:
                return False, "意图不存在"
            
            # 检查是否重复
            duplicate = SampleService._check_duplicate(content)
            if duplicate:
                return False, "样本内容重复"
            
            # 插入样本
            query = """
                INSERT INTO sample (content, intent_id, annotator, annotation_status)
                VALUES (%s, %s, %s, %s)
            """
            cursor = execute_query(query, (content, intent_id, annotator, "pending"))
            if cursor:
                sample_id = cursor.lastrowid
                return True, sample_id
            return False, "创建失败"
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def update_sample(sample_id, content, intent_id, annotator=None):
        try:
            # 检查样本是否存在
            sample = fetch_one("SELECT id FROM sample WHERE id = %s", (sample_id,))
            if not sample:
                return False, "样本不存在"
            
            # 检查意图是否存在
            intent = fetch_one("SELECT id FROM intent WHERE id = %s", (intent_id,))
            if not intent:
                return False, "意图不存在"
            
            # 检查是否重复
            duplicate = SampleService._check_duplicate(content, sample_id)
            if duplicate:
                return False, "样本内容重复"
            
            # 更新样本
            query = """
                UPDATE sample 
                SET content = %s, intent_id = %s, annotator = %s, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """
            cursor = execute_query(query, (content, intent_id, annotator, sample_id))
            if cursor:
                return True, "更新成功"
            return False, "更新失败"
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def delete_sample(sample_id):
        try:
            # 检查样本是否存在
            sample = fetch_one("SELECT id FROM sample WHERE id = %s", (sample_id,))
            if not sample:
                return False, "样本不存在"
            
            # 删除样本
            query = "DELETE FROM sample WHERE id = %s"
            cursor = execute_query(query, (sample_id,))
            if cursor:
                return True, "删除成功"
            return False, "删除失败"
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def get_sample(sample_id):
        query = "SELECT * FROM sample WHERE id = %s"
        return fetch_one(query, (sample_id,))
    
    @staticmethod
    def get_samples(filters=None):
        query = "SELECT * FROM sample"
        params = []
        
        if filters:
            where_clauses = []
            if filters.get('intent_id'):
                where_clauses.append("intent_id = %s")
                params.append(filters['intent_id'])
            if filters.get('annotation_status'):
                where_clauses.append("annotation_status = %s")
                params.append(filters['annotation_status'])
            if filters.get('duplicate_flag') is not None:
                where_clauses.append("duplicate_flag = %s")
                params.append(filters['duplicate_flag'])
            
            if where_clauses:
                query += " WHERE " + " AND ".join(where_clauses)
        
        query += " ORDER BY created_at DESC"
        return fetch_all(query, params)
    
    @staticmethod
    def batch_import(file_path):
        try:
            # 读取Excel文件
            df = pd.read_excel(file_path)
            
            # 校验模板格式
            required_columns = ['content', 'intent_id']
            if not all(col in df.columns for col in required_columns):
                return False, "Excel文件格式错误，缺少必要列"
            
            success_count = 0
            error_count = 0
            error_messages = []
            
            for index, row in df.iterrows():
                content = row.get('content')
                intent_id = row.get('intent_id')
                annotator = row.get('annotator', None)
                
                if not content or pd.isna(intent_id):
                    error_count += 1
                    error_messages.append(f"第{index+2}行：内容或意图ID为空")
                    continue
                
                success, message = SampleService.create_sample(content, intent_id, annotator)
                if success:
                    success_count += 1
                else:
                    error_count += 1
                    error_messages.append(f"第{index+2}行：{message}")
            
            return True, {
                "success_count": success_count,
                "error_count": error_count,
                "error_messages": error_messages
            }
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def batch_export(intent_id=None, file_path="samples_export.xlsx"):
        try:
            query = "SELECT * FROM sample"
            params = []
            
            if intent_id:
                query += " WHERE intent_id = %s"
                params.append(intent_id)
            
            samples = fetch_all(query, params)
            
            if not samples:
                return False, "没有样本数据"
            
            # 转换为DataFrame
            df = pd.DataFrame(samples)
            
            # 保存为Excel文件
            df.to_excel(file_path, index=False)
            
            return True, file_path
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def _check_duplicate(content, exclude_id=None):
        # 获取所有样本内容
        query = "SELECT id, content FROM sample"
        if exclude_id:
            query += " WHERE id != %s"
            samples = fetch_all(query, (exclude_id,))
        else:
            samples = fetch_all(query)
        
        # 计算相似度
        for sample in samples:
            similarity = SampleService._calculate_similarity(content, sample['content'])
            if similarity >= 0.95:  # 95%相似度阈值
                return True
        
        return False
    
    @staticmethod
    def _calculate_similarity(str1, str2):
        return SequenceMatcher(None, str1, str2).ratio()
    
    @staticmethod
    def check_duplicates(content):
        # 检查与现有样本的相似度
        query = "SELECT id, content FROM sample"
        samples = fetch_all(query)
        
        duplicates = []
        for sample in samples:
            similarity = SampleService._calculate_similarity(content, sample['content'])
            if similarity >= 0.95:
                duplicates.append({
                    "sample_id": sample['id'],
                    "content": sample['content'],
                    "similarity": round(similarity, 2)
                })
        
        return duplicates
    
    @staticmethod
    def batch_annotate(sample_ids, intent_id, annotator):
        try:
            success_count = 0
            for sample_id in sample_ids:
                query = """
                    UPDATE sample 
                    SET intent_id = %s, annotator = %s, annotation_status = 'pending', updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                """
                cursor = execute_query(query, (intent_id, annotator, sample_id))
                if cursor:
                    success_count += 1
            
            return True, f"成功标注 {success_count} 个样本"
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def review_sample(sample_id, status, reject_reason=None):
        try:
            # 检查样本是否存在
            sample = fetch_one("SELECT id FROM sample WHERE id = %s", (sample_id,))
            if not sample:
                return False, "样本不存在"
            
            # 更新审核状态
            query = """
                UPDATE sample 
                SET annotation_status = %s, reject_reason = %s, annotated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """
            cursor = execute_query(query, (status, reject_reason, sample_id))
            if cursor:
                return True, "审核成功"
            return False, "审核失败"
        except Exception as e:
            return False, str(e)
