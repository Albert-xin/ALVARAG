from common_lib.database import execute_query, fetch_all, fetch_one
from datetime import datetime

class VersionService:
    @staticmethod
    def get_versions(intent_id):
        query = """
            SELECT * FROM intent_version 
            WHERE intent_id = %s 
            ORDER BY updated_at DESC
        """
        return fetch_all(query, (intent_id,))
    
    @staticmethod
    def get_version(version_id):
        query = "SELECT * FROM intent_version WHERE id = %s"
        return fetch_one(query, (version_id,))
    
    @staticmethod
    def compare_versions(version_id1, version_id2):
        try:
            # 获取两个版本的信息
            version1 = VersionService.get_version(version_id1)
            version2 = VersionService.get_version(version_id2)
            
            if not version1 or not version2:
                return False, "版本不存在"
            
            if version1['intent_id'] != version2['intent_id']:
                return False, "两个版本不属于同一意图"
            
            # 获取对应版本的意图信息
            intent1 = fetch_one("SELECT * FROM intent WHERE id = %s", (version1['intent_id'],))
            intent2 = fetch_one("SELECT * FROM intent WHERE id = %s", (version2['intent_id'],))
            
            # 获取对应版本的样本信息
            samples1 = fetch_all("SELECT * FROM sample WHERE intent_id = %s", (version1['intent_id'],))
            samples2 = fetch_all("SELECT * FROM sample WHERE intent_id = %s", (version2['intent_id'],))
            
            # 生成差异报告
            diff = {
                "version1": {
                    "version": version1['version'],
                    "updated_at": version1['updated_at'],
                    "updated_by": version1['updated_by'],
                    "update_reason": version1['update_reason']
                },
                "version2": {
                    "version": version2['version'],
                    "updated_at": version2['updated_at'],
                    "updated_by": version2['updated_by'],
                    "update_reason": version2['update_reason']
                },
                "intent_diff": VersionService._compare_intents(intent1, intent2),
                "sample_diff": VersionService._compare_samples(samples1, samples2)
            }
            
            return True, diff
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def _compare_intents(intent1, intent2):
        diff = {}
        if intent1 and intent2:
            for key in ['name', 'description', 'status', 'domain']:
                if intent1.get(key) != intent2.get(key):
                    diff[key] = {
                        "old": intent1.get(key),
                        "new": intent2.get(key)
                    }
        return diff
    
    @staticmethod
    def _compare_samples(samples1, samples2):
        # 简单比较样本数量差异
        return {
            "sample_count_diff": len(samples2) - len(samples1),
            "old_sample_count": len(samples1),
            "new_sample_count": len(samples2)
        }
    
    @staticmethod
    def rollback_to_version(version_id, operator):
        try:
            # 获取目标版本信息
            target_version = VersionService.get_version(version_id)
            if not target_version:
                return False, "版本不存在"
            
            # 检查版本状态
            if target_version['status'] != 'published':
                return False, "只能回滚到已发布版本"
            
            # 获取当前意图信息
            current_intent = fetch_one("SELECT * FROM intent WHERE id = %s", (target_version['intent_id'],))
            if not current_intent:
                return False, "意图不存在"
            
            # 备份当前版本
            VersionService._backup_current_version(target_version['intent_id'], operator)
            
            # 回滚操作（这里简化处理，实际应该根据版本历史记录恢复）
            # 注意：实际项目中需要更复杂的回滚逻辑，包括恢复意图信息和关联样本
            
            # 更新版本状态
            query = "UPDATE intent_version SET status = 'archived' WHERE intent_id = %s AND id != %s"
            execute_query(query, (target_version['intent_id'], version_id))
            
            query = "UPDATE intent_version SET status = 'published' WHERE id = %s"
            execute_query(query, (version_id,))
            
            return True, "回滚成功"
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def _backup_current_version(intent_id, operator):
        # 获取当前意图信息
        current_intent = fetch_one("SELECT * FROM intent WHERE id = %s", (intent_id,))
        if not current_intent:
            return
        
        # 获取当前最新版本
        current_version = fetch_one(
            "SELECT version FROM intent_version WHERE intent_id = %s ORDER BY updated_at DESC LIMIT 1",
            (intent_id,)
        )
        
        if current_version:
            # 生成备份版本号
            major, minor = map(int, current_version['version'].split('.'))
            backup_version = f"{major}.{minor + 1}-backup"
        else:
            backup_version = "1.0-backup"
        
        # 创建备份版本
        query = """
            INSERT INTO intent_version (intent_id, version, update_content, updated_by, update_reason, status)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        execute_query(
            query, 
            (intent_id, backup_version, "回滚前备份", operator, "回滚操作", "archived")
        )
    
    @staticmethod
    def publish_version(version_id, operator):
        try:
            # 获取版本信息
            version = VersionService.get_version(version_id)
            if not version:
                return False, "版本不存在"
            
            # 更新版本状态为已发布
            query = "UPDATE intent_version SET status = 'published' WHERE id = %s"
            cursor = execute_query(query, (version_id,))
            
            # 将同一意图的其他版本设置为归档
            query = "UPDATE intent_version SET status = 'archived' WHERE intent_id = %s AND id != %s"
            execute_query(query, (version['intent_id'], version_id))
            
            if cursor:
                return True, "发布成功"
            return False, "发布失败"
        except Exception as e:
            return False, str(e)
