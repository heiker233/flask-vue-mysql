"""
认证路由模块
处理用户登录、注册等功能
"""

from flask import Blueprint, request, jsonify
from services.auth_service import AuthService

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.json
    result, status = AuthService.login(data)
    return jsonify(result), status

@auth_bp.route('/register', methods=['POST'])
def register():
    """用户注册"""
    data = request.json
    result, status = AuthService.register(data)
    return jsonify(result), status
