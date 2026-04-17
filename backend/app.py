"""
客户管理系统后端主应用
使用模块化结构，支持环境变量配置
"""
from flask import Flask
from flask_cors import CORS
from config import config
from extensions import db, cors
from models import User, Customer, CustomerTag, FollowUp, Deal, Product, Todo, Message, DealApproval
from werkzeug.security import generate_password_hash
import os

def create_app(config_name=None):
    """应用工厂函数"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # 初始化扩展
    db.init_app(app)
    cors.init_app(app, resources={r"/*": {"origins": app.config.get('CORS_ORIGINS', '*')}})
    
    # 注册蓝图
    from routes.auth import auth_bp
    from routes.customers import customers_bp
    from routes.follow_ups import follow_ups_bp
    from routes.deals import deals_bp
    from routes.products import products_bp
    from routes.stats import stats_bp
    from routes.todos import todos_bp
    from routes.import_export import import_export_bp
    from routes.users import users_bp
    from routes.messages import messages_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(customers_bp, url_prefix='/api')
    app.register_blueprint(follow_ups_bp, url_prefix='/api')
    app.register_blueprint(deals_bp, url_prefix='/api')
    app.register_blueprint(products_bp, url_prefix='/api')
    app.register_blueprint(stats_bp, url_prefix='/api')
    app.register_blueprint(todos_bp, url_prefix='/api')
    app.register_blueprint(import_export_bp, url_prefix='/api')
    app.register_blueprint(users_bp, url_prefix='/api')
    app.register_blueprint(messages_bp, url_prefix='/api')
    
    # 创建数据库表和初始数据
    with app.app_context():
        db.create_all()
        
        # 添加管理员用户（如果不存在）
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin_password = os.environ.get('ADMIN_PASSWORD', '123456')
            hashed_password = generate_password_hash(admin_password)
            admin = User(username='admin', password=hashed_password, role='admin')
            db.session.add(admin)
            db.session.commit()
            print(f'管理员用户已创建: admin / {admin_password}')
    
    return app

# 创建应用实例（用于直接运行）
app = create_app()

if __name__ == '__main__':
    app.run(debug=app.config.get('DEBUG', True), host='0.0.0.0', port=5000)
