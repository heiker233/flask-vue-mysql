
from extensions import db
from models import User
from werkzeug.security import generate_password_hash

class UserService:
    @staticmethod
    def get_users(page=None, page_size=10):
        query = User.query
        def format_user(u):
            return {
                'id': u.id,
                'username': u.username,
                'role': u.role,
                'created_at': u.created_at.isoformat() if u.created_at else None
            }
        
        if page:
            pagination = query.paginate(page=page, per_page=page_size, error_out=False)
            return {
                'items': [format_user(u) for u in pagination.items],
                'total': pagination.total,
                'page': pagination.page,
                'pages': pagination.pages
            }
            
        users = query.all()
        return [format_user(u) for u in users]

    @staticmethod
    def add_user(data):
        username = data.get('username')
        password = data.get('password')
        role = data.get('role', 'user')
        
        if not username or not password:
            return {'success': False, 'message': '用户名和密码不能为空'}, 400
        
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return {'success': False, 'message': '用户名已存在'}, 400
        
        try:
            hashed_password = generate_password_hash(password)
            new_user = User(username=username, password=hashed_password, role=role)
            db.session.add(new_user)
            db.session.commit()
            
            return {
                'success': True,
                'message': '用户添加成功',
                'user': {
                    'id': new_user.id,
                    'username': new_user.username,
                    'role': new_user.role
                }
            }, 200
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'添加失败: {str(e)}'}, 500

    @staticmethod
    def update_user(id, data):
        user = User.query.get(id)
        if not user:
            return {'success': False, 'message': '用户不存在'}, 404
        
        new_username = data.get('username')
        if new_username and new_username != user.username:
            existing = User.query.filter_by(username=new_username).first()
            if existing:
                return {'success': False, 'message': '用户名已存在'}, 400
            user.username = new_username
        
        if 'role' in data:
            user.role = data['role']
        
        if 'password' in data:
            hashed_password = generate_password_hash(data['password'])
            user.password = hashed_password
        
        try:
            db.session.commit()
            return {'success': True, 'message': '用户信息更新成功'}, 200
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'更新失败: {str(e)}'}, 500

    @staticmethod
    def delete_user(id):
        user = User.query.get(id)
        if not user:
            return {'success': False, 'message': '用户不存在'}, 404
        
        if user.role == 'admin':
            admin_count = User.query.filter_by(role='admin').count()
            if admin_count <= 1:
                return {'success': False, 'message': '不能删除最后一个管理员'}, 400
        
        try:
            db.session.delete(user)
            db.session.commit()
            return {'success': True, 'message': '用户删除成功'}, 200
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'删除失败: {str(e)}'}, 500

    @staticmethod
    def reset_password(id, data):
        user = User.query.get(id)
        if not user:
            return {'success': False, 'message': '用户不存在'}, 404
        
        new_password = data.get('new_password', '123456')
        
        try:
            hashed_password = generate_password_hash(new_password)
            user.password = hashed_password
            db.session.commit()
            return {
                'success': True,
                'message': f'密码已重置为: {new_password}'
            }, 200
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'重置失败: {str(e)}'}, 500
