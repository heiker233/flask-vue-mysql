"""
配置文件
从环境变量读取配置信息
"""
import os
from datetime import timedelta
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    """基础配置类"""
    # 数据库配置
    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = os.environ.get('DB_PORT', '3306')
    DB_NAME = os.environ.get('DB_NAME', 'customer_management')
    
    from urllib.parse import quote_plus
    _encoded_pw = quote_plus(DB_PASSWORD) if DB_PASSWORD else ''
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{DB_USER}:{_encoded_pw}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT 配置
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY 环境变量未设置，请检查 .env 文件")
    
    JWT_EXPIRATION_DELTA = timedelta(hours=24)
    
    # CORS 配置
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*')
    
    # Flask 配置
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False


class TestingConfig(Config):
    """测试环境配置"""
    DEBUG = True
    TESTING = True
    # 测试数据库
    DB_NAME = os.environ.get('TEST_DB_NAME', 'customer_management_test')
    from urllib.parse import quote_plus
    _encoded_pw = quote_plus(Config.DB_PASSWORD) if Config.DB_PASSWORD else ''
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{Config.DB_USER}:{_encoded_pw}@{Config.DB_HOST}:{Config.DB_PORT}/{DB_NAME}'


# 配置映射
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
