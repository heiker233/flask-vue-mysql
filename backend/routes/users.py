"""
用户管理路由模块（管理员功能）
处理用户的增删改查
"""
from flask import Blueprint, request, jsonify
from extensions import db
from models import User
from werkzeug.security import generate_password_hash

users_bp = Blueprint('users', __name__)


@users_bp.route('/users', methods=['GET'])
def get_users():
    """获取用户列表"""
    users = User.query.all()
    return jsonify([{
        'id': u.id,
        'username': u.username,
        'role': u.role,
        'created_at': u.created_at.isoformat() if u.created_at else None
    } for u in users])


@users_bp.route('/users', methods=['POST'])
def add_user():
    """添加用户（管理员功能）"""
    data = request.json
    username = data.get('username')
    password = data.get('password')
    role = data.get('role', 'user')
    
    if not username or not password:
        return jsonify({'success': False, 'message': '用户名和密码不能为空'}), 400
    
    # 检查用户名是否已存在
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({'success': False, 'message': '用户名已存在'}), 400
    
    try:
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password, role=role)
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '用户添加成功',
            'user': {
                'id': new_user.id,
                'username': new_user.username,
                'role': new_user.role
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'添加失败: {str(e)}'}), 500


@users_bp.route('/users/<int:id>', methods=['PUT'])
def update_user(id):
    """更新用户信息（支持重置密码）"""
    user = User.query.get(id)
    if not user:
        return jsonify({'success': False, 'message': '用户不存在'}), 404
    
    data = request.json
    
    # 如果更新用户名，检查是否重复
    new_username = data.get('username')
    if new_username and new_username != user.username:
        existing = User.query.filter_by(username=new_username).first()
        if existing:
            return jsonify({'success': False, 'message': '用户名已存在'}), 400
        user.username = new_username
    
    # 更新角色
    if 'role' in data:
        user.role = data['role']
    
    # 重置密码
    if 'password' in data:
        hashed_password = generate_password_hash(data['password'])
        user.password = hashed_password
    
    try:
        db.session.commit()
        return jsonify({'success': True, 'message': '用户信息更新成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'更新失败: {str(e)}'}), 500


@users_bp.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    """删除用户"""
    user = User.query.get(id)
    if not user:
        return jsonify({'success': False, 'message': '用户不存在'}), 404
    
    # 防止删除最后一个管理员
    if user.role == 'admin':
        admin_count = User.query.filter_by(role='admin').count()
        if admin_count <= 1:
            return jsonify({'success': False, 'message': '不能删除最后一个管理员'}), 400
    
    try:
        db.session.delete(user)
        db.session.commit()
        return jsonify({'success': True, 'message': '用户删除成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'删除失败: {str(e)}'}), 500


@users_bp.route('/users/<int:id>/reset-password', methods=['POST'])
def reset_password(id):
    """重置用户密码"""
    user = User.query.get(id)
    if not user:
        return jsonify({'success': False, 'message': '用户不存在'}), 404
    
    data = request.json
    new_password = data.get('new_password', '123456')
    
    try:
        hashed_password = generate_password_hash(new_password)
        user.password = hashed_password
        db.session.commit()
        return jsonify({
            'success': True,
            'message': f'密码已重置为: {new_password}'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'重置失败: {str(e)}'}), 500
