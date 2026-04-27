
from extensions import db
from models import FollowUp, Customer
from datetime import datetime

class FollowUpService:
    @staticmethod
    def _get_follow_type(data, default='其他'):
        return data.get('follow_up_method') or data.get('follow_type') or default

    @staticmethod
    def get_follow_ups(customer_id=None, deal_id=None, keyword='', page=None, page_size=10):
        query = FollowUp.query
        
        if customer_id:
            query = query.filter_by(customer_id=customer_id)
        
        if deal_id:
            query = query.filter_by(deal_id=deal_id)
        
        if keyword:
            query = query.join(Customer).filter(
                db.or_(
                    Customer.name.ilike(f'%{keyword}%'),
                    FollowUp.content.ilike(f'%{keyword}%')
                )
            )
        
        query = query.order_by(FollowUp.created_at.desc())
        
        def format_follow_up(f):
            return {
                'id': f.id,
                'customer_id': f.customer_id,
                'customer_name': f.customer.name if f.customer else None,
                'customer_company': f.customer.company if f.customer else None,
                'deal_id': f.deal_id,
                'content': f.content,
                'follow_type': f.follow_type,
                'follow_up_method': f.follow_type,
                'is_conversion': f.is_conversion,
                'next_follow_date': f.next_follow_date.isoformat() if f.next_follow_date else None,
                'created_by': f.created_by,
                'created_at': f.created_at.isoformat() if f.created_at else None,
                'updated_at': f.updated_at.isoformat() if f.updated_at else None
            }
            
        if page:
            pagination = query.paginate(page=page, per_page=page_size, error_out=False)
            return {
                'items': [format_follow_up(f) for f in pagination.items],
                'total': pagination.total,
                'page': pagination.page,
                'pages': pagination.pages
            }
            
        follow_ups = query.all()
        return [format_follow_up(f) for f in follow_ups]

    @staticmethod
    def add_follow_up(data, current_user_id):
        if not data.get('content'):
            return {'success': False, 'message': '跟进内容不能为空'}, 400
        
        if not data.get('customer_id'):
            return {'success': False, 'message': '客户ID不能为空'}, 400
        
        try:
            next_follow_date = None
            if data.get('next_follow_date'):
                try:
                    date_str = data['next_follow_date'].replace('Z', '+00:00')
                    next_follow_date = datetime.fromisoformat(date_str).date() # DB is Date type
                except:
                    pass
            
            new_follow_up = FollowUp(
                customer_id=data['customer_id'],
                deal_id=data.get('deal_id'),
                content=data['content'],
                follow_type=FollowUpService._get_follow_type(data),
                next_follow_date=next_follow_date,
                created_by=current_user_id
            )
            db.session.add(new_follow_up)
            db.session.commit()
            
            return {
                'success': True,
                'message': '跟进记录添加成功',
                'follow_up': {
                    'id': new_follow_up.id,
                    'customer_id': new_follow_up.customer_id,
                    'content': new_follow_up.content,
                    'created_at': new_follow_up.created_at.isoformat() if new_follow_up.created_at else None
                }
            }, 200
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'添加失败: {str(e)}'}, 500

    @staticmethod
    def update_follow_up(id, data):
        follow_up = FollowUp.query.get(id)
        if not follow_up:
            return {'success': False, 'message': '跟进记录不存在'}, 404
        
        if 'customer_id' in data:
            follow_up.customer_id = data['customer_id']
        if 'deal_id' in data:
            follow_up.deal_id = data['deal_id'] if data['deal_id'] else None
        if 'content' in data:
            follow_up.content = data['content']
        if 'follow_up_method' in data or 'follow_type' in data:
            follow_up.follow_type = FollowUpService._get_follow_type(data, follow_up.follow_type)
        if 'is_conversion' in data:
            follow_up.is_conversion = data['is_conversion']
        if 'next_follow_date' in data:
            if data['next_follow_date']:
                try:
                    date_str = data['next_follow_date'].replace('Z', '+00:00')
                    follow_up.next_follow_date = datetime.fromisoformat(date_str).date()
                except:
                    pass
            else:
                follow_up.next_follow_date = None
        
        # updated_at column doesn't exist in FollowUp model based on my read
        # follow_up.updated_at = datetime.utcnow()
        
        try:
            db.session.commit()
            return {'success': True, 'message': '跟进记录更新成功'}, 200
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'更新失败: {str(e)}'}, 500

    @staticmethod
    def delete_follow_up(id):
        follow_up = FollowUp.query.get(id)
        if not follow_up:
            return {'success': False, 'message': '跟进记录不存在'}, 404
        
        try:
            db.session.delete(follow_up)
            db.session.commit()
            return {'success': True, 'message': '跟进记录删除成功'}, 200
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'删除失败: {str(e)}'}, 500
