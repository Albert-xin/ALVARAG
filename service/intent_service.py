from common_lib.database import execute_query, fetch_all, fetch_one
from datetime import datetime

class IntentService:
    @staticmethod
    def create_intent(name, description, parent_id, created_by, domain='general'):
        try:
            # 检查名称是否已存在
            existing = fetch_one("SELECT id FROM intent WHERE name = %s", (name,))
            if existing:
                return False, "意图名称已存在"
            
            # 检查父意图是否存在
            if parent_id:
                parent = fetch_one("SELECT id FROM intent WHERE id = %s", (parent_id,))
                if not parent:
                    return False, "父意图不存在"
            
            # 插入新意图
            query = """
                INSERT INTO intent (name, description, parent_id, created_by, domain)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor = execute_query(query, (name, description, parent_id, created_by, domain))
            if cursor:
                intent_id = cursor.lastrowid
                # 创建初始版本
                IntentService._create_initial_version(intent_id, created_by)
                return True, intent_id
            return False, "创建失败"
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def update_intent(intent_id, name, description, parent_id, updated_by):
        try:
            # 检查意图是否存在
            existing = fetch_one("SELECT id FROM intent WHERE id = %s", (intent_id,))
            if not existing:
                return False, "意图不存在"
            
            # 检查名称是否与其他意图冲突
            existing_name = fetch_one("SELECT id FROM intent WHERE name = %s AND id != %s", (name, intent_id))
            if existing_name:
                return False, "意图名称已存在"
            
            # 检查父意图是否存在且不是自己（避免循环）
            if parent_id:
                if parent_id == intent_id:
                    return False, "父意图不能是自己"
                parent = fetch_one("SELECT id FROM intent WHERE id = %s", (parent_id,))
                if not parent:
                    return False, "父意图不存在"
            
            # 更新意图
            query = """
                UPDATE intent 
                SET name = %s, description = %s, parent_id = %s, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """
            cursor = execute_query(query, (name, description, parent_id, intent_id))
            if cursor:
                # 创建新版本
                IntentService._create_new_version(intent_id, "更新意图信息", updated_by, "意图信息变更")
                return True, "更新成功"
            return False, "更新失败"
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def delete_intent(intent_id, deleted_by):
        try:
            # 检查意图是否存在
            existing = fetch_one("SELECT id FROM intent WHERE id = %s", (intent_id,))
            if not existing:
                return False, "意图不存在"
            
            # 检查是否有关联样本
            samples = fetch_one("SELECT COUNT(*) as count FROM sample WHERE intent_id = %s", (intent_id,))
            if samples and samples['count'] > 0:
                return False, "意图下有关联样本，无法删除"
            
            # 检查是否有子意图
            children = fetch_one("SELECT COUNT(*) as count FROM intent WHERE parent_id = %s", (intent_id,))
            if children and children['count'] > 0:
                return False, "意图下有子意图，无法删除"
            
            # 删除意图
            query = "DELETE FROM intent WHERE id = %s"
            cursor = execute_query(query, (intent_id,))
            if cursor:
                return True, "删除成功"
            return False, "删除失败"
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def get_intent(intent_id):
        query = """
            SELECT * FROM intent WHERE id = %s
        """
        return fetch_one(query, (intent_id,))
    
    @staticmethod
    def get_intents(filters=None):
        query = "SELECT * FROM intent"
        params = []
        
        if filters:
            where_clauses = []
            if filters.get('status'):
                where_clauses.append("status = %s")
                params.append(filters['status'])
            if filters.get('domain'):
                where_clauses.append("domain = %s")
                params.append(filters['domain'])
            if filters.get('parent_id') is not None:
                where_clauses.append("parent_id = %s")
                params.append(filters['parent_id'])
            
            if where_clauses:
                query += " WHERE " + " AND ".join(where_clauses)
        
        query += " ORDER BY sort_order ASC, created_at DESC"
        return fetch_all(query, params)
    
    @staticmethod
    def toggle_status(intent_id, status, operator):
        try:
            # 检查意图是否存在
            existing = fetch_one("SELECT id FROM intent WHERE id = %s", (intent_id,))
            if not existing:
                return False, "意图不存在"
            
            # 更新状态
            query = "UPDATE intent SET status = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s"
            cursor = execute_query(query, (status, intent_id))
            if cursor:
                # 创建新版本
                IntentService._create_new_version(
                    intent_id, 
                    f"将状态切换为{status}", 
                    operator, 
                    "状态变更"
                )
                return True, "状态更新成功"
            return False, "状态更新失败"
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def _create_initial_version(intent_id, created_by):
        query = """
            INSERT INTO intent_version (intent_id, version, update_content, updated_by, update_reason, status)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        execute_query(
            query, 
            (intent_id, "1.0", "初始版本", created_by, "创建意图", "published")
        )
    
    @staticmethod
    def _create_new_version(intent_id, update_content, updated_by, update_reason):
        # 获取当前版本
        current_version = fetch_one(
            "SELECT version FROM intent_version WHERE intent_id = %s ORDER BY updated_at DESC LIMIT 1",
            (intent_id,)
        )
        
        if current_version:
            # 生成新版本号
            major, minor = map(int, current_version['version'].split('.'))
            new_version = f"{major}.{minor + 1}"
        else:
            new_version = "1.0"
        
        query = """
            INSERT INTO intent_version (intent_id, version, update_content, updated_by, update_reason, status)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        execute_query(
            query, 
            (intent_id, new_version, update_content, updated_by, update_reason, "published")
        )
    
    @staticmethod
    def update_sort_order(intent_id, sort_order):
        query = "UPDATE intent SET sort_order = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s"
        cursor = execute_query(query, (sort_order, intent_id))
        return cursor is not None
