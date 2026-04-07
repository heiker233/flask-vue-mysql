from flask import Flask, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime, timedelta
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import os

app = Flask(__name__)
# 配置 CORS 以允许所有来源（解决同一热点下手机无法登录问题）
CORS(app, resources={r"/*": {"origins": "*"}})

# 数据库配置
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:daige520@localhost/customer_management'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# JWT密钥配置
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
app.config['JWT_EXPIRATION_DELTA'] = timedelta(hours=24)

db = SQLAlchemy(app)

# Token验证装饰器
def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        # 从请求头中获取token
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # Bearer <token>
            except IndexError:
                return jsonify({'success': False, 'message': 'Token格式错误'}), 401
        
        if not token:
            return jsonify({'success': False, 'message': '缺少认证Token'}), 401
        
        try:
            # 验证token
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.get(payload['user_id'])
            if not current_user:
                return jsonify({'success': False, 'message': '用户不存在'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'success': False, 'message': 'Token已过期'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'success': False, 'message': '无效的Token'}), 401
        
        # 将当前用户信息传递给被装饰的函数
        return f(current_user, *args, **kwargs)
    return decorated_function

# 权限检查装饰器（需要配合token_required使用）
def admin_required(f):
    @wraps(f)
    def decorated_function(current_user, *args, **kwargs):
        # 从数据库查询用户真实角色，而不是依赖客户端传递的角色
        if current_user.role != 'admin':
            return jsonify({'success': False, 'message': '权限不足，需要管理员权限'}), 403
        return f(current_user, *args, **kwargs)
    return decorated_function

# 用户表
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), default='user')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    customers = db.relationship('Customer', backref='user', lazy=True)
    follow_ups = db.relationship('FollowUp', backref='user', lazy=True)
    deals = db.relationship('Deal', backref='user', lazy=True)
    todos = db.relationship('Todo', backref='user', lazy=True)

# 待办事项表
class Todo(db.Model):
    __tablename__ = 'todos'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.String(200), nullable=False)
    priority = db.Column(db.String(20), default='medium')  # high, medium, low
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# 客户表
class Customer(db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    company = db.Column(db.String(100))
    industry = db.Column(db.String(50))
    status = db.Column(db.String(20), default='potential')
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    follow_ups = db.relationship('FollowUp', backref='customer', lazy=True)
    deals = db.relationship('Deal', backref='customer', lazy=True)

# 跟进记录表
class FollowUp(db.Model):
    __tablename__ = 'follow_ups'
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    follow_type = db.Column(db.String(50))
    next_follow_date = db.Column(db.Date)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# 交易表
class Deal(db.Model):
    __tablename__ = 'deals'
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    deal_status = db.Column(db.String(20), default='negotiating')
    product = db.Column(db.String(100))
    expected_close_date = db.Column(db.Date)
    actual_close_date = db.Column(db.Date)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# 创建数据库表并添加初始数据
with app.app_context():
    db.create_all()
    # 添加管理员用户（如果不存在）
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        # 使用密码哈希存储
        hashed_password = generate_password_hash('123456')
        admin = User(username='admin', password=hashed_password, role='admin')
        db.session.add(admin)
        db.session.commit()
        print('管理员用户已创建: admin / 123456')

# 用户认证
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    user = User.query.filter_by(username=username).first()
    # 使用密码哈希验证
    if user and check_password_hash(user.password, password):
        # 生成JWT token
        token_payload = {
            'user_id': user.id,
            'username': user.username,
            'role': user.role,
            'exp': datetime.utcnow() + app.config['JWT_EXPIRATION_DELTA']
        }
        token = jwt.encode(token_payload, app.config['SECRET_KEY'], algorithm='HS256')
        
        return jsonify({
            'success': True,
            'token': token,
            'user': {
                'id': user.id,
                'username': user.username,
                'role': user.role
            }
        })
    else:
        return jsonify({'success': False, 'message': '用户名或密码错误'}), 401

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    # 验证用户名和密码长度
    if not username or len(username) < 3:
        return jsonify({'success': False, 'message': '用户名长度至少为3个字符'}), 400
    if not password or len(password) < 6:
        return jsonify({'success': False, 'message': '密码长度至少为6个字符'}), 400
    
    # 检查用户名是否已存在
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({'success': False, 'message': '用户名已存在'}), 400
    
    try:
        # 使用密码哈希存储
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password, role='user')
        db.session.add(new_user)
        db.session.commit()
        
        # 生成JWT token
        token_payload = {
            'user_id': new_user.id,
            'username': new_user.username,
            'role': new_user.role,
            'exp': datetime.utcnow() + app.config['JWT_EXPIRATION_DELTA']
        }
        token = jwt.encode(token_payload, app.config['SECRET_KEY'], algorithm='HS256')
        
        return jsonify({
            'success': True,
            'message': '注册成功',
            'token': token,
            'user': {
                'id': new_user.id,
                'username': new_user.username,
                'role': new_user.role
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': '注册失败: {}'.format(str(e))}), 500

# 客户模块 API

@app.route('/api/customers', methods=['GET'])
def get_customers():
    customers = Customer.query.order_by(Customer.created_at.desc()).all()
    return jsonify([{
        'id': c.id,
        'name': c.name,
        'phone': c.phone,
        'email': c.email,
        'company': c.company,
        'industry': c.industry,
        'status': c.status,
        'created_at': c.created_at.isoformat()
    } for c in customers])

@app.route('/api/customers', methods=['POST'])
def add_customer():
    data = request.json
    new_customer = Customer(
        name=data['name'],
        phone=data.get('phone'),
        email=data.get('email'),
        company=data.get('company'),
        industry=data.get('industry'),
        status=data.get('status', 'potential'),
        created_by=1
    )
    db.session.add(new_customer)
    db.session.commit()
    return jsonify({'success': True, 'message': '客户添加成功', 'customer': {'id': new_customer.id}})

@app.route('/api/customers/<int:id>', methods=['PUT'])
def update_customer(id):
    customer = Customer.query.get(id)
    if not customer:
        return jsonify({'success': False, 'message': '客户不存在'}), 404
    
    data = request.json
    customer.name = data.get('name', customer.name)
    customer.phone = data.get('phone', customer.phone)
    customer.email = data.get('email', customer.email)
    customer.company = data.get('company', customer.company)
    customer.industry = data.get('industry', customer.industry)
    customer.status = data.get('status', customer.status)
    
    db.session.commit()
    return jsonify({'success': True, 'message': '客户信息更新成功'})

@app.route('/api/customers/<int:id>', methods=['DELETE'])
def delete_customer(id):
    customer = Customer.query.get(id)
    if not customer:
        return jsonify({'success': False, 'message': '客户不存在'}), 404
    
    try:
        # 删除相关的跟进记录和交易记录
        FollowUp.query.filter_by(customer_id=id).delete()
        Deal.query.filter_by(customer_id=id).delete()
        
        # 删除客户
        db.session.delete(customer)
        db.session.commit()
        return jsonify({'success': True, 'message': '客户删除成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'删除失败: {str(e)}'}), 500

# 跟进记录模块 API

@app.route('/api/follow-ups', methods=['GET'])
def get_follow_ups():
    follow_ups = FollowUp.query.order_by(FollowUp.created_at.desc()).all()
    return jsonify([{
        'id': fu.id,
        'customer_id': fu.customer_id,
        'customer_name': fu.customer.name if fu.customer else None,
        'content': fu.content,
        'follow_type': fu.follow_type,
        'next_follow_date': fu.next_follow_date.isoformat() if fu.next_follow_date else None,
        'created_at': fu.created_at.isoformat()
    } for fu in follow_ups])

@app.route('/api/follow-ups', methods=['POST'])
def add_follow_up():
    data = request.json
    
    # 验证必要字段
    if 'customer_id' not in data or 'content' not in data:
        return jsonify({'success': False, 'message': '缺少必要字段'}), 400
    
    # 验证客户是否存在
    customer = Customer.query.get(data['customer_id'])
    if not customer:
        return jsonify({'success': False, 'message': '客户不存在'}), 400
    
    # 处理日期格式，支持带有时区信息的ISO格式
    next_follow_date = None
    if data.get('next_follow_date'):
        date_str = data['next_follow_date']
        # 尝试多种日期格式解析
        for fmt in ['%Y-%m-%d', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%S.%f', '%Y-%m-%dT%H:%M:%S.%fZ']:
            try:
                next_follow_date = datetime.strptime(date_str[:23] if '.' in date_str else date_str, fmt).date()
                break
            except ValueError:
                continue
    
    try:
        new_follow_up = FollowUp(
            customer_id=data['customer_id'],
            content=data['content'],
            follow_type=data.get('follow_type'),
            next_follow_date=next_follow_date,
            created_by=1
        )
        db.session.add(new_follow_up)
        db.session.commit()
        return jsonify({'success': True, 'message': '跟进记录添加成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'添加失败: {str(e)}'}), 500

@app.route('/api/follow-ups/<int:id>', methods=['DELETE'])
def delete_follow_up(id):
    follow_up = FollowUp.query.get(id)
    if not follow_up:
        return jsonify({'success': False, 'message': '跟进记录不存在'}), 404
    
    try:
        db.session.delete(follow_up)
        db.session.commit()
        return jsonify({'success': True, 'message': '跟进记录删除成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'删除失败: {str(e)}'}), 500

@app.route('/api/follow-ups/<int:id>', methods=['PUT'])
def update_follow_up(id):
    follow_up = FollowUp.query.get(id)
    if not follow_up:
        return jsonify({'success': False, 'message': '跟进记录不存在'}), 404
    
    data = request.json
    
    # 如果更新客户ID，验证新客户是否存在
    if 'customer_id' in data:
        customer = Customer.query.get(data['customer_id'])
        if not customer:
            return jsonify({'success': False, 'message': '新客户不存在'}), 400
        follow_up.customer_id = data['customer_id']
    
    follow_up.content = data.get('content', follow_up.content)
    follow_up.follow_type = data.get('follow_type', follow_up.follow_type)
    
    # 更新日期处理
    if data.get('next_follow_date'):
        date_str = data['next_follow_date']
        for fmt in ['%Y-%m-%d', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%S.%f', '%Y-%m-%dT%H:%M:%S.%fZ']:
            try:
                follow_up.next_follow_date = datetime.strptime(date_str[:23] if '.' in date_str else date_str, fmt).date()
                break
            except ValueError:
                continue
    
    try:
        db.session.commit()
        return jsonify({'success': True, 'message': '跟进记录更新成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'更新失败: {str(e)}'}), 500

# 交易模块 API

@app.route('/api/deals', methods=['GET'])
def get_deals():
    deals = Deal.query.order_by(Deal.created_at.desc()).all()
    return jsonify([{
        'id': d.id,
        'customer_id': d.customer_id,
        'customer_name': d.customer.name if d.customer else None,
        'amount': d.amount,
        'deal_status': d.deal_status,
        'product': d.product,
        'expected_close_date': d.expected_close_date.isoformat() if d.expected_close_date else None,
        'created_at': d.created_at.isoformat()
    } for d in deals])

@app.route('/api/deals', methods=['POST'])
def add_deal():
    data = request.json
    
    # 验证必要字段
    if 'customer_id' not in data or 'amount' not in data:
        return jsonify({'success': False, 'message': '缺少必要字段'}), 400
    
    # 验证客户是否存在
    customer = Customer.query.get(data['customer_id'])
    if not customer:
        return jsonify({'success': False, 'message': '客户不存在'}), 400
    
    # 处理日期格式，支持带有时区信息的ISO格式
    expected_close_date = None
    if data.get('expected_close_date'):
        date_str = data['expected_close_date']
        # 尝试多种日期格式解析
        for fmt in ['%Y-%m-%d', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%S.%f', '%Y-%m-%dT%H:%M:%S.%fZ']:
            try:
                expected_close_date = datetime.strptime(date_str[:23] if '.' in date_str else date_str, fmt).date()
                break
            except ValueError:
                continue
    
    actual_close_date = None
    if data.get('actual_close_date'):
        date_str = data['actual_close_date']
        for fmt in ['%Y-%m-%d', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%S.%f', '%Y-%m-%dT%H:%M:%S.%fZ']:
            try:
                actual_close_date = datetime.strptime(date_str[:23] if '.' in date_str else date_str, fmt).date()
                break
            except ValueError:
                continue
    
    try:
        new_deal = Deal(
            customer_id=data['customer_id'],
            amount=data['amount'],
            deal_status=data.get('deal_status', 'negotiating'),
            product=data.get('product'),
            expected_close_date=expected_close_date,
            actual_close_date=actual_close_date,
            created_by=1
        )
        db.session.add(new_deal)
        db.session.commit()
        return jsonify({'success': True, 'message': '交易记录添加成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'添加失败: {str(e)}'}), 500

@app.route('/api/deals/<int:id>', methods=['PUT'])
def update_deal(id):
    deal = Deal.query.get(id)
    if not deal:
        return jsonify({'success': False, 'message': '交易记录不存在'}), 404
    
    data = request.json
    
    # 如果更新客户ID，验证新客户是否存在
    if 'customer_id' in data:
        customer = Customer.query.get(data['customer_id'])
        if not customer:
            return jsonify({'success': False, 'message': '新客户不存在'}), 400
        deal.customer_id = data['customer_id']
    
    deal.amount = data.get('amount', deal.amount)
    deal.deal_status = data.get('deal_status', deal.deal_status)
    deal.product = data.get('product', deal.product)
    
    # 更新预计关闭日期
    if data.get('expected_close_date'):
        date_str = data['expected_close_date']
        for fmt in ['%Y-%m-%d', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%S.%f', '%Y-%m-%dT%H:%M:%S.%fZ']:
            try:
                deal.expected_close_date = datetime.strptime(date_str[:23] if '.' in date_str else date_str, fmt).date()
                break
            except ValueError:
                continue
    
    # 更新实际关闭日期
    if data.get('actual_close_date'):
        date_str = data['actual_close_date']
        for fmt in ['%Y-%m-%d', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%S.%f', '%Y-%m-%dT%H:%M:%S.%fZ']:
            try:
                deal.actual_close_date = datetime.strptime(date_str[:23] if '.' in date_str else date_str, fmt).date()
                break
            except ValueError:
                continue
    
    try:
        db.session.commit()
        return jsonify({'success': True, 'message': '交易记录更新成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'更新失败: {str(e)}'}), 500

@app.route('/api/deals/<int:id>', methods=['DELETE'])
def delete_deal(id):
    deal = Deal.query.get(id)
    if not deal:
        return jsonify({'success': False, 'message': '交易记录不存在'}), 404
    
    try:
        db.session.delete(deal)
        db.session.commit()
        return jsonify({'success': True, 'message': '交易记录删除成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'删除失败: {str(e)}'}), 500

# 统计模块 API

@app.route('/api/stats/customers', methods=['GET'])
def customer_stats():
    total = Customer.query.count()
    potential = Customer.query.filter_by(status='potential').count()
    active = Customer.query.filter_by(status='active').count()
    lost = Customer.query.filter_by(status='lost').count()
    
    return jsonify({
        'total': total,
        'potential': potential,
        'active': active,
        'lost': lost
    })

@app.route('/api/stats/deals', methods=['GET'])
def deal_stats():
    total_deals = Deal.query.count()
    total_amount = db.session.query(db.func.sum(Deal.amount)).scalar() or 0
    closed_deals = Deal.query.filter_by(deal_status='closed').count()
    closed_amount = db.session.query(db.func.sum(Deal.amount)).filter(Deal.deal_status == 'closed').scalar() or 0
    
    return jsonify({
        'total_deals': total_deals,
        'total_amount': total_amount,
        'closed_deals': closed_deals,
        'closed_amount': closed_amount
    })

# 用户管理 API

@app.route('/api/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([{
        'id': u.id,
        'username': u.username,
        'role': u.role,
        'created_at': u.created_at.isoformat()
    } for u in users])

@app.route('/api/users', methods=['POST'])
@token_required
@admin_required
def add_user(current_user):
    data = request.json
    username = data.get('username')
    password = data.get('password')
    role = data.get('role', 'user')
    
    # 检查用户名是否已存在
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({'success': False, 'message': '用户名已存在'}), 400
    
    # 使用密码哈希存储
    hashed_password = generate_password_hash(password)
    new_user = User(username=username, password=hashed_password, role=role)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'success': True, 'message': '用户添加成功', 'user': {'id': new_user.id}})

@app.route('/api/users/<int:id>', methods=['PUT'])
@token_required
@admin_required
def update_user(current_user, id):
    user = User.query.get(id)
    if not user:
        return jsonify({'success': False, 'message': '用户不存在'}), 404
    
    data = request.json
    user.username = data.get('username', user.username)
    user.role = data.get('role', user.role)
    if 'password' in data and data['password']:
        # 使用密码哈希存储
        user.password = generate_password_hash(data['password'])
    
    db.session.commit()
    return jsonify({'success': True, 'message': '用户信息更新成功'})

@app.route('/api/users/<int:id>', methods=['DELETE'])
@token_required
@admin_required
def delete_user(current_user, id):
    user = User.query.get(id)
    if not user:
        return jsonify({'success': False, 'message': '用户不存在'}), 404
    
    # 检查是否是当前登录用户（不能删除自己）
    if user.id == current_user.id:
        return jsonify({'success': False, 'message': '不能删除当前登录的用户'}), 400
    
    # 如果要删除的是管理员，检查是否至少还有一个管理员
    if user.role == 'admin':
        admin_count = User.query.filter_by(role='admin').count()
        if admin_count <= 1:
            return jsonify({'success': False, 'message': '系统中至少需要保留一个管理员'}), 400
    
    db.session.delete(user)
    db.session.commit()
    return jsonify({'success': True, 'message': '用户删除成功'}), 200

# 首页统计数据 API

@app.route('/api/stats', methods=['GET'])
def get_stats():
    # 计算总客户数
    total_customers = Customer.query.count()
    
    # 计算总交易数和交易总额（只计算已完成的交易）
    deals = Deal.query.all()
    total_deals = len(deals)
    total_amount = sum(deal.amount for deal in deals if deal.deal_status == 'closed')
    
    # 计算总跟进记录数
    total_follow_ups = FollowUp.query.count()
    
    # 计算环比数据（本月 vs 上月）
    from datetime import timedelta
    now = datetime.utcnow()
    current_month = now.strftime('%Y-%m')
    last_month = (now - timedelta(days=30)).strftime('%Y-%m')
    
    current_year, current_month_num = map(int, current_month.split('-'))
    last_year, last_month_num = map(int, last_month.split('-'))
    
    # 本月数据
    current_customers = Customer.query.filter(
        db.extract('year', Customer.created_at) == current_year,
        db.extract('month', Customer.created_at) == current_month_num
    ).count()
    
    current_deals = Deal.query.filter(
        db.extract('year', Deal.created_at) == current_year,
        db.extract('month', Deal.created_at) == current_month_num
    ).count()
    
    current_amount = sum(deal.amount for deal in Deal.query.filter(
        db.extract('year', Deal.created_at) == current_year,
        db.extract('month', Deal.created_at) == current_month_num,
        Deal.deal_status == 'closed'
    ).all())
    
    current_follow_ups = FollowUp.query.filter(
        db.extract('year', FollowUp.created_at) == current_year,
        db.extract('month', FollowUp.created_at) == current_month_num
    ).count()
    
    # 上月数据
    last_customers = Customer.query.filter(
        db.extract('year', Customer.created_at) == last_year,
        db.extract('month', Customer.created_at) == last_month_num
    ).count()
    
    last_deals = Deal.query.filter(
        db.extract('year', Deal.created_at) == last_year,
        db.extract('month', Deal.created_at) == last_month_num
    ).count()
    
    last_amount = sum(deal.amount for deal in Deal.query.filter(
        db.extract('year', Deal.created_at) == last_year,
        db.extract('month', Deal.created_at) == last_month_num,
        Deal.deal_status == 'closed'
    ).all())
    
    last_follow_ups = FollowUp.query.filter(
        db.extract('year', FollowUp.created_at) == last_year,
        db.extract('month', FollowUp.created_at) == last_month_num
    ).count()
    
    # 计算环比增长率
    def calculate_growth(current, last):
        if last == 0:
            return 100 if current > 0 else 0
        return round(((current - last) / last) * 100, 2)
    
    return jsonify({
        'total_customers': total_customers,
        'total_deals': total_deals,
        'total_amount': total_amount,
        'total_follow_ups': total_follow_ups,
        'customer_trend': calculate_growth(current_customers, last_customers),
        'deal_trend': calculate_growth(current_deals, last_deals),
        'amount_trend': calculate_growth(current_amount, last_amount),
        'follow_up_trend': calculate_growth(current_follow_ups, last_follow_ups)
    })

@app.route('/api/stats/recent-customers', methods=['GET'])
def get_recent_customers():
    # 获取最近5个客户
    customers = Customer.query.order_by(Customer.created_at.desc()).limit(5).all()
    return jsonify([{
        'id': c.id,
        'name': c.name,
        'company': c.company,
        'status': c.status,
        'created_at': c.created_at.isoformat()
    } for c in customers])

@app.route('/api/stats/recent-follow-ups', methods=['GET'])
def get_recent_follow_ups():
    # 获取最近5条跟进记录，包含客户名称
    follow_ups = FollowUp.query.order_by(FollowUp.created_at.desc()).limit(5).all()
    result = []
    for fu in follow_ups:
        customer = Customer.query.get(fu.customer_id)
        customer_name = customer.name if customer else '未知客户'
        result.append({
            'id': fu.id,
            'customer_id': fu.customer_id,
            'customer_name': customer_name,
            'content': fu.content,
            'follow_type': fu.follow_type,
            'created_at': fu.created_at.isoformat()
        })
    return jsonify(result)

# 月度统计分析 API

@app.route('/api/stats/monthly', methods=['GET'])
def get_monthly_stats():
    # 获取最近6个月的数据
    from datetime import timedelta
    months = []
    for i in range(6):
        month_date = datetime.utcnow() - timedelta(days=30 * i)
        month_str = month_date.strftime('%Y-%m')
        months.append(month_str)
    
    monthly_data = []
    for month in months:
        year, month_num = map(int, month.split('-'))
        
        # 计算该月新增客户数
        new_customers = Customer.query.filter(
            db.extract('year', Customer.created_at) == year,
            db.extract('month', Customer.created_at) == month_num
        ).count()
        
        # 计算该月新增交易数
        new_deals = Deal.query.filter(
            db.extract('year', Deal.created_at) == year,
            db.extract('month', Deal.created_at) == month_num
        ).count()
        
        # 计算该月完成交易金额
        month_deals = Deal.query.filter(
            db.extract('year', Deal.created_at) == year,
            db.extract('month', Deal.created_at) == month_num,
            Deal.deal_status == 'closed'
        ).all()
        closed_amount = sum(deal.amount for deal in month_deals)
        
        # 计算该月跟进记录数
        follow_ups = FollowUp.query.filter(
            db.extract('year', FollowUp.created_at) == year,
            db.extract('month', FollowUp.created_at) == month_num
        ).count()
        
        monthly_data.append({
            'month': month,
            'new_customers': new_customers,
            'new_deals': new_deals,
            'closed_amount': closed_amount,
            'follow_ups': follow_ups
        })
    
    # 按月份排序（从旧到新）
    monthly_data.reverse()
    
    return jsonify(monthly_data)

@app.route('/api/stats/comparison', methods=['GET'])
def get_comparison_stats():
    # 获取本月和上月的数据
    from datetime import timedelta
    now = datetime.utcnow()
    current_month = now.strftime('%Y-%m')
    last_month = (now - timedelta(days=30)).strftime('%Y-%m')
    
    current_year, current_month_num = map(int, current_month.split('-'))
    last_year, last_month_num = map(int, last_month.split('-'))
    
    # 本月数据
    current_customers = Customer.query.filter(
        db.extract('year', Customer.created_at) == current_year,
        db.extract('month', Customer.created_at) == current_month_num
    ).count()
    
    current_deals = Deal.query.filter(
        db.extract('year', Deal.created_at) == current_year,
        db.extract('month', Deal.created_at) == current_month_num
    ).count()
    
    current_month_deals = Deal.query.filter(
        db.extract('year', Deal.created_at) == current_year,
        db.extract('month', Deal.created_at) == current_month_num,
        Deal.deal_status == 'closed'
    ).all()
    current_amount = sum(deal.amount for deal in current_month_deals)
    
    current_follow_ups = FollowUp.query.filter(
        db.extract('year', FollowUp.created_at) == current_year,
        db.extract('month', FollowUp.created_at) == current_month_num
    ).count()
    
    # 上月数据
    last_customers = Customer.query.filter(
        db.extract('year', Customer.created_at) == last_year,
        db.extract('month', Customer.created_at) == last_month_num
    ).count()
    
    last_deals = Deal.query.filter(
        db.extract('year', Deal.created_at) == last_year,
        db.extract('month', Deal.created_at) == last_month_num
    ).count()
    
    last_month_deals = Deal.query.filter(
        db.extract('year', Deal.created_at) == last_year,
        db.extract('month', Deal.created_at) == last_month_num,
        Deal.deal_status == 'closed'
    ).all()
    last_amount = sum(deal.amount for deal in last_month_deals)
    
    last_follow_ups = FollowUp.query.filter(
        db.extract('year', FollowUp.created_at) == last_year,
        db.extract('month', FollowUp.created_at) == last_month_num
    ).count()
    
    # 计算环比增长率
    def calculate_growth(current, last):
        if last == 0:
            return 100 if current > 0 else 0
        return round(((current - last) / last) * 100, 2)
    
    return jsonify({
        'current_month': current_month,
        'last_month': last_month,
        'customers': {
            'current': current_customers,
            'last': last_customers,
            'growth': calculate_growth(current_customers, last_customers)
        },
        'deals': {
            'current': current_deals,
            'last': last_deals,
            'growth': calculate_growth(current_deals, last_deals)
        },
        'amount': {
            'current': current_amount,
            'last': last_amount,
            'growth': calculate_growth(current_amount, last_amount)
        },
        'follow_ups': {
            'current': current_follow_ups,
            'last': last_follow_ups,
            'growth': calculate_growth(current_follow_ups, last_follow_ups)
        }
    })

# 新的统计API端点

@app.route('/api/stats/kpi', methods=['GET'])
def get_kpi_stats():
    """获取KPI统计数据"""
    range_type = request.args.get('range', 'month')
    from datetime import timedelta
    
    now = datetime.utcnow()
    
    # 根据时间范围计算起始日期
    if range_type == 'custom':
        # 自定义时间范围
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            # 计算上一周期（相同天数）
            days_diff = (end_date - start_date).days
            prev_end_date = start_date
            prev_start_date = prev_end_date - timedelta(days=days_diff)
        else:
            start_date = now - timedelta(days=30)
            prev_start_date = now - timedelta(days=60)
    elif range_type == 'month':
        start_date = now - timedelta(days=30)
        prev_start_date = now - timedelta(days=60)
    elif range_type == 'quarter':
        start_date = now - timedelta(days=90)
        prev_start_date = now - timedelta(days=180)
    else:  # year
        start_date = now - timedelta(days=365)
        prev_start_date = now - timedelta(days=730)
    
    # 当前周期数据
    current_customers = Customer.query.filter(Customer.created_at >= start_date).count()
    current_deals = Deal.query.filter(Deal.created_at >= start_date).count()
    current_amount = sum(deal.amount for deal in Deal.query.filter(
        Deal.created_at >= start_date,
        Deal.deal_status == 'closed'
    ).all())
    
    # 上一周期数据
    prev_customers = Customer.query.filter(
        Customer.created_at >= prev_start_date,
        Customer.created_at < start_date
    ).count()
    prev_deals = Deal.query.filter(
        Deal.created_at >= prev_start_date,
        Deal.created_at < start_date
    ).count()
    prev_amount = sum(deal.amount for deal in Deal.query.filter(
        Deal.created_at >= prev_start_date,
        Deal.created_at < start_date,
        Deal.deal_status == 'closed'
    ).all())
    
    # 计算转化率
    total_deals_current = Deal.query.filter(Deal.created_at >= start_date).count()
    closed_deals_current = Deal.query.filter(
        Deal.created_at >= start_date,
        Deal.deal_status == 'closed'
    ).count()
    conversion_rate = round((closed_deals_current / total_deals_current * 100), 2) if total_deals_current > 0 else 0
    
    total_deals_prev = Deal.query.filter(
        Deal.created_at >= prev_start_date,
        Deal.created_at < start_date
    ).count()
    closed_deals_prev = Deal.query.filter(
        Deal.created_at >= prev_start_date,
        Deal.created_at < start_date,
        Deal.deal_status == 'closed'
    ).count()
    prev_conversion_rate = round((closed_deals_prev / total_deals_prev * 100), 2) if total_deals_prev > 0 else 0
    
    def calculate_growth(current, last):
        if last == 0:
            return 100 if current > 0 else 0
        return round(((current - last) / last) * 100, 2)
    
    return jsonify({
        'customers': current_customers,
        'deals': current_deals,
        'amount': current_amount,
        'conversionRate': conversion_rate,
        'customerTrend': calculate_growth(current_customers, prev_customers),
        'dealTrend': calculate_growth(current_deals, prev_deals),
        'amountTrend': calculate_growth(current_amount, prev_amount),
        'conversionTrend': calculate_growth(conversion_rate, prev_conversion_rate)
    })

@app.route('/api/stats/trend', methods=['GET'])
def get_trend_stats():
    """获取趋势统计数据"""
    range_type = request.args.get('range', 'month')
    from datetime import timedelta
    
    now = datetime.utcnow()
    data = []
    
    if range_type == 'custom':
        # 自定义时间范围
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            days_diff = (end_date - start_date).days
            
            # 根据天数选择统计粒度
            if days_diff <= 31:
                # 按天统计
                for i in range(days_diff + 1):
                    date = start_date + timedelta(days=i)
                    next_date = date + timedelta(days=1)
                    
                    new_customers = Customer.query.filter(
                        Customer.created_at >= date,
                        Customer.created_at < next_date
                    ).count()
                    
                    new_deals = Deal.query.filter(
                        Deal.created_at >= date,
                        Deal.created_at < next_date
                    ).count()
                    
                    closed_amount = sum(deal.amount for deal in Deal.query.filter(
                        Deal.created_at >= date,
                        Deal.created_at < next_date,
                        Deal.deal_status == 'closed'
                    ).all())
                    
                    follow_ups = FollowUp.query.filter(
                        FollowUp.created_at >= date,
                        FollowUp.created_at < next_date
                    ).count()
                    
                    conversion_rate = round((new_deals / new_customers * 100), 2) if new_customers > 0 else 0
                    
                    data.append({
                        'period': date.strftime('%m-%d'),
                        'newCustomers': new_customers,
                        'newDeals': new_deals,
                        'closedAmount': closed_amount,
                        'followUps': follow_ups,
                        'conversionRate': conversion_rate
                    })
            elif days_diff <= 180:
                # 按周统计
                weeks = (days_diff // 7) + 1
                for i in range(weeks):
                    week_start = start_date + timedelta(weeks=i)
                    week_end = min(week_start + timedelta(weeks=1), end_date + timedelta(days=1))
                    
                    new_customers = Customer.query.filter(
                        Customer.created_at >= week_start,
                        Customer.created_at < week_end
                    ).count()
                    
                    new_deals = Deal.query.filter(
                        Deal.created_at >= week_start,
                        Deal.created_at < week_end
                    ).count()
                    
                    closed_amount = sum(deal.amount for deal in Deal.query.filter(
                        Deal.created_at >= week_start,
                        Deal.created_at < week_end,
                        Deal.deal_status == 'closed'
                    ).all())
                    
                    follow_ups = FollowUp.query.filter(
                        FollowUp.created_at >= week_start,
                        FollowUp.created_at < week_end
                    ).count()
                    
                    conversion_rate = round((new_deals / new_customers * 100), 2) if new_customers > 0 else 0
                    
                    data.append({
                        'period': f'第{i+1}周',
                        'newCustomers': new_customers,
                        'newDeals': new_deals,
                        'closedAmount': closed_amount,
                        'followUps': follow_ups,
                        'conversionRate': conversion_rate
                    })
            else:
                # 按月统计
                current_date = start_date
                month_count = 0
                while current_date <= end_date:
                    year, month = current_date.year, current_date.month
                    
                    new_customers = Customer.query.filter(
                        db.extract('year', Customer.created_at) == year,
                        db.extract('month', Customer.created_at) == month
                    ).count()
                    
                    new_deals = Deal.query.filter(
                        db.extract('year', Deal.created_at) == year,
                        db.extract('month', Deal.created_at) == month
                    ).count()
                    
                    closed_amount = sum(deal.amount for deal in Deal.query.filter(
                        db.extract('year', Deal.created_at) == year,
                        db.extract('month', Deal.created_at) == month,
                        Deal.deal_status == 'closed'
                    ).all())
                    
                    follow_ups = FollowUp.query.filter(
                        db.extract('year', FollowUp.created_at) == year,
                        db.extract('month', FollowUp.created_at) == month
                    ).count()
                    
                    conversion_rate = round((new_deals / new_customers * 100), 2) if new_customers > 0 else 0
                    
                    data.append({
                        'period': current_date.strftime('%Y-%m'),
                        'newCustomers': new_customers,
                        'newDeals': new_deals,
                        'closedAmount': closed_amount,
                        'followUps': follow_ups,
                        'conversionRate': conversion_rate
                    })
                    
                    # 移动到下个月
                    if month == 12:
                        current_date = current_date.replace(year=year + 1, month=1)
                    else:
                        current_date = current_date.replace(month=month + 1)
                    month_count += 1
                    if month_count > 24:  # 最多24个月
                        break
        else:
            # 默认最近30天
            for i in range(29, -1, -1):
                date = now - timedelta(days=i)
                next_date = date + timedelta(days=1)
                
                new_customers = Customer.query.filter(
                    Customer.created_at >= date,
                    Customer.created_at < next_date
                ).count()
                
                new_deals = Deal.query.filter(
                    Deal.created_at >= date,
                    Deal.created_at < next_date
                ).count()
                
                closed_amount = sum(deal.amount for deal in Deal.query.filter(
                    Deal.created_at >= date,
                    Deal.created_at < next_date,
                    Deal.deal_status == 'closed'
                ).all())
                
                follow_ups = FollowUp.query.filter(
                    FollowUp.created_at >= date,
                    FollowUp.created_at < next_date
                ).count()
                
                conversion_rate = round((new_deals / new_customers * 100), 2) if new_customers > 0 else 0
                
                data.append({
                    'period': date.strftime('%m-%d'),
                    'newCustomers': new_customers,
                    'newDeals': new_deals,
                    'closedAmount': closed_amount,
                    'followUps': follow_ups,
                    'conversionRate': conversion_rate
                })
    
    elif range_type == 'month':
        # 本月数据，从本月第一天开始按天统计
        current_year = now.year
        current_month = now.month
        
        # 获取本月第一天和最后一天
        from calendar import monthrange
        _, last_day = monthrange(current_year, current_month)
        
        for day in range(1, last_day + 1):
            date = datetime(current_year, current_month, day)
            next_date = date + timedelta(days=1)
            
            # 如果日期超过今天，显示为0
            if date > now:
                data.append({
                    'period': f'{current_month:02d}-{day:02d}',
                    'newCustomers': 0,
                    'newDeals': 0,
                    'closedAmount': 0,
                    'followUps': 0,
                    'conversionRate': 0
                })
                continue
            
            new_customers = Customer.query.filter(
                Customer.created_at >= date,
                Customer.created_at < next_date
            ).count()
            
            new_deals = Deal.query.filter(
                Deal.created_at >= date,
                Deal.created_at < next_date
            ).count()
            
            closed_amount = sum(deal.amount for deal in Deal.query.filter(
                Deal.created_at >= date,
                Deal.created_at < next_date,
                Deal.deal_status == 'closed'
            ).all())
            
            follow_ups = FollowUp.query.filter(
                FollowUp.created_at >= date,
                FollowUp.created_at < next_date
            ).count()
            
            conversion_rate = round((new_deals / new_customers * 100), 2) if new_customers > 0 else 0
            
            data.append({
                'period': f'{current_month:02d}-{day:02d}',
                'newCustomers': new_customers,
                'newDeals': new_deals,
                'closedAmount': closed_amount,
                'followUps': follow_ups,
                'conversionRate': conversion_rate
            })
    
    elif range_type == 'quarter':
        # 本季度数据，从本季度第一个月开始按月统计
        current_year = now.year
        current_month = now.month
        
        # 计算本季度的月份 (1-3, 4-6, 7-9, 10-12)
        quarter_start_month = ((current_month - 1) // 3) * 3 + 1
        
        for month_offset in range(3):
            month = quarter_start_month + month_offset
            
            new_customers = Customer.query.filter(
                db.extract('year', Customer.created_at) == current_year,
                db.extract('month', Customer.created_at) == month
            ).count()
            
            new_deals = Deal.query.filter(
                db.extract('year', Deal.created_at) == current_year,
                db.extract('month', Deal.created_at) == month
            ).count()
            
            closed_amount = sum(deal.amount for deal in Deal.query.filter(
                db.extract('year', Deal.created_at) == current_year,
                db.extract('month', Deal.created_at) == month,
                Deal.deal_status == 'closed'
            ).all())
            
            follow_ups = FollowUp.query.filter(
                db.extract('year', FollowUp.created_at) == current_year,
                db.extract('month', FollowUp.created_at) == month
            ).count()
            
            conversion_rate = round((new_deals / new_customers * 100), 2) if new_customers > 0 else 0
            
            data.append({
                'period': f'{current_year}-{month:02d}',
                'newCustomers': new_customers,
                'newDeals': new_deals,
                'closedAmount': closed_amount,
                'followUps': follow_ups,
                'conversionRate': conversion_rate
            })
    
    else:  # year
        # 本年数据，从本年第一个月开始按月统计
        current_year = now.year
        current_month = now.month
        
        for month in range(1, current_month + 1):
            new_customers = Customer.query.filter(
                db.extract('year', Customer.created_at) == current_year,
                db.extract('month', Customer.created_at) == month
            ).count()
            
            new_deals = Deal.query.filter(
                db.extract('year', Deal.created_at) == current_year,
                db.extract('month', Deal.created_at) == month
            ).count()
            
            closed_amount = sum(deal.amount for deal in Deal.query.filter(
                db.extract('year', Deal.created_at) == current_year,
                db.extract('month', Deal.created_at) == month,
                Deal.deal_status == 'closed'
            ).all())
            
            follow_ups = FollowUp.query.filter(
                db.extract('year', FollowUp.created_at) == current_year,
                db.extract('month', FollowUp.created_at) == month
            ).count()
            
            conversion_rate = round((new_deals / new_customers * 100), 2) if new_customers > 0 else 0
            
            data.append({
                'period': f'{current_year}-{month:02d}',
                'newCustomers': new_customers,
                'newDeals': new_deals,
                'closedAmount': closed_amount,
                'followUps': follow_ups,
                'conversionRate': conversion_rate
            })
    
    return jsonify(data)

@app.route('/api/stats/status', methods=['GET'])
def get_status_stats():
    """获取状态分布统计"""
    # 客户状态分布
    potential = Customer.query.filter_by(status='potential').count()
    active = Customer.query.filter_by(status='active').count()
    lost = Customer.query.filter_by(status='lost').count()
    
    # 交易状态分布
    negotiating = Deal.query.filter_by(deal_status='negotiating').count()
    closed = Deal.query.filter_by(deal_status='closed').count()
    failed = Deal.query.filter_by(deal_status='failed').count()
    
    return jsonify({
        'customers': {
            'potential': potential,
            'active': active,
            'lost': lost
        },
        'deals': {
            'negotiating': negotiating,
            'closed': closed,
            'failed': failed
        }
    })

@app.route('/api/stats/industry', methods=['GET'])
def get_industry_stats():
    """获取行业分布统计"""
    from sqlalchemy import func
    
    # 按行业分组统计客户数
    industry_stats = db.session.query(
        Customer.industry,
        func.count(Customer.id)
    ).filter(Customer.industry != None).group_by(Customer.industry).all()
    
    result = {}
    for industry, count in industry_stats:
        result[industry] = count
    
    return jsonify(result)

@app.route('/api/stats/monthly-summary', methods=['GET'])
def get_monthly_summary():
    """获取月度汇总数据（用于详细数据报表）- 显示本年数据"""
    from datetime import timedelta
    from sqlalchemy import func
    
    now = datetime.utcnow()
    current_year = now.year
    current_month = now.month
    monthly_data = []
    
    # 获取本年1月到当前月的数据
    for month in range(1, current_month + 1):
        month_str = f'{current_year}-{month:02d}'
        
        # 计算该月新增客户数
        new_customers = Customer.query.filter(
            db.extract('year', Customer.created_at) == current_year,
            db.extract('month', Customer.created_at) == month
        ).count()
        
        # 计算该月新增交易数和完成交易金额
        new_deals = Deal.query.filter(
            db.extract('year', Deal.created_at) == current_year,
            db.extract('month', Deal.created_at) == month
        ).count()
        
        month_deals = Deal.query.filter(
            db.extract('year', Deal.created_at) == current_year,
            db.extract('month', Deal.created_at) == month,
            Deal.deal_status == 'closed'
        ).all()
        closed_amount = sum(deal.amount for deal in month_deals)
        
        # 计算该月跟进记录数
        follow_ups = FollowUp.query.filter(
            db.extract('year', FollowUp.created_at) == current_year,
            db.extract('month', FollowUp.created_at) == month
        ).count()
        
        # 计算转化率
        conversion_rate = round((new_deals / new_customers * 100), 2) if new_customers > 0 else 0
        
        monthly_data.append({
            'month': month_str,
            'newCustomers': new_customers,
            'newDeals': new_deals,
            'closedAmount': closed_amount,
            'followUps': follow_ups,
            'conversionRate': conversion_rate
        })
    
    return jsonify(monthly_data)

# 数据库导入功能
import pandas as pd
from werkzeug.utils import secure_filename
import io

ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/import/customers', methods=['POST'])
def import_customers():
    """导入客户数据"""
    if 'file' not in request.files:
        return jsonify({'error': '没有上传文件'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': '不支持的文件格式，请上传 Excel 或 CSV 文件'}), 400
    
    try:
        # 读取文件
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)
        
        # 检查必要的列
        required_columns = ['name']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return jsonify({'error': f'缺少必要的列: {", ".join(missing_columns)}'}), 400
        
        # 导入数据
        success_count = 0
        error_count = 0
        errors = []
        
        for index, row in df.iterrows():
            try:
                # 检查客户是否已存在（根据姓名和电话）
                existing = Customer.query.filter_by(
                    name=str(row.get('name', '')).strip(),
                    phone=str(row.get('phone', '')).strip() if pd.notna(row.get('phone')) else None
                ).first()
                
                if existing:
                    error_count += 1
                    errors.append(f'第 {index + 2} 行: 客户 "{row.get("name")}" 已存在')
                    continue
                
                # 创建新客户
                customer = Customer(
                    name=str(row.get('name', '')).strip(),
                    phone=str(row.get('phone', '')).strip() if pd.notna(row.get('phone')) else None,
                    email=str(row.get('email', '')).strip() if pd.notna(row.get('email')) else None,
                    company=str(row.get('company', '')).strip() if pd.notna(row.get('company')) else None,
                    industry=str(row.get('industry', '')).strip() if pd.notna(row.get('industry')) else None,
                    status=str(row.get('status', 'potential')).strip() if pd.notna(row.get('status')) else 'potential',
                    created_by=request.form.get('user_id', 1)
                )
                db.session.add(customer)
                success_count += 1
            except Exception as e:
                error_count += 1
                errors.append(f'第 {index + 2} 行: {str(e)}')
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'导入完成: 成功 {success_count} 条，失败 {error_count} 条',
            'success_count': success_count,
            'error_count': error_count,
            'errors': errors[:10]  # 只返回前10个错误
        })
        
    except Exception as e:
        return jsonify({'error': f'导入失败: {str(e)}'}), 500

@app.route('/api/import/deals', methods=['POST'])
def import_deals():
    """导入交易数据"""
    if 'file' not in request.files:
        return jsonify({'error': '没有上传文件'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': '不支持的文件格式，请上传 Excel 或 CSV 文件'}), 400
    
    try:
        # 读取文件
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)
        
        # 检查必要的列
        required_columns = ['customer_id', 'amount']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return jsonify({'error': f'缺少必要的列: {", ".join(missing_columns)}'}), 400
        
        # 导入数据
        success_count = 0
        error_count = 0
        errors = []
        
        for index, row in df.iterrows():
            try:
                # 检查客户是否存在
                customer_id = int(row.get('customer_id'))
                customer = Customer.query.get(customer_id)
                if not customer:
                    error_count += 1
                    errors.append(f'第 {index + 2} 行: 客户 ID {customer_id} 不存在')
                    continue
                
                # 创建新交易
                deal = Deal(
                    customer_id=customer_id,
                    amount=float(row.get('amount', 0)),
                    product=str(row.get('product', '')).strip() if pd.notna(row.get('product')) else None,
                    deal_status=str(row.get('deal_status', 'negotiating')).strip() if pd.notna(row.get('deal_status')) else 'negotiating',
                    expected_close_date=pd.to_datetime(row.get('expected_close_date')).date() if pd.notna(row.get('expected_close_date')) else None,
                    created_by=request.form.get('user_id', 1)
                )
                db.session.add(deal)
                success_count += 1
            except Exception as e:
                error_count += 1
                errors.append(f'第 {index + 2} 行: {str(e)}')
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'导入完成: 成功 {success_count} 条，失败 {error_count} 条',
            'success_count': success_count,
            'error_count': error_count,
            'errors': errors[:10]
        })
        
    except Exception as e:
        return jsonify({'error': f'导入失败: {str(e)}'}), 500

# 待办事项 API
@app.route('/api/todos', methods=['GET'])
def get_todos():
    """获取当前用户的待办事项列表"""
    user_id = request.args.get('user_id', type=int)
    if not user_id:
        return jsonify({'error': '缺少用户ID参数'}), 400
    
    try:
        todos = Todo.query.filter_by(user_id=user_id).order_by(Todo.created_at.desc()).all()
        return jsonify([{
            'id': todo.id,
            'content': todo.content,
            'priority': todo.priority,
            'completed': todo.completed,
            'created_at': todo.created_at.isoformat() if todo.created_at else None,
            'updated_at': todo.updated_at.isoformat() if todo.updated_at else None
        } for todo in todos])
    except Exception as e:
        return jsonify({'error': f'获取待办事项失败: {str(e)}'}), 500

@app.route('/api/todos', methods=['POST'])
def create_todo():
    """创建新的待办事项"""
    data = request.json
    
    if not data.get('content'):
        return jsonify({'error': '待办事项内容不能为空'}), 400
    
    if not data.get('user_id'):
        return jsonify({'error': '用户ID不能为空'}), 400
    
    try:
        new_todo = Todo(
            user_id=data['user_id'],
            content=data['content'],
            priority=data.get('priority', 'medium'),
            completed=data.get('completed', False)
        )
        db.session.add(new_todo)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '待办事项创建成功',
            'todo': {
                'id': new_todo.id,
                'content': new_todo.content,
                'priority': new_todo.priority,
                'completed': new_todo.completed,
                'created_at': new_todo.created_at.isoformat() if new_todo.created_at else None
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'创建待办事项失败: {str(e)}'}), 500

@app.route('/api/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    """更新待办事项"""
    todo = Todo.query.get(todo_id)
    if not todo:
        return jsonify({'error': '待办事项不存在'}), 404
    
    data = request.json
    
    try:
        if 'content' in data:
            todo.content = data['content']
        if 'priority' in data:
            todo.priority = data['priority']
        if 'completed' in data:
            todo.completed = data['completed']
        
        todo.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '待办事项更新成功',
            'todo': {
                'id': todo.id,
                'content': todo.content,
                'priority': todo.priority,
                'completed': todo.completed,
                'updated_at': todo.updated_at.isoformat() if todo.updated_at else None
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'更新待办事项失败: {str(e)}'}), 500

@app.route('/api/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    """删除待办事项"""
    todo = Todo.query.get(todo_id)
    if not todo:
        return jsonify({'error': '待办事项不存在'}), 404
    
    try:
        db.session.delete(todo)
        db.session.commit()
        return jsonify({'success': True, 'message': '待办事项删除成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'删除待办事项失败: {str(e)}'}), 500

@app.route('/api/import/template/<data_type>', methods=['GET'])
def download_template(data_type):
    """下载导入模板"""
    try:
        if data_type == 'customers':
            # 创建客户导入模板
            df = pd.DataFrame({
                'name': ['张三', '李四'],
                'phone': ['13800138000', '13900139000'],
                'email': ['zhangsan@example.com', 'lisi@example.com'],
                'company': ['ABC公司', 'XYZ公司'],
                'industry': ['IT', '金融'],
                'status': ['potential', 'active']
            })
            filename = '客户导入模板.xlsx'
        elif data_type == 'deals':
            # 创建交易导入模板
            df = pd.DataFrame({
                'customer_id': [1, 2],
                'amount': [10000.00, 20000.00],
                'product': ['产品A', '产品B'],
                'deal_status': ['negotiating', 'closed'],
                'expected_close_date': ['2024-12-31', '2024-12-31']
            })
            filename = '交易导入模板.xlsx'
        else:
            return jsonify({'error': '未知的模板类型'}), 400
        
        # 将 DataFrame 转换为字节流
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Sheet1')
        output.seek(0)
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        return jsonify({'error': f'下载模板失败: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)