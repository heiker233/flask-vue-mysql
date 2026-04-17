
from extensions import db
from models import Message
from datetime import datetime

class MessageService:
    @staticmethod
    def get_messages(user_id=None, is_read=None, page=None, page_size=10):
        query = Message.query
        if user_id:
            query = query.filter_by(user_id=user_id)
        if is_read is not None:
            query = query.filter_by(is_read=is_read)
        
        query = query.order_by(Message.created_at.desc())
        
        def format_msg(m):
            return {
                'id': m.id,
                'user_id': m.user_id,
                'title': m.title,
                'content': m.content,
                'msg_type': m.msg_type,
                'is_read': m.is_read,
                'created_at': m.created_at.isoformat() if m.created_at else None
            }
            
        if page:
            pagination = query.paginate(page=page, per_page=page_size, error_out=False)
            return {
                'items': [format_msg(m) for m in pagination.items],
                'total': pagination.total,
                'page': pagination.page,
                'pages': pagination.pages
            }
            
        messages = query.all()
        return [format_msg(m) for m in messages]

    @staticmethod
    def add_message(data):
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
            
            return {
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
            }, 200
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'添加失败: {str(e)}'}, 500

    @staticmethod
    def mark_message_read(id):
        message = Message.query.get(id)
        if not message:
            return {'success': False, 'message': '消息不存在'}, 404
        
        message.is_read = True
        
        try:
            db.session.commit()
            return {'success': True, 'message': '消息已标记为已读'}, 200
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'操作失败: {str(e)}'}, 500

    @staticmethod
    def delete_message(id):
        message = Message.query.get(id)
        if not message:
            return {'success': False, 'message': '消息不存在'}, 404
        
        try:
            db.session.delete(message)
            db.session.commit()
            return {'success': True, 'message': '消息删除成功'}, 200
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'删除失败: {str(e)}'}, 500

    @staticmethod
    def get_unread_count(user_id=None):
        query = Message.query.filter_by(is_read=False)
        if user_id:
            query = query.filter_by(user_id=user_id)
        
        count = query.count()
        return {'count': count}

    @staticmethod
    def mark_all_messages_read(user_id=None):
        try:
            query = Message.query.filter_by(is_read=False)
            if user_id:
                query = query.filter_by(user_id=user_id)
            
            count = query.update({'is_read': True})
            db.session.commit()
            
            return {
                'success': True,
                'message': f'已标记 {count} 条消息为已读',
                'count': count
            }, 200
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'操作失败: {str(e)}'}, 500
