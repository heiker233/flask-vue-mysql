"""
客户服务模块
处理客户相关的核心业务逻辑
"""
from extensions import db
from models import Customer, CustomerTag, FollowUp, Deal
from datetime import datetime

class CustomerService:
    
    @staticmethod
    def get_customers(filters, sort_by='created_at', sort_order='desc'):
        query = Customer.query
        
        # 关键词搜索
        keyword = filters.get('keyword', '').strip()
        if keyword:
            query = query.filter(
                db.or_(
                    Customer.name.ilike(f'%{keyword}%'),
                    Customer.phone.ilike(f'%{keyword}%'),
                    Customer.email.ilike(f'%{keyword}%'),
                    Customer.company.ilike(f'%{keyword}%')
                )
            )
        
        # 精确筛选
        for field in ['industry', 'status', 'cooperation_stage', 'assigned_to']:
            value = filters.get(field)
            if value:
                # 处理 assigned_to 可能为字符串格式的整数
                if field == 'assigned_to':
                    try:
                        value = int(value)
                    except ValueError:
                        continue
                query = query.filter(getattr(Customer, field) == value)
        
        # 价值评分范围
        if filters.get('value_score_min') is not None:
            query = query.filter(Customer.value_score >= int(filters['value_score_min']))
        if filters.get('value_score_max') is not None:
            query = query.filter(Customer.value_score <= int(filters['value_score_max']))
        
        # 电话前缀筛选
        if filters.get('phone_prefix'):
            query = query.filter(Customer.phone.ilike(f"{filters['phone_prefix']}%"))
        
        # 日期范围筛选
        if filters.get('start_date'):
            try:
                start_dt = datetime.fromisoformat(filters['start_date'])
                query = query.filter(Customer.created_at >= start_dt)
            except ValueError:
                pass
        
        if filters.get('end_date'):
            try:
                end_dt = datetime.fromisoformat(filters['end_date'])
                query = query.filter(Customer.created_at <= end_dt)
            except ValueError:
                pass
        
        # 排序
        sort_column = getattr(Customer, sort_by, Customer.created_at)
        if sort_order == 'asc':
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())
        
        page = filters.get('page')
        page_size = filters.get('pageSize', 10)
        
        if page:
            try:
                page = int(page)
                page_size = int(page_size)
                return query.paginate(page=page, per_page=page_size, error_out=False)
            except ValueError:
                pass
                
        customers = query.all()
        return customers

    @staticmethod
    def format_customer_data(c):
        tags = [{'id': t.id, 'name': t.tag_name, 'type': t.tag_type} for t in c.tags]
        
        latest_follow_up = FollowUp.query.filter_by(customer_id=c.id).order_by(FollowUp.created_at.desc()).first()
        next_follow_date = latest_follow_up.next_follow_date.isoformat() if latest_follow_up and latest_follow_up.next_follow_date else None
        
        assignee = {'id': c.assignee.id, 'username': c.assignee.username} if c.assignee else None
        
        return {
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
        }

    @staticmethod
    def create_customer(data, current_user_id=1):
        phone = data.get('phone', '').strip() or None
        email = data.get('email', '').strip() or None
        
        # 查重
        duplicate = None
        if phone:
            duplicate = Customer.query.filter_by(phone=phone).first()
        if not duplicate and email:
            duplicate = Customer.query.filter_by(email=email).first()
            
        if duplicate:
            return False, f'客户已存在：{duplicate.name}', {
                'id': duplicate.id, 'name': duplicate.name, 
                'phone': duplicate.phone, 'email': duplicate.email
            }
            
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
            created_by=current_user_id
        )
        db.session.add(new_customer)
        db.session.flush()
        
        if data.get('tags'):
            for tag in data['tags']:
                tag_name = tag['name'] if isinstance(tag, dict) else tag
                tag_type = tag.get('type', 'custom') if isinstance(tag, dict) else 'custom'
                new_tag = CustomerTag(customer_id=new_customer.id, tag_name=tag_name, tag_type=tag_type)
                db.session.add(new_tag)
                
        db.session.commit()
        return True, '客户添加成功', new_customer

    @staticmethod
    def update_customer(id, data):
        customer = Customer.query.get(id)
        if not customer:
            return False, '客户不存在', None
            
        phone = data.get('phone', customer.phone)
        email = data.get('email', customer.email)
        
        if phone and Customer.query.filter(Customer.phone == phone, Customer.id != id).first():
            return False, '电话号码已被其他客户使用', None
        if email and Customer.query.filter(Customer.email == email, Customer.id != id).first():
            return False, '邮箱已被其他客户使用', None
            
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
            
        if 'tags' in data:
            CustomerTag.query.filter_by(customer_id=id).delete()
            for tag in data['tags']:
                tag_name = tag['name'] if isinstance(tag, dict) else tag
                tag_type = tag.get('type', 'custom') if isinstance(tag, dict) else 'custom'
                new_tag = CustomerTag(customer_id=id, tag_name=tag_name, tag_type=tag_type)
                db.session.add(new_tag)
                
        db.session.commit()
        return True, '客户信息更新成功', customer

    @staticmethod
    def delete_customer(id):
        customer = Customer.query.get(id)
        if not customer:
            return False, '客户不存在'
            
        FollowUp.query.filter_by(customer_id=id).delete()
        Deal.query.filter_by(customer_id=id).delete()
        db.session.delete(customer)
        db.session.commit()
        return True, '客户删除成功'

    @staticmethod
    def assign_customer(id, assigned_to):
        customer = Customer.query.get(id)
        if not customer:
            return False, '客户不存在'
            
        customer.assigned_to = assigned_to
        db.session.commit()
        return True, '客户分配成功'
