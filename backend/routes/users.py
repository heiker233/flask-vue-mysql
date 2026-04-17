"""
用户管理路由模块（管理员功能）
处理用户的增删改查
"""

from flask import Blueprint, request, jsonify
from services.user_service import UserService
from utils import token_required, admin_required

users_bp = Blueprint('users', __name__)

@users_bp.route('/users', methods=['GET'])
@token_required
def get_users():
    """获取用户列表"""
    page = request.args.get('page', type=int)
    page_size = request.args.get('pageSize', 10, type=int)
    result = UserService.get_users(page, page_size)
    return jsonify(result)

@users_bp.route('/users', methods=['POST'])
@admin_required
def add_user():
    """添加用户（管理员功能）"""
    data = request.json
    result, status = UserService.add_user(data)
    return jsonify(result), status

@users_bp.route('/users/<int:id>', methods=['PUT'])
@admin_required
def update_user(id):
    """更新用户信息（支持重置密码）"""
    data = request.json
    result, status = UserService.update_user(id, data)
    return jsonify(result), status

@users_bp.route('/users/<int:id>', methods=['DELETE'])
@admin_required
def delete_user(id):
    """删除用户"""
    result, status = UserService.delete_user(id)
    return jsonify(result), status

@users_bp.route('/users/<int:id>/reset-password', methods=['POST'])
@admin_required
def reset_password(id):
    """重置用户密码"""
    data = request.json
    result, status = UserService.reset_password(id, data)
    return jsonify(result), status
