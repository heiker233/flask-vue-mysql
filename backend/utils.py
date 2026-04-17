"""
通用工具模块
包含 JWT 验证装饰器等
"""
import jwt
from functools import wraps
from flask import request, jsonify, current_app
from models import User

def token_required(f):
    """验证 JWT Token 的装饰器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # 从请求头中获取 Authorization Token
        # 支持 'Authorization: Bearer <token>' 格式
        auth_header = request.headers.get('Authorization')
        if auth_header:
            if auth_header.startswith('Bearer '):
                token = auth_header.split(" ")[1]
            else:
                token = auth_header
        
        if not token:
            return jsonify({'success': False, 'message': '未提供验证凭据，请登录'}), 401
        
        try:
            # 解码 Token
            payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.get(payload['user_id'])
            
            if not current_user:
                return jsonify({'success': False, 'message': '验证失败，用户不存在'}), 401
                
        except jwt.ExpiredSignatureError:
            return jsonify({'success': False, 'message': '验证过期，请重新登录'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'success': False, 'message': '无效的验证凭据'}), 401
        except Exception as e:
            return jsonify({'success': False, 'message': f'验证出错: {str(e)}'}), 401
            
        # 将当前用户信息存入 request，方便在路由中使用
        request.current_user = current_user
        
        return f(*args, **kwargs)
        
    return decorated

def admin_required(f):
    """验证管理员权限的装饰器"""
    @wraps(f)
    @token_required
    def decorated(*args, **kwargs):
        if request.current_user.role != 'admin':
            return jsonify({'success': False, 'message': '权限不足，仅限管理员访问'}), 403
        return f(*args, **kwargs)
    return decorated
