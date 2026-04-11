"""
消息通知路由模块
处理系统消息的增删改查
"""
from flask import Blueprint, request, jsonify
from extensions import db
from models import Message
from datetime import datetime

messages_bp = Blueprint('messages', __name__)


@messages_bp.route('/messages', methods=['GET'])
def get_messages():
    """获取消息列表"""
    user_id = request.args.get('user_id', type=int)
    is_read = request.args.get('is_read', type=lambda x: x.lower() == 'true')
    
    query = Message.query
    if user_id:
        query = query.filter_by(user_id=user_id)
    if is_read is not None:
        query = query.filter_by(is_read=is_read)
    
    query = query.order_by(Message.created_at.desc())
    messages = query.all()
    
    return jsonify([{
        'id': m.id,
        'user_id': m.user_id,
        'title': m.title,
        'content': m.content,
        'msg_type': m.msg_type,
        'is_read': m.is_read,
        'created_at': m.created_at.isoformat() if m.created_at else None
    } for m in messages])


@messages_bp.route('/messages', methods=['POST'])
def add_message():
    """添加消息"""
    data = request.json
    
    try:
        new_message = Message(
            user_id=data.get('user_id', 1),
            title=data.get('title', ''),
            content=data.get('content', ''),
            msg_type=data.get('msg_type', 'info'),
            is_read=data.get('is_read', False)
        )
        db.session.add(new_message)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '消息添加成功',
            'msg': {
                'id': new_message.id,
                'title': new_message.title,
                'content': new_message.content,
                'msg_type': new_message.msg_type,
                'is_read': new_message.is_read,
                'created_at': new_message.created_at.isoformat() if new_message.created_at else None
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'添加失败: {str(e)}'}), 500


@messages_bp.route('/messages/<int:id>/read', methods=['PUT'])
def mark_message_read(id):
    """标记消息为已读"""
    message = Message.query.get(id)
    if not message:
        return jsonify({'success': False, 'message': '消息不存在'}), 404
    
    message.is_read = True
    
    try:
        db.session.commit()
        return jsonify({'success': True, 'message': '消息已标记为已读'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'操作失败: {str(e)}'}), 500


@messages_bp.route('/messages/<int:id>', methods=['DELETE'])
def delete_message(id):
    """删除消息"""
    message = Message.query.get(id)
    if not message:
        return jsonify({'success': False, 'message': '消息不存在'}), 404
    
    try:
        db.session.delete(message)
        db.session.commit()
        return jsonify({'success': True, 'message': '消息删除成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'删除失败: {str(e)}'}), 500


@messages_bp.route('/messages/unread-count', methods=['GET'])
def get_unread_count():
    """获取未读消息数量"""
    user_id = request.args.get('user_id', type=int)
    
    query = Message.query.filter_by(is_read=False)
    if user_id:
        query = query.filter_by(user_id=user_id)
    
    count = query.count()
    return jsonify({'count': count})


@messages_bp.route('/messages/read_all', methods=['PUT'])
def mark_all_messages_read():
    """标记所有消息为已读"""
    data = request.json
    user_id = data.get('user_id')
    
    try:
        query = Message.query.filter_by(is_read=False)
        if user_id:
            query = query.filter_by(user_id=user_id)
        
        count = query.update({'is_read': True})
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'已标记 {count} 条消息为已读',
            'count': count
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'操作失败: {str(e)}'}), 500
