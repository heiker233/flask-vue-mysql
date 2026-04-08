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
    customers = db.relationship('Customer', foreign_keys='Customer.created_by', backref='user', lazy=True)
    assigned_customers = db.relationship('Customer', foreign_keys='Customer.assigned_to', backref='assignee', lazy=True)
    follow_ups = db.relationship('FollowUp', backref='user', lazy=True)
    created_deals = db.relationship('Deal', foreign_keys='Deal.created_by', backref='creator', lazy=True)
    todos = db.relationship('Todo', backref='user', lazy=True)

# 待办事项表
class Todo(db.Model):
    __tablename__ = 'todos'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.String(200), nullable=False)
    priority = db.Column(db.String(20), default='medium')  # high, medium, low
    completed = db.Column(db.Boolean, default=False)
    due_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# 客户标签关联表
class CustomerTag(db.Model):
    __tablename__ = 'customer_tags'
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    tag_name = db.Column(db.String(50), nullable=False)
    tag_type = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

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
    value_score = db.Column(db.Integer, default=3)
    cooperation_stage = db.Column(db.String(20), default='initial')
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    follow_ups = db.relationship('FollowUp', backref='customer', lazy=True)
    deals = db.relationship('Deal', backref='customer', lazy=True)
    tags = db.relationship('CustomerTag', backref='customer', lazy=True, cascade='all, delete-orphan')

# 跟进记录表
class FollowUp(db.Model):
    __tablename__ = 'follow_ups'
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    deal_id = db.Column(db.Integer, db.ForeignKey('deals.id'))
    content = db.Column(db.Text, nullable=False)
    follow_type = db.Column(db.String(50))
    next_follow_date = db.Column(db.Date)
    is_conversion = db.Column(db.Boolean, default=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# 产品库表
class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))
    price = db.Column(db.Float, default=0)
    description = db.Column(db.Text)
    unit = db.Column(db.String(20), default='件')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# 交易表
class Deal(db.Model):
    __tablename__ = 'deals'
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=True)
    product_name = db.Column(db.String(100))
    quantity = db.Column(db.Integer, default=1)
    unit_price = db.Column(db.Float, default=0)
    amount = db.Column(db.Float, nullable=False)
    deal_status = db.Column(db.String(20), default='negotiating')
    payment_status = db.Column(db.String(20), default='unpaid')
    paid_amount = db.Column(db.Float, default=0)
    approval_status = db.Column(db.String(20), default='pending')
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    approved_at = db.Column(db.DateTime, nullable=True)
    expected_close_date = db.Column(db.Date)
    actual_close_date = db.Column(db.Date)
    notes = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    follow_ups = db.relationship('FollowUp', backref='deal', lazy=True)
    product = db.relationship('Product', backref='deals')
    approver = db.relationship('User', foreign_keys=[approved_by], backref='approved_deals')

# 交易审批记录表
class DealApproval(db.Model):
    __tablename__ = 'deal_approvals'
    id = db.Column(db.Integer, primary_key=True)
    deal_id = db.Column(db.Integer, db.ForeignKey('deals.id'), nullable=False)
    approver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(20), nullable=False)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    deal = db.relationship('Deal', backref='approval_records')
    approver = db.relationship('User', backref='approval_actions')

# 消息表
class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    msg_type = db.Column(db.String(50), default='info')
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

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
    query = Customer.query
    
    keyword = request.args.get('keyword', '').strip()
    if keyword:
        query = query.filter(
            db.or_(
                Customer.name.ilike(f'%{keyword}%'),
                Customer.phone.ilike(f'%{keyword}%'),
                Customer.email.ilike(f'%{keyword}%'),
                Customer.company.ilike(f'%{keyword}%')
            )
        )
    
    industry = request.args.get('industry', '').strip()
    if industry:
        query = query.filter(Customer.industry == industry)
    
    status = request.args.get('status', '').strip()
    if status:
        query = query.filter(Customer.status == status)
    
    cooperation_stage = request.args.get('cooperation_stage', '').strip()
    if cooperation_stage:
        query = query.filter(Customer.cooperation_stage == cooperation_stage)
    
    assigned_to = request.args.get('assigned_to', type=int)
    if assigned_to:
        query = query.filter(Customer.assigned_to == assigned_to)
    
    value_score_min = request.args.get('value_score_min', type=int)
    if value_score_min is not None:
        query = query.filter(Customer.value_score >= value_score_min)
    
    value_score_max = request.args.get('value_score_max', type=int)
    if value_score_max is not None:
        query = query.filter(Customer.value_score <= value_score_max)
    
    phone_prefix = request.args.get('phone_prefix', '').strip()
    if phone_prefix:
        query = query.filter(Customer.phone.ilike(f'{phone_prefix}%'))
    
    start_date = request.args.get('start_date', '').strip()
    if start_date:
        try:
            start_dt = datetime.fromisoformat(start_date)
            query = query.filter(Customer.created_at >= start_dt)
        except ValueError:
            pass
    
    end_date = request.args.get('end_date', '').strip()
    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date)
            query = query.filter(Customer.created_at <= end_dt)
        except ValueError:
            pass
    
    sort_by = request.args.get('sort_by', 'created_at').strip()
    sort_order = request.args.get('sort_order', 'desc').strip().lower()
    
    sort_column = getattr(Customer, sort_by, Customer.created_at)
    if sort_order == 'asc':
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())
    
    customers = query.all()
    result = []
    for c in customers:
        tags = [{'id': t.id, 'name': t.tag_name, 'type': t.tag_type} for t in c.tags]
        
        latest_follow_up = FollowUp.query.filter_by(customer_id=c.id).order_by(FollowUp.created_at.desc()).first()
        next_follow_date = None
        if latest_follow_up and latest_follow_up.next_follow_date:
            next_follow_date = latest_follow_up.next_follow_date.isoformat()
        
        assignee = None
        if c.assignee:
            assignee = {
                'id': c.assignee.id,
                'username': c.assignee.username
            }
        
        result.append({
            'id': c.id,
            'name': c.name,
            'phone': c.phone,
            'email': c.email,
            'company': c.company,
            'industry': c.industry,
            'status': c.status,
            'value_score': c.value_score,
            'cooperation_stage': c.cooperation_stage,
            'assigned_to': c.assigned_to,
            'assignee': assignee,
            'tags': tags,
            'next_follow_date': next_follow_date,
            'created_at': c.created_at.isoformat()
        })
    return jsonify(result)

@app.route('/api/customers/<int:id>/assign', methods=['PUT'])
def assign_customer(id):
    customer = Customer.query.get(id)
    if not customer:
        return jsonify({'success': False, 'message': '客户不存在'}), 404
    
    data = request.json
    customer.assigned_to = data.get('assigned_to')
    db.session.commit()
    return jsonify({'success': True, 'message': '客户分配成功'})

@app.route('/api/customers', methods=['POST'])
def add_customer():
    data = request.json
    
    # 客户查重
    phone = data.get('phone', '').strip() if data.get('phone') else None
    email = data.get('email', '').strip() if data.get('email') else None
    
    duplicate_check = None
    if phone:
        duplicate_check = Customer.query.filter(Customer.phone == phone).first()
    if not duplicate_check and email:
        duplicate_check = Customer.query.filter(Customer.email == email).first()
    
    if duplicate_check:
        return jsonify({
            'success': False,
            'message': f'客户已存在：{duplicate_check.name}',
            'duplicate': {
                'id': duplicate_check.id,
                'name': duplicate_check.name,
                'phone': duplicate_check.phone,
                'email': duplicate_check.email
            }
        }), 409
    
    new_customer = Customer(
        name=data['name'],
        phone=phone,
        email=email,
        company=data.get('company'),
        industry=data.get('industry'),
        status=data.get('status', 'potential'),
        value_score=data.get('value_score', 3),
        cooperation_stage=data.get('cooperation_stage', 'initial'),
        assigned_to=data.get('assigned_to'),
        created_by=1
    )
    db.session.add(new_customer)
    db.session.flush()
    
    # 添加客户标签
    if 'tags' in data and data['tags']:
        for tag in data['tags']:
            new_tag = CustomerTag(
                customer_id=new_customer.id,
                tag_name=tag['name'] if isinstance(tag, dict) else tag,
                tag_type=tag.get('type', 'custom') if isinstance(tag, dict) else 'custom'
            )
            db.session.add(new_tag)
    
    db.session.commit()
    
    # 返回完整的客户数据
    return jsonify({
        'success': True, 
        'message': '客户添加成功', 
        'customer': {
            'id': new_customer.id,
            'name': new_customer.name,
            'phone': new_customer.phone,
            'email': new_customer.email,
            'company': new_customer.company,
            'industry': new_customer.industry,
            'status': new_customer.status,
            'value_score': new_customer.value_score,
            'cooperation_stage': new_customer.cooperation_stage,
            'assigned_to': new_customer.assigned_to,
            'created_at': new_customer.created_at.isoformat() if new_customer.created_at else None,
            'updated_at': new_customer.updated_at.isoformat() if new_customer.updated_at else None,
            'assignee': {'username': new_customer.assignee.username} if new_customer.assignee else None
        }
    })

@app.route('/api/customers/<int:id>', methods=['PUT'])
def update_customer(id):
    customer = Customer.query.get(id)
    if not customer:
        return jsonify({'success': False, 'message': '客户不存在'}), 404
    
    data = request.json
    
    # 客户查重
    phone = data.get('phone', customer.phone)
    email = data.get('email', customer.email)
    
    if phone:
        duplicate = Customer.query.filter(
            Customer.phone == phone,
            Customer.id != id
        ).first()
        if duplicate:
            return jsonify({
                'success': False,
                'message': f'电话号码已被其他客户使用：{duplicate.name}'
            }), 409
    
    if email:
        duplicate = Customer.query.filter(
            Customer.email == email,
            Customer.id != id
        ).first()
        if duplicate:
            return jsonify({
                'success': False,
                'message': f'邮箱已被其他客户使用：{duplicate.name}'
            }), 409
    
    customer.name = data.get('name', customer.name)
    customer.phone = phone
    customer.email = email
    customer.company = data.get('company', customer.company)
    customer.industry = data.get('industry', customer.industry)
    customer.status = data.get('status', customer.status)
    customer.value_score = data.get('value_score', customer.value_score)
    customer.cooperation_stage = data.get('cooperation_stage', customer.cooperation_stage)
    if 'assigned_to' in data:
        customer.assigned_to = data['assigned_to']
    
    # 更新客户标签
    if 'tags' in data:
        CustomerTag.query.filter_by(customer_id=id).delete()
        for tag in data['tags']:
            new_tag = CustomerTag(
                customer_id=id,
                tag_name=tag['name'] if isinstance(tag, dict) else tag,
                tag_type=tag.get('type', 'custom') if isinstance(tag, dict) else 'custom'
            )
            db.session.add(new_tag)
    
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
    deal_id = request.args.get('deal_id', type=int)
    if deal_id:
        follow_ups = FollowUp.query.filter_by(deal_id=deal_id).order_by(FollowUp.created_at.desc()).all()
    else:
        follow_ups = FollowUp.query.order_by(FollowUp.created_at.desc()).all()
    return jsonify([{
        'id': fu.id,
        'customer_id': fu.customer_id,
        'customer_name': fu.customer.name if fu.customer else None,
        'deal_id': fu.deal_id,
        'content': fu.content,
        'follow_type': fu.follow_type,
        'next_follow_date': fu.next_follow_date.isoformat() if fu.next_follow_date else None,
        'is_conversion': fu.is_conversion,
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
            deal_id=data.get('deal_id'),
            content=data['content'],
            follow_type=data.get('follow_type'),
            next_follow_date=next_follow_date,
            is_conversion=data.get('is_conversion', False),
            created_by=1
        )
        db.session.add(new_follow_up)
        
        # 如果标记为促成交易转化且有关联交易，可考虑更新交易状态（此处仅建立关联，具体可扩展）
        if data.get('is_conversion') and data.get('deal_id'):
            deal = Deal.query.get(data['deal_id'])
            if deal and deal.deal_status != 'closed':
                deal.deal_status = 'closed'
                # 增加客户价值评分
                customer.value_score = min(5, customer.value_score + 1)
                # 发送通知
                msg = Message(
                    user_id=1,
                    title="交易状态变更",
                    content=f"客户 {customer.name} 的交易已完成，评分+10",
                    msg_type="deal"
                )
                db.session.add(msg)
                
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
    
    if 'deal_id' in data:
        follow_up.deal_id = data['deal_id']
    if 'is_conversion' in data:
        follow_up.is_conversion = data['is_conversion']
        
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
        'product_id': d.product_id,
        'product_name': d.product_name,
        'quantity': d.quantity,
        'unit_price': d.unit_price,
        'amount': d.amount,
        'deal_status': d.deal_status,
        'payment_status': d.payment_status,
        'paid_amount': d.paid_amount,
        'approval_status': d.approval_status,
        'approved_by': d.approved_by,
        'approver_name': d.approver.username if d.approver else None,
        'approved_at': d.approved_at.isoformat() if d.approved_at else None,
        'expected_close_date': d.expected_close_date.isoformat() if d.expected_close_date else None,
        'actual_close_date': d.actual_close_date.isoformat() if d.actual_close_date else None,
        'notes': d.notes,
        'created_at': d.created_at.isoformat()
    } for d in deals])

@app.route('/api/deals', methods=['POST'])
def add_deal():
    data = request.json
    
    if 'customer_id' not in data or 'amount' not in data:
        return jsonify({'success': False, 'message': '缺少必要字段'}), 400
    
    customer = Customer.query.get(data['customer_id'])
    if not customer:
        return jsonify({'success': False, 'message': '客户不存在'}), 400
    
    expected_close_date = None
    if data.get('expected_close_date'):
        date_str = data['expected_close_date']
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
    
    amount = float(data['amount'])
    approval_status = 'pending'
    if amount < 100000:
        approval_status = 'approved'
    
    try:
        new_deal = Deal(
            customer_id=data['customer_id'],
            product_id=data.get('product_id'),
            product_name=data.get('product_name'),
            quantity=data.get('quantity', 1),
            unit_price=data.get('unit_price', 0),
            amount=amount,
            deal_status=data.get('deal_status', 'negotiating'),
            payment_status=data.get('payment_status', 'unpaid'),
            paid_amount=data.get('paid_amount', 0),
            approval_status=approval_status,
            expected_close_date=expected_close_date,
            actual_close_date=actual_close_date,
            notes=data.get('notes'),
            created_by=1
        )
        db.session.add(new_deal)
        db.session.commit()
        return jsonify({'success': True, 'message': '交易记录添加成功', 'approval_required': amount >= 100000})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'添加失败: {str(e)}'}), 500

@app.route('/api/deals/<int:id>', methods=['PUT'])
def update_deal(id):
    deal = Deal.query.get(id)
    if not deal:
        return jsonify({'success': False, 'message': '交易记录不存在'}), 404
    
    data = request.json
    
    if 'customer_id' in data:
        customer = Customer.query.get(data['customer_id'])
        if not customer:
            return jsonify({'success': False, 'message': '新客户不存在'}), 400
        deal.customer_id = data['customer_id']
    
    deal.product_id = data.get('product_id', deal.product_id)
    deal.product_name = data.get('product_name', deal.product_name)
    deal.quantity = data.get('quantity', deal.quantity)
    deal.unit_price = data.get('unit_price', deal.unit_price)
    deal.amount = data.get('amount', deal.amount)
    deal.payment_status = data.get('payment_status', deal.payment_status)
    deal.paid_amount = data.get('paid_amount', deal.paid_amount)
    deal.notes = data.get('notes', deal.notes)
    
    old_status = deal.deal_status
    new_status = data.get('deal_status', deal.deal_status)
    if old_status != new_status:
        deal.deal_status = new_status
        customer = Customer.query.get(deal.customer_id)
        if new_status == 'closed':
            customer.value_score = min(5, customer.value_score + 1)
            msg_content = f"客户 {customer.name} 的交易已完成，价值评分+1"
        elif new_status == 'cancelled':
            customer.value_score = max(1, customer.value_score - 1)
            msg_content = f"客户 {customer.name} 的交易已取消，价值评分-1"
        else:
            msg_content = f"客户 {customer.name} 的交易状态变更为：{new_status}"
            
        msg = Message(
            user_id=1,
            title="交易状态变更通知",
            content=msg_content,
            msg_type="deal"
        )
        db.session.add(msg)
    
    if data.get('expected_close_date'):
        date_str = data['expected_close_date']
        for fmt in ['%Y-%m-%d', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%S.%f', '%Y-%m-%dT%H:%M:%S.%fZ']:
            try:
                deal.expected_close_date = datetime.strptime(date_str[:23] if '.' in date_str else date_str, fmt).date()
                break
            except ValueError:
                continue
    
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
        # 先删除关联的审批记录
        DealApproval.query.filter_by(deal_id=id).delete()
        # 删除关联的跟进记录
        FollowUp.query.filter_by(deal_id=id).delete()
        # 最后删除交易记录
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

@app.route('/api/import/preview', methods=['POST'])
def import_preview():
    """导入数据预览"""
    if 'file' not in request.files:
        return jsonify({'error': '没有上传文件'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400
        
    try:
        import pandas as pd
        import io
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)
            
        # 填充NaN为None以支持JSON序列化
        df = df.where(pd.notnull(df), None)
        
        # 取前5行作为预览
        preview_data = df.head(5).to_dict(orient='records')
        columns = list(df.columns)
        
        return jsonify({
            'success': True,
            'columns': columns,
            'preview_data': preview_data,
            'total_rows': len(df)
        })
    except Exception as e:
        return jsonify({'error': f'读取文件失败: {str(e)}'}), 500

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
            'due_date': todo.due_date.isoformat() if todo.due_date else None,
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
    
    due_date = None
    if data.get('due_date'):
        date_str = data['due_date']
        for fmt in ['%Y-%m-%d', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%S.%f', '%Y-%m-%dT%H:%M:%S.%fZ']:
            try:
                due_date = datetime.strptime(date_str[:23] if '.' in date_str else date_str, fmt)
                break
            except ValueError:
                continue
                
    try:
        new_todo = Todo(
            user_id=data['user_id'],
            content=data['content'],
            priority=data.get('priority', 'medium'),
            due_date=due_date
        )
        db.session.add(new_todo)
        
        # 预警：如果有到期日且在24小时内，发送消息
        if due_date and (due_date - datetime.utcnow()).total_seconds() < 86400:
            msg = Message(
                user_id=data['user_id'],
                title="待办事项即将到期",
                content=f"待办事项 '{data['content']}' 即将于 {due_date.strftime('%Y-%m-%d %H:%M')} 到期",
                msg_type="todo"
            )
            db.session.add(msg)
            
        db.session.commit()
        return jsonify({'success': True, 'message': '待办事项创建成功', 'todo_id': new_todo.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'创建待办事项失败: {str(e)}'}), 500

@app.route('/api/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    """更新待办事项状态"""
    data = request.json
    
    try:
        todo = Todo.query.get(todo_id)
        if not todo:
            return jsonify({'error': '待办事项不存在'}), 404
            
        if 'completed' in data:
            todo.completed = data['completed']
        if 'content' in data:
            todo.content = data['content']
        if 'priority' in data:
            todo.priority = data['priority']
        if 'due_date' in data:
            date_str = data['due_date']
            if date_str:
                for fmt in ['%Y-%m-%d', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%S.%f', '%Y-%m-%dT%H:%M:%S.%fZ']:
                    try:
                        todo.due_date = datetime.strptime(date_str[:23] if '.' in date_str else date_str, fmt)
                        break
                    except ValueError:
                        continue
            else:
                todo.due_date = None
                
        db.session.commit()
        return jsonify({'success': True, 'message': '待办事项更新成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'更新待办事项失败: {str(e)}'}), 500

# 消息中心 API
@app.route('/api/messages', methods=['GET'])
def get_messages():
    """获取当前用户的消息列表"""
    user_id = request.args.get('user_id', type=int)
    if not user_id:
        return jsonify({'error': '缺少用户ID参数'}), 400
    
    try:
        messages = Message.query.filter_by(user_id=user_id).order_by(Message.created_at.desc()).all()
        return jsonify([{
            'id': msg.id,
            'title': msg.title,
            'content': msg.content,
            'msg_type': msg.msg_type,
            'is_read': msg.is_read,
            'created_at': msg.created_at.isoformat()
        } for msg in messages])
    except Exception as e:
        return jsonify({'error': f'获取消息失败: {str(e)}'}), 500

@app.route('/api/messages/<int:id>/read', methods=['PUT'])
def read_message(id):
    """标记消息为已读"""
    try:
        msg = Message.query.get(id)
        if msg:
            msg.is_read = True
            db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/messages/read_all', methods=['PUT'])
def read_all_messages():
    """标记所有消息为已读"""
    user_id = request.json.get('user_id')
    try:
        Message.query.filter_by(user_id=user_id, is_read=False).update({'is_read': True})
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

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


# 待办事项同步 API - 将未完成的跟进和交易同步到待办事项
@app.route('/api/todos/sync', methods=['POST'])
def sync_todos():
    """同步未完成的跟进和交易到待办事项"""
    data = request.json
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({'error': '缺少用户ID参数'}), 400
    
    try:
        created_count = 0
        today = datetime.utcnow().date()
        
        # 1. 获取需要跟进的客户（下次跟进时间已到期或即将到期）
        customers = Customer.query.filter(
            (Customer.assigned_to == user_id) | (Customer.created_by == user_id)
        ).all()
        
        for customer in customers:
            latest_follow_up = FollowUp.query.filter_by(customer_id=customer.id).order_by(FollowUp.created_at.desc()).first()
            
            if latest_follow_up and latest_follow_up.next_follow_date:
                next_date = latest_follow_up.next_follow_date
                # 如果下次跟进时间在未来3天内或已逾期
                if next_date <= today + timedelta(days=3):
                    is_overdue = next_date < today
                    days_diff = (next_date - today).days
                    
                    if is_overdue:
                        content = f"【逾期跟进】客户 {customer.name} 的跟进已逾期 {abs(days_diff)} 天"
                        priority = 'high'
                    elif days_diff == 0:
                        content = f"【今日跟进】客户 {customer.name} 需要今天跟进"
                        priority = 'high'
                    else:
                        content = f"【即将跟进】客户 {customer.name} 将在 {days_diff} 天后需要跟进"
                        priority = 'medium'
                    
                    # 检查是否已存在相同的待办事项
                    existing_todo = Todo.query.filter_by(
                        user_id=user_id,
                        content=content
                    ).first()
                    
                    if not existing_todo:
                        new_todo = Todo(
                            user_id=user_id,
                            content=content,
                            priority=priority,
                            completed=False
                        )
                        db.session.add(new_todo)
                        created_count += 1
        
        # 2. 获取即将到期或逾期的交易
        deals = Deal.query.filter(
            ((Deal.created_by == user_id) | (Customer.assigned_to == user_id)) &
            (Deal.deal_status.in_(['negotiating', 'proposal']))
        ).join(Customer).all()
        
        for deal in deals:
            if deal.expected_close_date:
                close_date = deal.expected_close_date
                days_to_close = (close_date - today).days
                
                # 如果预计成交日期在未来7天内或已逾期
                if days_to_close <= 7:
                    if days_to_close < 0:
                        content = f"【逾期交易】客户 {deal.customer.name} 的交易已逾期 {abs(days_to_close)} 天，金额 ¥{deal.amount:,.2f}"
                        priority = 'high'
                    elif days_to_close == 0:
                        content = f"【今日成交】客户 {deal.customer.name} 的交易预计今日成交，金额 ¥{deal.amount:,.2f}"
                        priority = 'high'
                    elif days_to_close <= 3:
                        content = f"【即将成交】客户 {deal.customer.name} 的交易将在 {days_to_close} 天后到期，金额 ¥{deal.amount:,.2f}"
                        priority = 'high'
                    else:
                        content = f"【交易提醒】客户 {deal.customer.name} 的交易将在 {days_to_close} 天后到期，金额 ¥{deal.amount:,.2f}"
                        priority = 'medium'
                    
                    # 检查是否已存在相同的待办事项
                    existing_todo = Todo.query.filter_by(
                        user_id=user_id,
                        content=content
                    ).first()
                    
                    if not existing_todo:
                        new_todo = Todo(
                            user_id=user_id,
                            content=content,
                            priority=priority,
                            completed=False
                        )
                        db.session.add(new_todo)
                        created_count += 1
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'同步完成，新增 {created_count} 条待办事项',
            'created_count': created_count
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'同步待办事项失败: {str(e)}'}), 500


# 获取用户的待办事项统计
@app.route('/api/todos/stats', methods=['GET'])
def get_todo_stats():
    """获取用户的待办事项统计"""
    user_id = request.args.get('user_id', type=int)
    
    if not user_id:
        return jsonify({'error': '缺少用户ID参数'}), 400
    
    try:
        total = Todo.query.filter_by(user_id=user_id).count()
        unfinished = Todo.query.filter_by(user_id=user_id, completed=False).count()
        high_priority = Todo.query.filter_by(user_id=user_id, completed=False, priority='high').count()
        
        return jsonify({
            'success': True,
            'total': total,
            'unfinished': unfinished,
            'high_priority': high_priority
        })
    except Exception as e:
        return jsonify({'error': f'获取待办统计失败: {str(e)}'}), 500


# 产品库 API
@app.route('/api/products', methods=['GET'])
def get_products():
    products = Product.query.filter_by(is_active=True).order_by(Product.created_at.desc()).all()
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'category': p.category,
        'price': p.price,
        'description': p.description,
        'unit': p.unit,
        'created_at': p.created_at.isoformat()
    } for p in products])

@app.route('/api/products', methods=['POST'])
def add_product():
    data = request.json
    if not data.get('name'):
        return jsonify({'success': False, 'message': '产品名称不能为空'}), 400
    
    try:
        new_product = Product(
            name=data['name'],
            category=data.get('category'),
            price=data.get('price', 0),
            description=data.get('description'),
            unit=data.get('unit', '件')
        )
        db.session.add(new_product)
        db.session.commit()
        return jsonify({'success': True, 'message': '产品添加成功', 'id': new_product.id})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'添加失败: {str(e)}'}), 500

@app.route('/api/products/<int:id>', methods=['PUT'])
def update_product(id):
    product = Product.query.get(id)
    if not product:
        return jsonify({'success': False, 'message': '产品不存在'}), 404
    
    data = request.json
    product.name = data.get('name', product.name)
    product.category = data.get('category', product.category)
    product.price = data.get('price', product.price)
    product.description = data.get('description', product.description)
    product.unit = data.get('unit', product.unit)
    
    try:
        db.session.commit()
        return jsonify({'success': True, 'message': '产品更新成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'更新失败: {str(e)}'}), 500

@app.route('/api/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    product = Product.query.get(id)
    if not product:
        return jsonify({'success': False, 'message': '产品不存在'}), 404
    
    product.is_active = False
    try:
        db.session.commit()
        return jsonify({'success': True, 'message': '产品已禁用'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'删除失败: {str(e)}'}), 500


# 交易审批 API
@app.route('/api/deals/<int:id>/approve', methods=['POST'])
def approve_deal(id):
    deal = Deal.query.get(id)
    if not deal:
        return jsonify({'success': False, 'message': '交易不存在'}), 404
    
    data = request.json
    action = data.get('action')
    comment = data.get('comment', '')
    approver_id = data.get('approver_id', 1)
    
    if action not in ['approve', 'reject']:
        return jsonify({'success': False, 'message': '无效的操作'}), 400
    
    if deal.approval_status != 'pending':
        return jsonify({'success': False, 'message': '该交易已审批'}), 400
    
    try:
        if action == 'approve':
            deal.approval_status = 'approved'
            deal.approved_by = approver_id
            deal.approved_at = datetime.utcnow()
        else:
            deal.approval_status = 'rejected'
            deal.approved_by = approver_id
            deal.approved_at = datetime.utcnow()
        
        approval_record = DealApproval(
            deal_id=id,
            approver_id=approver_id,
            action=action,
            comment=comment
        )
        db.session.add(approval_record)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'交易已{"批准" if action == "approve" else "拒绝"}'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'审批失败: {str(e)}'}), 500

@app.route('/api/deals/pending-approval', methods=['GET'])
def get_pending_deals():
    deals = Deal.query.filter_by(approval_status='pending').order_by(Deal.created_at.desc()).all()
    return jsonify([{
        'id': d.id,
        'customer_name': d.customer.name if d.customer else None,
        'product_name': d.product_name,
        'amount': d.amount,
        'created_at': d.created_at.isoformat(),
        'created_by': d.created_by
    } for d in deals])


# =============================================================================
# 高级统计分析 API - 销售漏斗、客户价值、销售人员业绩
# =============================================================================

@app.route('/api/stats/sales-funnel', methods=['GET'])
def get_sales_funnel():
    """销售漏斗分析 - 潜在客户→意向客户→成交客户的转化率"""
    range_type = request.args.get('range', 'month')
    
    now = datetime.utcnow()
    if range_type == 'month':
        start_date = datetime(now.year, now.month, 1)
    elif range_type == 'year':
        start_date = datetime(now.year, 1, 1)
    elif range_type == 'quarter':
        quarter_start = ((now.month - 1) // 3) * 3 + 1
        start_date = datetime(now.year, quarter_start, 1)
    else:
        start_date = datetime(2000, 1, 1)
    
    try:
        # 1. 潜在客户数（所有客户）
        total_customers = Customer.query.filter(Customer.created_at >= start_date).count()
        
        # 2. 有意向客户数（有跟进记录的客户）
        customers_with_followup = db.session.query(FollowUp.customer_id).distinct().filter(
            FollowUp.created_at >= start_date
        ).count()
        
        # 3. 有交易客户数（创建过交易的客户）
        customers_with_deals = db.session.query(Deal.customer_id).distinct().filter(
            Deal.created_at >= start_date
        ).count()
        
        # 4. 成交客户数（交易状态为closed的客户）
        closed_customers = db.session.query(Deal.customer_id).distinct().filter(
            Deal.created_at >= start_date,
            Deal.deal_status == 'closed'
        ).count()
        
        # 计算转化率
        def calc_rate(numerator, denominator):
            return round((numerator / denominator * 100), 2) if denominator > 0 else 0
        
        funnel_data = {
            'stages': [
                {
                    'name': '潜在客户',
                    'count': total_customers,
                    'conversion_rate': 100.0,
                    'description': '系统中所有客户'
                },
                {
                    'name': '已跟进客户',
                    'count': customers_with_followup,
                    'conversion_rate': calc_rate(customers_with_followup, total_customers),
                    'description': '有过跟进记录的客户'
                },
                {
                    'name': '有交易客户',
                    'count': customers_with_deals,
                    'conversion_rate': calc_rate(customers_with_deals, customers_with_followup) if customers_with_followup > 0 else 0,
                    'description': '创建过交易的客户'
                },
                {
                    'name': '成交客户',
                    'count': closed_customers,
                    'conversion_rate': calc_rate(closed_customers, customers_with_deals) if customers_with_deals > 0 else 0,
                    'description': '交易已完成的客户'
                }
            ],
            'summary': {
                'total_conversion_rate': calc_rate(closed_customers, total_customers),
                'total_customers': total_customers,
                'closed_customers': closed_customers
            }
        }
        
        return jsonify(funnel_data)
    except Exception as e:
        return jsonify({'error': f'获取销售漏斗数据失败: {str(e)}'}), 500


@app.route('/api/stats/customer-value', methods=['GET'])
def get_customer_value_analysis():
    """客户价值分析 - 按交易金额/频次划分高/中/低价值客户"""
    range_type = request.args.get('range', 'month')
    
    now = datetime.utcnow()
    if range_type == 'month':
        start_date = datetime(now.year, now.month, 1)
    elif range_type == 'year':
        start_date = datetime(now.year, 1, 1)
    elif range_type == 'quarter':
        quarter_start = ((now.month - 1) // 3) * 3 + 1
        start_date = datetime(now.year, quarter_start, 1)
    else:
        start_date = datetime(2000, 1, 1)
    
    try:
        # 获取每个客户的交易统计
        customer_stats = db.session.query(
            Customer.id,
            Customer.name,
            db.func.count(Deal.id).label('deal_count'),
            db.func.sum(Deal.amount).label('total_amount'),
            db.func.avg(Deal.amount).label('avg_amount')
        ).outerjoin(Deal, Customer.id == Deal.customer_id).filter(
            Deal.created_at >= start_date
        ).group_by(Customer.id).all()
        
        # 计算分位数用于划分价值等级
        amounts = [s.total_amount or 0 for s in customer_stats]
        counts = [s.deal_count for s in customer_stats]
        
        def get_percentile(data, percentile):
            if not data:
                return 0
            sorted_data = sorted(data)
            index = int(len(sorted_data) * percentile / 100)
            return sorted_data[min(index, len(sorted_data) - 1)]
        
        # 使用金额和频次双重标准划分
        amount_high = get_percentile(amounts, 80) if amounts else 0
        amount_low = get_percentile(amounts, 40) if amounts else 0
        count_high = get_percentile(counts, 80) if counts else 0
        count_low = get_percentile(counts, 40) if counts else 0
        
        high_value = []
        medium_value = []
        low_value = []
        
        for stat in customer_stats:
            total_amount = stat.total_amount or 0
            deal_count = stat.deal_count
            
            # 价值评分：金额占60%，频次占40%
            amount_score = 60 if total_amount >= amount_high else (30 if total_amount >= amount_low else 0)
            count_score = 40 if deal_count >= count_high else (20 if deal_count >= count_low else 0)
            total_score = amount_score + count_score
            
            customer_data = {
                'id': stat.id,
                'name': stat.name,
                'total_amount': round(total_amount, 2),
                'deal_count': deal_count,
                'avg_amount': round(stat.avg_amount or 0, 2),
                'score': total_score
            }
            
            if total_score >= 70:
                high_value.append(customer_data)
            elif total_score >= 30:
                medium_value.append(customer_data)
            else:
                low_value.append(customer_data)
        
        # 按金额排序
        high_value.sort(key=lambda x: x['total_amount'], reverse=True)
        medium_value.sort(key=lambda x: x['total_amount'], reverse=True)
        low_value.sort(key=lambda x: x['total_amount'], reverse=True)
        
        return jsonify({
            'distribution': {
                'high': {
                    'count': len(high_value),
                    'percentage': round(len(high_value) / len(customer_stats) * 100, 2) if customer_stats else 0,
                    'total_amount': round(sum(c['total_amount'] for c in high_value), 2),
                    'customers': high_value[:10]  # 只返回前10个
                },
                'medium': {
                    'count': len(medium_value),
                    'percentage': round(len(medium_value) / len(customer_stats) * 100, 2) if customer_stats else 0,
                    'total_amount': round(sum(c['total_amount'] for c in medium_value), 2),
                    'customers': medium_value[:10]
                },
                'low': {
                    'count': len(low_value),
                    'percentage': round(len(low_value) / len(customer_stats) * 100, 2) if customer_stats else 0,
                    'total_amount': round(sum(c['total_amount'] for c in low_value), 2),
                    'customers': low_value[:10]
                }
            },
            'thresholds': {
                'amount_high': amount_high,
                'amount_low': amount_low,
                'count_high': count_high,
                'count_low': count_low
            }
        })
    except Exception as e:
        return jsonify({'error': f'获取客户价值分析失败: {str(e)}'}), 500


@app.route('/api/stats/sales-performance', methods=['GET'])
def get_sales_performance():
    """销售人员业绩统计 - 按人/按部门统计成交金额"""
    range_type = request.args.get('range', 'month')
    
    now = datetime.utcnow()
    if range_type == 'month':
        start_date = datetime(now.year, now.month, 1)
    elif range_type == 'year':
        start_date = datetime(now.year, 1, 1)
    elif range_type == 'quarter':
        quarter_start = ((now.month - 1) // 3) * 3 + 1
        start_date = datetime(now.year, quarter_start, 1)
    else:
        start_date = datetime(2000, 1, 1)
    
    try:
        # 1. 按销售人员统计
        sales_by_person = db.session.query(
            User.id,
            User.username,
            db.func.count(Deal.id).label('deal_count'),
            db.func.sum(Deal.amount).label('total_amount'),
            db.func.sum(db.case((Deal.deal_status == 'closed', Deal.amount), else_=0)).label('closed_amount')
        ).outerjoin(Deal, User.id == Deal.created_by).filter(
            Deal.created_at >= start_date
        ).group_by(User.id).all()
        
        person_performance = []
        for person in sales_by_person:
            total = person.total_amount or 0
            closed = person.closed_amount or 0
            person_performance.append({
                'id': person.id,
                'name': person.username,
                'deal_count': person.deal_count,
                'total_amount': round(total, 2),
                'closed_amount': round(closed, 2),
                'conversion_rate': round(closed / total * 100, 2) if total > 0 else 0
            })
        
        # 按成交金额排序
        person_performance.sort(key=lambda x: x['total_amount'], reverse=True)
        
        # 2. 按部门/行业统计（使用客户行业作为部门维度）
        sales_by_industry = db.session.query(
            Customer.industry,
            db.func.count(Deal.id).label('deal_count'),
            db.func.sum(Deal.amount).label('total_amount'),
            db.func.sum(db.case((Deal.deal_status == 'closed', Deal.amount), else_=0)).label('closed_amount')
        ).join(Deal, Customer.id == Deal.customer_id).filter(
            Deal.created_at >= start_date
        ).group_by(Customer.industry).all()
        
        industry_performance = []
        for ind in sales_by_industry:
            if ind.industry:  # 跳过空行业
                total = ind.total_amount or 0
                closed = ind.closed_amount or 0
                industry_performance.append({
                    'industry': ind.industry,
                    'deal_count': ind.deal_count,
                    'total_amount': round(total, 2),
                    'closed_amount': round(closed, 2),
                    'conversion_rate': round(closed / total * 100, 2) if total > 0 else 0
                })
        
        industry_performance.sort(key=lambda x: x['total_amount'], reverse=True)
        
        # 3. 计算总体统计
        total_amount = sum(p['total_amount'] for p in person_performance)
        total_closed = sum(p['closed_amount'] for p in person_performance)
        total_deals = sum(p['deal_count'] for p in person_performance)
        
        return jsonify({
            'by_person': person_performance,
            'by_industry': industry_performance,
            'summary': {
                'total_sales': len(person_performance),
                'total_deals': total_deals,
                'total_amount': round(total_amount, 2),
                'total_closed': round(total_closed, 2),
                'overall_conversion_rate': round(total_closed / total_amount * 100, 2) if total_amount > 0 else 0,
                'avg_per_person': round(total_amount / len(person_performance), 2) if person_performance else 0
            },
            'ranking': {
                'top_performer': person_performance[0] if person_performance else None,
                'top_industry': industry_performance[0] if industry_performance else None
            }
        })
    except Exception as e:
        return jsonify({'error': f'获取销售业绩统计失败: {str(e)}'}), 500


# =============================================================================
# 数据导出 API - 支持 CSV/Excel/JSON 格式，字段自定义
# =============================================================================

import csv
import io
from flask import send_file

def format_value(value, date_format='%Y-%m-%d %H:%M:%S'):
    """格式化字段值"""
    if value is None:
        return ''
    if isinstance(value, datetime):
        return value.strftime(date_format)
    if isinstance(value, bool):
        return '是' if value else '否'
    return str(value)

def get_customer_status_text(status):
    """获取客户状态文本"""
    status_map = {
        'potential': '潜在客户',
        'active': '活跃客户',
        'lost': '已流失客户'
    }
    return status_map.get(status, status)

def get_deal_status_text(status):
    """获取交易状态文本"""
    status_map = {
        'negotiating': '谈判中',
        'proposal': '方案制定',
        'closed': '已完成',
        'cancelled': '已取消'
    }
    return status_map.get(status, status)

def get_payment_status_text(status):
    """获取付款状态文本"""
    status_map = {
        'unpaid': '未付款',
        'partial': '部分付款',
        'paid': '已付款'
    }
    return status_map.get(status, status)

def get_approval_status_text(status):
    """获取审批状态文本"""
    status_map = {
        'pending': '待审批',
        'approved': '已批准',
        'rejected': '已拒绝'
    }
    return status_map.get(status, status)

@app.route('/api/export', methods=['POST'])
def export_data():
    """通用数据导出接口 - 支持 CSV/Excel/JSON"""
    data = request.json
    
    data_type = data.get('data_type')
    export_format = data.get('format', 'csv')
    export_range = data.get('range', 'all')
    fields = data.get('fields', [])
    filters = data.get('filters', {})
    selected_ids = data.get('selected_ids', [])
    filename = data.get('filename', f'export_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
    encoding = data.get('encoding', 'utf-8')
    include_header = data.get('include_header', True)
    date_format = data.get('date_format', '%Y-%m-%d %H:%M:%S')
    
    if not data_type:
        return jsonify({'error': '缺少数据类型参数'}), 400
    
    if not fields:
        return jsonify({'error': '缺少导出字段参数'}), 400
    
    try:
        # 根据数据类型查询数据
        query = None
        if data_type == 'customers':
            query = Customer.query
            # 应用筛选条件
            if filters.get('keyword'):
                keyword = f"%{filters['keyword']}%"
                query = query.filter(
                    db.or_(
                        Customer.name.ilike(keyword),
                        Customer.phone.ilike(keyword),
                        Customer.company.ilike(keyword)
                    )
                )
            if filters.get('status'):
                query = query.filter(Customer.status == filters['status'])
            if filters.get('industry'):
                query = query.filter(Customer.industry == filters['industry'])
            if filters.get('cooperation_stage'):
                query = query.filter(Customer.cooperation_stage == filters['cooperation_stage'])
            if filters.get('assigned_to'):
                query = query.filter(Customer.assigned_to == filters['assigned_to'])
            if filters.get('start_date') and filters.get('end_date'):
                start = datetime.strptime(filters['start_date'], '%Y-%m-%d')
                end = datetime.strptime(filters['end_date'], '%Y-%m-%d')
                end = end.replace(hour=23, minute=59, second=59)
                query = query.filter(Customer.created_at >= start, Customer.created_at <= end)
                
        elif data_type == 'deals':
            query = Deal.query
            if filters.get('keyword'):
                keyword = f"%{filters['keyword']}%"
                query = query.join(Customer).filter(
                    db.or_(
                        Customer.name.ilike(keyword),
                        Deal.product_name.ilike(keyword)
                    )
                )
            if filters.get('status'):
                query = query.filter(Deal.deal_status == filters['status'])
            if filters.get('start_date') and filters.get('end_date'):
                start = datetime.strptime(filters['start_date'], '%Y-%m-%d')
                end = datetime.strptime(filters['end_date'], '%Y-%m-%d')
                end = end.replace(hour=23, minute=59, second=59)
                query = query.filter(Deal.created_at >= start, Deal.created_at <= end)
                
        elif data_type == 'follow-ups':
            query = FollowUp.query
            if filters.get('keyword'):
                keyword = f"%{filters['keyword']}%"
                query = query.join(Customer).filter(
                    db.or_(
                        Customer.name.ilike(keyword),
                        FollowUp.content.ilike(keyword)
                    )
                )
            if filters.get('follow_type'):
                query = query.filter(FollowUp.follow_type == filters['follow_type'])
            if filters.get('start_date') and filters.get('end_date'):
                start = datetime.strptime(filters['start_date'], '%Y-%m-%d')
                end = datetime.strptime(filters['end_date'], '%Y-%m-%d')
                end = end.replace(hour=23, minute=59, second=59)
                query = query.filter(FollowUp.created_at >= start, FollowUp.created_at <= end)
        else:
            return jsonify({'error': '不支持的数据类型'}), 400
        
        # 应用选中ID筛选
        if export_range == 'selected' and selected_ids:
            query = query.filter(getattr(query.column_descriptions[0]['type'], 'id').in_(selected_ids))
        
        # 获取数据
        records = query.all()
        
        # 字段映射配置
        field_configs = {
            'customers': {
                'id': ('客户ID', lambda c: c.id),
                'name': ('客户姓名', lambda c: c.name),
                'phone': ('联系电话', lambda c: c.phone or ''),
                'email': ('电子邮箱', lambda c: c.email or ''),
                'company': ('公司名称', lambda c: c.company or ''),
                'industry': ('所属行业', lambda c: c.industry or ''),
                'status': ('客户状态', lambda c: get_customer_status_text(c.status)),
                'value_score': ('价值评分', lambda c: c.value_score),
                'cooperation_stage': ('合作阶段', lambda c: c.cooperation_stage or ''),
                'assigned_to': ('负责人ID', lambda c: c.assigned_to or ''),
                'assignee_name': ('负责人姓名', lambda c: c.assignee.username if c.assignee else ''),
                'created_at': ('创建时间', lambda c: format_value(c.created_at, date_format)),
                'updated_at': ('更新时间', lambda c: format_value(c.updated_at, date_format)),
                'notes': ('备注信息', lambda c: c.notes or '')
            },
            'deals': {
                'id': ('交易ID', lambda d: d.id),
                'customer_id': ('客户ID', lambda d: d.customer_id),
                'customer_name': ('客户姓名', lambda d: d.customer.name if d.customer else ''),
                'product_id': ('产品ID', lambda d: d.product_id or ''),
                'product_name': ('产品名称', lambda d: d.product_name or ''),
                'quantity': ('数量', lambda d: d.quantity),
                'unit_price': ('单价', lambda d: d.unit_price),
                'amount': ('交易金额', lambda d: d.amount),
                'deal_status': ('交易状态', lambda d: get_deal_status_text(d.deal_status)),
                'payment_status': ('付款状态', lambda d: get_payment_status_text(d.payment_status)),
                'paid_amount': ('已付金额', lambda d: d.paid_amount),
                'approval_status': ('审批状态', lambda d: get_approval_status_text(d.approval_status)),
                'expected_close_date': ('预期完成日期', lambda d: format_value(d.expected_close_date, '%Y-%m-%d') if d.expected_close_date else ''),
                'actual_close_date': ('实际完成日期', lambda d: format_value(d.actual_close_date, '%Y-%m-%d') if d.actual_close_date else ''),
                'notes': ('备注', lambda d: d.notes or ''),
                'created_at': ('创建时间', lambda d: format_value(d.created_at, date_format)),
                'updated_at': ('更新时间', lambda d: format_value(d.updated_at, date_format))
            },
            'follow-ups': {
                'id': ('记录ID', lambda f: f.id),
                'customer_id': ('客户ID', lambda f: f.customer_id),
                'customer_name': ('客户姓名', lambda f: f.customer.name if f.customer else ''),
                'deal_id': ('交易ID', lambda f: f.deal_id or ''),
                'content': ('跟进内容', lambda f: f.content),
                'follow_type': ('跟进方式', lambda f: f.follow_type or ''),
                'next_follow_date': ('下次跟进日期', lambda f: format_value(f.next_follow_date, '%Y-%m-%d') if f.next_follow_date else ''),
                'is_conversion': ('是否促成交易', lambda f: '是' if f.is_conversion else '否'),
                'created_by': ('创建人ID', lambda f: f.created_by or ''),
                'creator_name': ('创建人姓名', lambda f: f.user.username if f.user else ''),
                'created_at': ('创建时间', lambda f: format_value(f.created_at, date_format))
            }
        }
        
        config = field_configs.get(data_type, {})
        
        # 生成数据
        export_data_list = []
        for record in records:
            row = {}
            for field in fields:
                if field in config:
                    header, getter = config[field]
                    try:
                        row[header] = getter(record)
                    except Exception:
                        row[header] = ''
            export_data_list.append(row)
        
        # 根据格式生成文件
        if export_format == 'csv':
            output = io.StringIO()
            if encoding == 'utf-8':
                output.write('\ufeff')  # UTF-8 BOM
            
            if export_data_list:
                headers = list(export_data_list[0].keys())
                writer = csv.DictWriter(output, fieldnames=headers)
                if include_header:
                    writer.writeheader()
                writer.writerows(export_data_list)
            
            output.seek(0)
            
            if encoding == 'gbk':
                content = output.getvalue().encode('gbk', errors='ignore')
            else:
                content = output.getvalue().encode('utf-8')
            
            return send_file(
                io.BytesIO(content),
                mimetype='text/csv;charset=' + encoding,
                as_attachment=True,
                download_name=f'{filename}.csv'
            )
            
        elif export_format == 'excel':
            try:
                import pandas as pd
                df = pd.DataFrame(export_data_list)
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='数据')
                output.seek(0)
                return send_file(
                    output,
                    mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    as_attachment=True,
                    download_name=f'{filename}.xlsx'
                )
            except ImportError:
                # 如果没有pandas，回退到CSV
                return jsonify({'error': 'Excel导出需要安装pandas和openpyxl'}), 500
                
        elif export_format == 'json':
            output = io.BytesIO()
            json_content = json.dumps({
                'export_info': {
                    'data_type': data_type,
                    'export_time': datetime.now().isoformat(),
                    'record_count': len(export_data_list),
                    'fields': fields
                },
                'data': export_data_list
            }, ensure_ascii=False, indent=2)
            output.write(json_content.encode('utf-8'))
            output.seek(0)
            return send_file(
                output,
                mimetype='application/json',
                as_attachment=True,
                download_name=f'{filename}.json'
            )
        else:
            return jsonify({'error': '不支持的导出格式'}), 400
            
    except Exception as e:
        return jsonify({'error': f'导出失败: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)