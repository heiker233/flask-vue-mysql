from datetime import datetime
from extensions import db

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
    priority = db.Column(db.String(20), default='medium')
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
