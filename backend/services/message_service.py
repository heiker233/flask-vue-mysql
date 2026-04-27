from datetime import datetime, timedelta

from extensions import db
from models import Deal, Message, Todo, User


class MessageService:
    @staticmethod
    def _build_pending_deal_message(deal):
        customer_name = deal.customer.name if deal.customer else '未知客户'
        return {
            'title': '交易待审批提醒',
            'content': f'交易#{deal.id}（客户：{customer_name}）待审批'
        }

    @staticmethod
    def _format_msg(message):
        return {
            'id': message.id,
            'user_id': message.user_id,
            'title': message.title,
            'content': message.content,
            'msg_type': message.msg_type,
            'is_read': message.is_read,
            'created_at': message.created_at.isoformat() if message.created_at else None
        }

    @staticmethod
    def _create_message(user_id, title, content, msg_type='info', is_read=False, commit=True):
        new_message = Message(
            user_id=user_id,
            title=title,
            content=content,
            msg_type=msg_type,
            is_read=is_read
        )
        db.session.add(new_message)
        if commit:
            db.session.commit()
        return new_message

    @staticmethod
    def add_message(data):
        try:
            new_message = MessageService._create_message(
                user_id=data.get('user_id', 1),
                title=data.get('title', ''),
                content=data.get('content', ''),
                msg_type=data.get('msg_type', 'info'),
                is_read=data.get('is_read', False)
            )

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
    def notify_user(user_id, title, content, msg_type='info'):
        try:
            MessageService._create_message(
                user_id=user_id,
                title=title,
                content=content,
                msg_type=msg_type
            )
            return True
        except Exception:
            db.session.rollback()
            return False

    @staticmethod
    def notify_admins(title, content, msg_type='deal'):
        try:
            admin_ids = [user.id for user in User.query.filter_by(role='admin').all()]
            if not admin_ids:
                return True

            for admin_id in admin_ids:
                MessageService._create_message(
                    user_id=admin_id,
                    title=title,
                    content=content,
                    msg_type=msg_type,
                    commit=False
                )
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            return False

    @staticmethod
    def ensure_todo_reminders(user_id):
        today = datetime.utcnow().date()
        start_of_day = datetime.combine(today, datetime.min.time())
        end_of_day = start_of_day + timedelta(days=1)

        todos = Todo.query.filter(
            Todo.user_id == user_id,
            Todo.completed.is_(False),
            Todo.due_date.isnot(None)
        ).all()

        try:
            for todo in todos:
                due_date = todo.due_date.date()
                if due_date < today:
                    title = '待办逾期提醒'
                elif due_date == today:
                    title = '待办到期提醒'
                else:
                    continue

                content = todo.content
                exists = Message.query.filter(
                    Message.user_id == user_id,
                    Message.msg_type == 'todo',
                    Message.title == title,
                    Message.content == content,
                    Message.created_at >= start_of_day,
                    Message.created_at < end_of_day
                ).first()
                if exists:
                    continue

                MessageService._create_message(
                    user_id=user_id,
                    title=title,
                    content=content,
                    msg_type='todo',
                    commit=False
                )

            db.session.commit()
        except Exception:
            db.session.rollback()

    @staticmethod
    def ensure_admin_pending_deal_reminders(user_id):
        user = User.query.get(user_id)
        if not user or user.role != 'admin':
            return

        pending_deals = Deal.query.filter_by(approval_status='pending').all()

        try:
            for deal in pending_deals:
                payload = MessageService._build_pending_deal_message(deal)
                exists = Message.query.filter_by(
                    user_id=user_id,
                    msg_type='deal',
                    title=payload['title'],
                    content=payload['content']
                ).first()
                if exists:
                    continue

                MessageService._create_message(
                    user_id=user_id,
                    title=payload['title'],
                    content=payload['content'],
                    msg_type='deal',
                    commit=False
                )

            db.session.commit()
        except Exception:
            db.session.rollback()

    @staticmethod
    def get_messages(user_id=None, is_read=None, page=None, page_size=10):
        if user_id:
            MessageService.ensure_todo_reminders(user_id)
            MessageService.ensure_admin_pending_deal_reminders(user_id)

        query = Message.query
        if user_id:
            query = query.filter_by(user_id=user_id)
        if is_read is not None:
            query = query.filter_by(is_read=is_read)

        query = query.order_by(Message.created_at.desc())

        if page:
            pagination = query.paginate(page=page, per_page=page_size, error_out=False)
            return {
                'items': [MessageService._format_msg(m) for m in pagination.items],
                'total': pagination.total,
                'page': pagination.page,
                'pages': pagination.pages
            }

        messages = query.all()
        return [MessageService._format_msg(m) for m in messages]

    @staticmethod
    def mark_message_read(message_id, current_user_id=None):
        query = Message.query.filter_by(id=message_id)
        if current_user_id is not None:
            query = query.filter_by(user_id=current_user_id)

        message = query.first()
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
    def delete_message(message_id, current_user_id=None):
        query = Message.query.filter_by(id=message_id)
        if current_user_id is not None:
            query = query.filter_by(user_id=current_user_id)

        message = query.first()
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
