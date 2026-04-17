"""
数据库表结构更新脚本
添加缺失的字段到 deals 表
"""
import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

# 数据库配置
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'port': int(os.environ.get('DB_PORT', 3306)),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', ''),
    'database': os.environ.get('DB_NAME', 'customer_management'),
    'charset': 'utf8mb4'
}

def update_database():
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # 检查 deals 表的现有字段
        cursor.execute("DESCRIBE deals")
        existing_columns = [row[0] for row in cursor.fetchall()]
        
        print("现有字段:", existing_columns)
        
        # 需要添加的字段
        columns_to_add = [
            ("product_id", "INT", "NULL"),
            ("product_name", "VARCHAR(100)", "NULL"),
            ("quantity", "INT", "DEFAULT 1"),
            ("unit_price", "FLOAT", "DEFAULT 0"),
            ("payment_status", "VARCHAR(20)", "DEFAULT 'unpaid'"),
            ("paid_amount", "FLOAT", "DEFAULT 0"),
            ("approval_status", "VARCHAR(20)", "DEFAULT 'pending'"),
            ("approved_by", "INT", "NULL"),
            ("approved_at", "DATETIME", "NULL"),
            ("expected_close_date", "DATE", "NULL"),
            ("actual_close_date", "DATE", "NULL"),
            ("notes", "TEXT", "NULL"),
        ]
        
        for col_name, col_type, default in columns_to_add:
            if col_name not in existing_columns:
                sql = f"ALTER TABLE deals ADD COLUMN {col_name} {col_type} {default}"
                print(f"添加字段: {col_name}")
                cursor.execute(sql)
            else:
                print(f"字段已存在: {col_name}")
        
        # 添加外键约束（如果不存在）
        try:
            cursor.execute("""
                SELECT CONSTRAINT_NAME 
                FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE 
                WHERE TABLE_NAME = 'deals' 
                AND COLUMN_NAME = 'product_id' 
                AND CONSTRAINT_SCHEMA = DATABASE()
            """)
            if not cursor.fetchone():
                cursor.execute("""
                    ALTER TABLE deals 
                    ADD CONSTRAINT fk_deal_product 
                    FOREIGN KEY (product_id) REFERENCES products(id)
                """)
                print("添加外键: fk_deal_product")
        except Exception as e:
            print(f"添加 product_id 外键失败（可能已存在）: {e}")
        
        try:
            cursor.execute("""
                SELECT CONSTRAINT_NAME 
                FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE 
                WHERE TABLE_NAME = 'deals' 
                AND COLUMN_NAME = 'approved_by' 
                AND CONSTRAINT_SCHEMA = DATABASE()
            """)
            if not cursor.fetchone():
                cursor.execute("""
                    ALTER TABLE deals 
                    ADD CONSTRAINT fk_deal_approver 
                    FOREIGN KEY (approved_by) REFERENCES users(id)
                """)
                print("添加外键: fk_deal_approver")
        except Exception as e:
            print(f"添加 approved_by 外键失败（可能已存在）: {e}")
        
        conn.commit()
        print("\n数据库更新完成！")
        
    except Exception as e:
        conn.rollback()
        print(f"更新失败: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    update_database()
