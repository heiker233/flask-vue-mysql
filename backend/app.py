from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
import os

app = Flask(__name__)
# 配置 CORS 以允许所有来源（解决同一热点下手机无法登录问题）
CORS(app, resources={r"/*": {"origins": "*"}})

# 数据库配置
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:daige520@localhost/customer_management'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

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
        admin = User(username='admin', password='admin', role='admin')
        db.session.add(admin)
        db.session.commit()
        print('管理员用户已创建: admin / admin')

# 用户认证
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    user = User.query.filter_by(username=username, password=password).first()
    if user:
        return jsonify({'success': True, 'user': {'id': user.id, 'username': user.username, 'role': user.role}})
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
        new_user = User(username=username, password=password, role='user')
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'success': True, 'message': '注册成功', 'user': {'id': new_user.id, 'username': new_user.username, 'role': new_user.role}})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': '注册失败: {}'.format(str(e))}), 500

# 客户模块 API

@app.route('/api/customers', methods=['GET'])
def get_customers():
    customers = Customer.query.all()
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
    follow_ups = FollowUp.query.all()
    return jsonify([{
        'id': fu.id,
        'customer_id': fu.customer_id,
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
    deals = Deal.query.all()
    return jsonify([{
        'id': d.id,
        'customer_id': d.customer_id,
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
def add_user():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    role = data.get('role', 'user')
    
    # 检查用户名是否已存在
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({'success': False, 'message': '用户名已存在'}), 400
    
    new_user = User(username=username, password=password, role=role)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'success': True, 'message': '用户添加成功', 'user': {'id': new_user.id}})

@app.route('/api/users/<int:id>', methods=['PUT'])
def update_user(id):
    user = User.query.get(id)
    if not user:
        return jsonify({'success': False, 'message': '用户不存在'}), 404
    
    data = request.json
    user.username = data.get('username', user.username)
    user.role = data.get('role', user.role)
    if 'password' in data and data['password']:
        user.password = data['password']
    
    db.session.commit()
    return jsonify({'success': True, 'message': '用户信息更新成功'})

@app.route('/api/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    user = User.query.get(id)
    if not user:
        return jsonify({'success': False, 'message': '用户不存在'}), 404
    
    db.session.delete(user)
    db.session.commit()
    return jsonify({'success': True, 'message': '用户删除成功'}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)