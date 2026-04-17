
from extensions import db
from models import User
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timedelta
from flask import current_app

class AuthService:
    @staticmethod
    def login(data):
        username = data.get('username')
        password = data.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            token_payload = {
                'user_id': user.id,
                'username': user.username,
                'role': user.role,
                'exp': datetime.utcnow() + current_app.config['JWT_EXPIRATION_DELTA']
            }
            token = jwt.encode(token_payload, current_app.config['SECRET_KEY'], algorithm='HS256')
            
            return {
                'success': True,
                'token': token,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'role': user.role
                }
            }, 200
        else:
            return {'success': False, 'message': '用户名或密码错误'}, 401

    @staticmethod
    def register(data):
        username = data.get('username')
        password = data.get('password')
        
        if not username or len(username) < 3:
            return {'success': False, 'message': '用户名长度至少为3个字符'}, 400
        if not password or len(password) < 6:
            return {'success': False, 'message': '密码长度至少为6个字符'}, 400
        
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return {'success': False, 'message': '用户名已存在'}, 400
        
        try:
            hashed_password = generate_password_hash(password)
            new_user = User(username=username, password=hashed_password, role='user')
            db.session.add(new_user)
            db.session.commit()
            
            token_payload = {
                'user_id': new_user.id,
                'username': new_user.username,
                'role': new_user.role,
                'exp': datetime.utcnow() + current_app.config['JWT_EXPIRATION_DELTA']
            }
            token = jwt.encode(token_payload, current_app.config['SECRET_KEY'], algorithm='HS256')
            
            return {
                'success': True,
                'message': '注册成功',
                'token': token,
                'user': {
                    'id': new_user.id,
                    'username': new_user.username,
                    'role': new_user.role
                }
            }, 200
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'注册失败: {str(e)}'}, 500
