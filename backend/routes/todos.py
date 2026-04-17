"""
待办事项路由模块
处理待办事项的增删改查
"""

from flask import Blueprint, request, jsonify
from services.todo_service import TodoService
from utils import token_required

todos_bp = Blueprint('todos', __name__)

@todos_bp.route('/todos', methods=['GET'])
@token_required
def get_todos():
    """获取待办事项列表"""
    user_id = request.current_user.id
    page = request.args.get('page', type=int)
    page_size = request.args.get('pageSize', 10, type=int)
    result = TodoService.get_todos(user_id, page, page_size)
    return jsonify(result)

@todos_bp.route('/todos', methods=['POST'])
@token_required
def add_todo():
    """添加待办事项"""
    data = request.json
    data['user_id'] = request.current_user.id
    result, status = TodoService.add_todo(data)
    return jsonify(result), status

@todos_bp.route('/todos/<int:id>', methods=['PUT'])
@token_required
def update_todo(id):
    """更新待办事项"""
    data = request.json
    result, status = TodoService.update_todo(id, data)
    return jsonify(result), status

@todos_bp.route('/todos/<int:id>', methods=['DELETE'])
@token_required
def delete_todo(id):
    """删除待办事项"""
    result, status = TodoService.delete_todo(id)
    return jsonify(result), status
