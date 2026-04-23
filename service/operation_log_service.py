from common_lib.database import execute_query, fetch_all
from datetime import datetime

class OperationLogService:
    @staticmethod
    def log_operation(operator, operation_type, operation_content, operation_result, target_type, target_id=None):
        try:
            query = """
                INSERT INTO operation_log 
                (operator, operation_time, operation_type, operation_content, operation_result, target_type, target_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            execute_query(
                query, 
                (operator, datetime.now(), operation_type, operation_content, operation_result, target_type, target_id)
            )
            return True
        except Exception as e:
            print(f"Log operation failed: {e}")
            return False
    
    @staticmethod
    def get_operation_logs(filters=None):
        query = "SELECT * FROM operation_log"
        params = []
        
        if filters:
            where_clauses = []
            if filters.get('operator'):
                where_clauses.append("operator = %s")
                params.append(filters['operator'])
            if filters.get('operation_type'):
                where_clauses.append("operation_type = %s")
                params.append(filters['operation_type'])
            if filters.get('start_time'):
                where_clauses.append("operation_time >= %s")
                params.append(filters['start_time'])
            if filters.get('end_time'):
                where_clauses.append("operation_time <= %s")
                params.append(filters['end_time'])
            if filters.get('target_type'):
                where_clauses.append("target_type = %s")
                params.append(filters['target_type'])
            if filters.get('target_id'):
                where_clauses.append("target_id = %s")
                params.append(filters['target_id'])
            
            if where_clauses:
                query += " WHERE " + " AND ".join(where_clauses)
        
        query += " ORDER BY operation_time DESC"
        return fetch_all(query, params)
