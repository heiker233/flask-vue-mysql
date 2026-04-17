import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

# 数据库连接参数
config = {
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', ''),
    'host': os.environ.get('DB_HOST', 'localhost'),
    'port': int(os.environ.get('DB_PORT', 3306)),
    'charset': 'utf8mb4'
}

try:
    # 连接到 MySQL 服务器（不指定数据库）
    conn = pymysql.connect(**config)
    cursor = conn.cursor()
    
    # 创建数据库
    cursor.execute('CREATE DATABASE IF NOT EXISTS customer_management CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci')
    
    print('数据库 customer_management 创建成功')
    
    # 关闭连接
    cursor.close()
    conn.close()
    
except pymysql.Error as e:
    print(f'数据库操作错误: {e}')
