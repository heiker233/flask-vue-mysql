"""
待办事项路由模块
处理待办事项的增删改查
"""
from flask import Blueprint, request, jsonify
from extensions import db
from models import Todo
from datetime import datetime

todos_bp = Blueprint('todos', __name__)


@todos_bp.route('/todos', methods=['GET'])
def get_todos():
    """获取待办事项列表"""
    user_id = request.args.get('user_id', type=int)
    
    query = Todo.query
    if user_id:
        query = query.filter_by(user_id=user_id)
    
    # 排序：未完成的在前，按优先级排序
    query = query.order_by(Todo.completed.asc(), Todo.priority.desc(), Todo.created_at.desc())
    
    todos = query.all()
    
    return jsonify([{
        'id': t.id,
        'user_id': t.user_id,
        'content': t.content,
        'priority': t.priority,
        'completed': t.completed,
        'due_date': t.due_date.isoformat() if t.due_date else None,
        'created_at': t.created_at.isoformat() if t.created_at else None,
        'updated_at': t.updated_at.isoformat() if t.updated_at else None
    } for t in todos])


@todos_bp.route('/todos', methods=['POST'])
def add_todo():
    """添加待办事项"""
    data = request.json
    
    if not data.get('content'):
        return jsonify({'success': False, 'message': '待办内容不能为空'}), 400
    
    # 解析截止日期
    due_date = None
    if data.get('due_date'):
        try:
            due_date = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00'))
        except:
            pass
    
    try:
        new_todo = Todo(
            user_id=data.get('user_id', 1),  # TODO: 从token获取
            content=data['content'],
            priority=data.get('priority', 'medium'),
            completed=data.get('completed', False),
            due_date=due_date
        )
        db.session.add(new_todo)
        db.session.commit()
        
        return jsonify({
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
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'添加失败: {str(e)}'}), 500


@todos_bp.route('/todos/<int:id>', methods=['PUT'])
def update_todo(id):
    """更新待办事项"""
    todo = Todo.query.get(id)
    if not todo:
        return jsonify({'success': False, 'message': '待办事项不存在'}), 404
    
    data = request.json
    
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
        return jsonify({'success': True, 'message': '待办事项更新成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'更新失败: {str(e)}'}), 500


@todos_bp.route('/todos/<int:id>', methods=['DELETE'])
def delete_todo(id):
    """删除待办事项"""
    todo = Todo.query.get(id)
    if not todo:
        return jsonify({'success': False, 'message': '待办事项不存在'}), 404
    
    try:
        db.session.delete(todo)
        db.session.commit()
        return jsonify({'success': True, 'message': '待办事项删除成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'删除失败: {str(e)}'}), 500
