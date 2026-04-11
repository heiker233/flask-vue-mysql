"""
客户管理路由模块
处理客户的增删改查、分配等功能
"""
from flask import Blueprint, request, jsonify
from extensions import db
from models import Customer, CustomerTag, FollowUp, Deal
from datetime import datetime

customers_bp = Blueprint('customers', __name__)


@customers_bp.route('/customers', methods=['GET'])
def get_customers():
    """获取客户列表"""
    query = Customer.query
    
    # 关键词搜索
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
    
    # 行业筛选
    industry = request.args.get('industry', '').strip()
    if industry:
        query = query.filter(Customer.industry == industry)
    
    # 状态筛选
    status = request.args.get('status', '').strip()
    if status:
        query = query.filter(Customer.status == status)
    
    # 合作阶段筛选
    cooperation_stage = request.args.get('cooperation_stage', '').strip()
    if cooperation_stage:
        query = query.filter(Customer.cooperation_stage == cooperation_stage)
    
    # 负责人筛选
    assigned_to = request.args.get('assigned_to', type=int)
    if assigned_to:
        query = query.filter(Customer.assigned_to == assigned_to)
    
    # 价值评分范围
    value_score_min = request.args.get('value_score_min', type=int)
    if value_score_min is not None:
        query = query.filter(Customer.value_score >= value_score_min)
    
    value_score_max = request.args.get('value_score_max', type=int)
    if value_score_max is not None:
        query = query.filter(Customer.value_score <= value_score_max)
    
    # 电话前缀筛选
    phone_prefix = request.args.get('phone_prefix', '').strip()
    if phone_prefix:
        query = query.filter(Customer.phone.ilike(f'{phone_prefix}%'))
    
    # 日期范围筛选
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
    
    # 排序
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
        # 获取标签
        tags = [{'id': t.id, 'name': t.tag_name, 'type': t.tag_type} for t in c.tags]
        
        # 获取最新跟进记录
        latest_follow_up = FollowUp.query.filter_by(customer_id=c.id).order_by(FollowUp.created_at.desc()).first()
        next_follow_date = None
        if latest_follow_up and latest_follow_up.next_follow_date:
            next_follow_date = latest_follow_up.next_follow_date.isoformat()
        
        # 获取负责人信息
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
            'created_at': c.created_at.isoformat() if c.created_at else None,
            'updated_at': c.updated_at.isoformat() if c.updated_at else None
        })
    
    return jsonify(result)


@customers_bp.route('/customers', methods=['POST'])
def add_customer():
    """添加客户"""
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
    
    try:
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
            created_by=1  # TODO: 从token获取当前用户ID
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
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'添加失败: {str(e)}'}), 500


@customers_bp.route('/customers/<int:id>', methods=['PUT'])
def update_customer(id):
    """更新客户信息"""
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
    
    # 更新字段
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
    
    try:
        db.session.commit()
        return jsonify({'success': True, 'message': '客户信息更新成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'更新失败: {str(e)}'}), 500


@customers_bp.route('/customers/<int:id>', methods=['DELETE'])
def delete_customer(id):
    """删除客户"""
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


@customers_bp.route('/customers/<int:id>/assign', methods=['PUT'])
def assign_customer(id):
    """分配客户给负责人"""
    customer = Customer.query.get(id)
    if not customer:
        return jsonify({'success': False, 'message': '客户不存在'}), 404
    
    data = request.json
    customer.assigned_to = data.get('assigned_to')
    
    try:
        db.session.commit()
        return jsonify({'success': True, 'message': '客户分配成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'分配失败: {str(e)}'}), 500
