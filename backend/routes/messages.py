"""
消息通知路由模块
处理系统消息的增删改查
"""

from flask import Blueprint, request, jsonify
from services.message_service import MessageService
from utils import token_required

messages_bp = Blueprint('messages', __name__)

@messages_bp.route('/messages', methods=['GET'])
@token_required
def get_messages():
    """获取消息列表"""
    user_id = request.current_user.id
    is_read = request.args.get('is_read', type=lambda x: x.lower() == 'true') if 'is_read' in request.args else None
    page = request.args.get('page', type=int)
    page_size = request.args.get('pageSize', 10, type=int)
    
    result = MessageService.get_messages(user_id, is_read, page, page_size)
    return jsonify(result)

@messages_bp.route('/messages', methods=['POST'])
@token_required
def add_message():
    """添加消息"""
    data = request.json
    data['user_id'] = request.current_user.id
    result, status = MessageService.add_message(data)
    return jsonify(result), status

@messages_bp.route('/messages/<int:id>/read', methods=['PUT'])
@token_required
def mark_message_read(id):
    """标记消息为已读"""
    result, status = MessageService.mark_message_read(id, request.current_user.id)
    return jsonify(result), status

@messages_bp.route('/messages/<int:id>', methods=['DELETE'])
@token_required
def delete_message(id):
    """删除消息"""
    result, status = MessageService.delete_message(id, request.current_user.id)
    return jsonify(result), status

@messages_bp.route('/messages/unread-count', methods=['GET'])
@token_required
def get_unread_count():
    """获取未读消息数量"""
    user_id = request.current_user.id
    result = MessageService.get_unread_count(user_id)
    return jsonify(result)

@messages_bp.route('/messages/read_all', methods=['PUT'])
@token_required
def mark_all_messages_read():
    """标记所有消息为已读"""
    user_id = request.current_user.id
    result, status = MessageService.mark_all_messages_read(user_id)
    return jsonify(result), status
