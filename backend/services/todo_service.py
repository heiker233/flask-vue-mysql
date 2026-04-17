
from extensions import db
from models import Todo
from datetime import datetime

class TodoService:
    @staticmethod
    def get_todos(user_id=None, page=None, page_size=10):
        query = Todo.query
        if user_id:
            query = query.filter_by(user_id=user_id)
        
        query = query.order_by(Todo.completed.asc(), Todo.priority.desc(), Todo.created_at.desc())
        
        def format_todo(t):
            return {
                'id': t.id,
                'user_id': t.user_id,
                'content': t.content,
                'priority': t.priority,
                'completed': t.completed,
                'due_date': t.due_date.isoformat() if t.due_date else None,
                'created_at': t.created_at.isoformat() if t.created_at else None,
                'updated_at': t.updated_at.isoformat() if t.updated_at else None
            }
            
        if page:
            pagination = query.paginate(page=page, per_page=page_size, error_out=False)
            return {
                'items': [format_todo(t) for t in pagination.items],
                'total': pagination.total,
                'page': pagination.page,
                'pages': pagination.pages
            }
            
        todos = query.all()
        return [format_todo(t) for t in todos]

    @staticmethod
    def add_todo(data):
        if not data.get('content'):
            return {'success': False, 'message': '待办内容不能为空'}, 400
        
        due_date = None
        if data.get('due_date'):
            try:
                due_date = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00'))
            except:
                pass
        
        try:
            new_todo = Todo(
                user_id=data.get('user_id', 1),
                content=data['content'],
                priority=data.get('priority', 'medium'),
                completed=data.get('completed', False),
                due_date=due_date
            )
            db.session.add(new_todo)
            db.session.commit()
            
            return {
                'success': True,
                'message': '待办事项添加成功',
                'todo': {
                    'id': new_todo.id,
                    'content': new_todo.content,
                    'priority': new_todo.priority,
                    'completed': new_todo.completed,
                    'due_date': new_todo.due_date.isoformat() if new_todo.due_date else None,
                    'created_at': new_todo.created_at.isoformat() if new_todo.created_at else None
                }
            }, 200
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'添加失败: {str(e)}'}, 500

    @staticmethod
    def update_todo(id, data):
        todo = Todo.query.get(id)
        if not todo:
            return {'success': False, 'message': '待办事项不存在'}, 404
        
        todo.content = data.get('content', todo.content)
        todo.priority = data.get('priority', todo.priority)
        todo.completed = data.get('completed', todo.completed)
        
        if 'due_date' in data:
            if data['due_date']:
                try:
                    todo.due_date = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00'))
                except:
                    todo.due_date = None
            else:
                todo.due_date = None
        
        todo.updated_at = datetime.utcnow()
        
        try:
            db.session.commit()
            return {'success': True, 'message': '待办事项更新成功'}, 200
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'更新失败: {str(e)}'}, 500

    @staticmethod
    def delete_todo(id):
        todo = Todo.query.get(id)
        if not todo:
            return {'success': False, 'message': '待办事项不存在'}, 404
        
        try:
            db.session.delete(todo)
            db.session.commit()
            return {'success': True, 'message': '待办事项删除成功'}, 200
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'删除失败: {str(e)}'}, 500
