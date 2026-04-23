import pymysql
from common_lib.config.settings import settings

class DatabaseInitializer:
    def __init__(self):
        self.host = settings.database.host
        self.port = settings.database.port
        self.user = settings.database.user
        self.password = settings.database.password
        self.database = settings.database.name
        self.connection = None
    
    def connect(self):
        try:
            self.connection = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
            return True
        except Exception as e:
            print(f"Database connection failed: {e}")
            return False
    
    def create_tables(self):
        if not self.connection:
            if not self.connect():
                return False
        
        try:
            with self.connection.cursor() as cursor:
                # 意图表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS intent (
                        id INT PRIMARY KEY AUTO_INCREMENT,
                        name VARCHAR(255) NOT NULL UNIQUE,
                        description TEXT,
                        parent_id INT DEFAULT NULL,
                        created_by VARCHAR(100) NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        status ENUM('enabled', 'disabled') DEFAULT 'enabled',
                        domain ENUM('general', 'scientific') DEFAULT 'general',
                        sort_order INT DEFAULT 0,
                        FOREIGN KEY (parent_id) REFERENCES intent(id) ON DELETE SET NULL
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                ''')
                
                # 样本表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS sample (
                        id INT PRIMARY KEY AUTO_INCREMENT,
                        content TEXT NOT NULL,
                        intent_id INT NOT NULL,
                        annotator VARCHAR(100),
                        annotated_at TIMESTAMP DEFAULT NULL,
                        annotation_status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
                        duplicate_flag BOOLEAN DEFAULT FALSE,
                        reject_reason TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        FOREIGN KEY (intent_id) REFERENCES intent(id) ON DELETE CASCADE
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                ''')
                
                # 版本表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS intent_version (
                        id INT PRIMARY KEY AUTO_INCREMENT,
                        intent_id INT NOT NULL,
                        version VARCHAR(20) NOT NULL,
                        update_content TEXT,
                        updated_by VARCHAR(100) NOT NULL,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        update_reason TEXT,
                        status ENUM('draft', 'published', 'archived') DEFAULT 'draft',
                        FOREIGN KEY (intent_id) REFERENCES intent(id) ON DELETE CASCADE
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                ''')
                
                # 操作日志表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS operation_log (
                        id INT PRIMARY KEY AUTO_INCREMENT,
                        operator VARCHAR(100) NOT NULL,
                        operation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        operation_type ENUM('create', 'update', 'delete', 'status_change', 'import', 'export') NOT NULL,
                        operation_content TEXT NOT NULL,
                        operation_result ENUM('success', 'failure') NOT NULL,
                        target_type ENUM('intent', 'sample', 'version', 'test') NOT NULL,
                        target_id INT DEFAULT NULL
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                ''')
                
                # 反馈表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS feedback (
                        id INT PRIMARY KEY AUTO_INCREMENT,
                        record_id VARCHAR(100) NOT NULL,
                        feedback_type ENUM('incorrect_intent', 'missing_intent', 'other') NOT NULL,
                        feedback_content TEXT,
                        user_id VARCHAR(100) NOT NULL,
                        feedback_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                ''')
                
                # A/B测试表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS ab_test (
                        id INT PRIMARY KEY AUTO_INCREMENT,
                        name VARCHAR(255) NOT NULL,
                        start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        end_time TIMESTAMP DEFAULT NULL,
                        status ENUM('active', 'paused', 'completed', 'archived') DEFAULT 'active',
                        traffic_ratio FLOAT DEFAULT 0.5,
                        created_by VARCHAR(100) NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                ''')
                
                # A/B测试结果表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS ab_test_result (
                        id INT PRIMARY KEY AUTO_INCREMENT,
                        test_id INT NOT NULL,
                        group_name ENUM('A', 'B') NOT NULL,
                        accuracy FLOAT DEFAULT 0,
                        response_time FLOAT DEFAULT 0,
                        sample_count INT DEFAULT 0,
                        recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (test_id) REFERENCES ab_test(id) ON DELETE CASCADE
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                ''')
                
                # 对话记录表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS conversation (
                        id INT PRIMARY KEY AUTO_INCREMENT,
                        conversation_id VARCHAR(100) NOT NULL,
                        user_id VARCHAR(100) NOT NULL,
                        session_id VARCHAR(100) NOT NULL,
                        message_content TEXT NOT NULL,
                        send_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        identified_intent VARCHAR(255),
                        parent_conversation_id INT DEFAULT NULL,
                        FOREIGN KEY (parent_conversation_id) REFERENCES conversation(id) ON DELETE SET NULL
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                ''')
                
                # 意图切换记录表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS intent_switch (
                        id INT PRIMARY KEY AUTO_INCREMENT,
                        user_id VARCHAR(100) NOT NULL,
                        session_id VARCHAR(100) NOT NULL,
                        previous_intent VARCHAR(255) NOT NULL,
                        current_intent VARCHAR(255) NOT NULL,
                        trigger_message TEXT NOT NULL,
                        switch_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                ''')
                
                # 监控数据表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS monitoring_data (
                        id INT PRIMARY KEY AUTO_INCREMENT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        interval_type ENUM('realtime', 'hourly', 'daily', 'weekly', 'monthly') NOT NULL,
                        accuracy FLOAT DEFAULT 0,
                        error_rate FLOAT DEFAULT 0,
                        miss_rate FLOAT DEFAULT 0,
                        sample_count INT DEFAULT 0
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                ''')
                
                # 指标表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS metrics (
                        id INT PRIMARY KEY AUTO_INCREMENT,
                        metric_type ENUM('accuracy', 'error_rate', 'miss_rate', 'response_time', 'coverage') NOT NULL,
                        value FLOAT DEFAULT 0,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        time_period ENUM('daily', 'weekly', 'monthly') NOT NULL
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                ''')
            
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error creating tables: {e}")
            self.connection.rollback()
            return False
    
    def close(self):
        if self.connection:
            self.connection.close()

def init_database():
    initializer = DatabaseInitializer()
    return initializer.create_tables()
