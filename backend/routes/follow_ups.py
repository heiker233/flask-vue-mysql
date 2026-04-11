"""
跟进记录路由模块
处理跟进记录的增删改查
"""
from flask import Blueprint, request, jsonify
from extensions import db
from models import FollowUp, Customer
from datetime import datetime

follow_ups_bp = Blueprint('follow_ups', __name__)


@follow_ups_bp.route('/follow-ups', methods=['GET'])
def get_follow_ups():
    """获取跟进记录列表"""
    query = FollowUp.query
    
    # 客户筛选
    customer_id = request.args.get('customer_id', type=int)
    if customer_id:
        query = query.filter_by(customer_id=customer_id)
    
    # 交易筛选
    deal_id = request.args.get('deal_id', type=int)
    if deal_id:
        query = query.filter_by(deal_id=deal_id)
    
    # 搜索关键词
    keyword = request.args.get('keyword', '').strip()
    if keyword:
        query = query.join(Customer).filter(
            db.or_(
                Customer.name.ilike(f'%{keyword}%'),
                FollowUp.content.ilike(f'%{keyword}%')
            )
        )
    
    follow_ups = query.order_by(FollowUp.created_at.desc()).all()
    
    return jsonify([{
        'id': f.id,
        'customer_id': f.customer_id,
        'customer_name': f.customer.name if f.customer else None,
        'customer_company': f.customer.company if f.customer else None,
        'deal_id': f.deal_id,
        'content': f.content,
        'follow_up_method': f.follow_up_method,
        'next_follow_date': f.next_follow_date.isoformat() if f.next_follow_date else None,
        'created_by': f.created_by,
        'created_at': f.created_at.isoformat() if f.created_at else None,
        'updated_at': f.updated_at.isoformat() if f.updated_at else None
    } for f in follow_ups])


@follow_ups_bp.route('/follow-ups', methods=['POST'])
def add_follow_up():
    """添加跟进记录"""
    data = request.json
    
    if not data.get('content'):
        return jsonify({'success': False, 'message': '跟进内容不能为空'}), 400
    
    if not data.get('customer_id'):
        return jsonify({'success': False, 'message': '客户ID不能为空'}), 400
    
    try:
        # 解析下次跟进日期
        next_follow_date = None
        if data.get('next_follow_date'):
            try:
                next_follow_date = datetime.fromisoformat(data['next_follow_date'].replace('Z', '+00:00'))
            except:
                pass
        
        new_follow_up = FollowUp(
            customer_id=data['customer_id'],
            deal_id=data.get('deal_id'),
            content=data['content'],
            follow_up_method=data.get('follow_up_method', 'phone'),
            next_follow_date=next_follow_date,
            created_by=data.get('created_by', 1)  # TODO: 从token获取
        )
        db.session.add(new_follow_up)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '跟进记录添加成功',
            'follow_up': {
                'id': new_follow_up.id,
                'customer_id': new_follow_up.customer_id,
                'content': new_follow_up.content,
                'created_at': new_follow_up.created_at.isoformat() if new_follow_up.created_at else None
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'添加失败: {str(e)}'}), 500


@follow_ups_bp.route('/follow-ups/<int:id>', methods=['PUT'])
def update_follow_up(id):
    """更新跟进记录"""
    follow_up = FollowUp.query.get(id)
    if not follow_up:
        return jsonify({'success': False, 'message': '跟进记录不存在'}), 404
    
    data = request.json
    
    # 更新字段
    if 'content' in data:
        follow_up.content = data['content']
    if 'follow_up_method' in data:
        follow_up.follow_up_method = data['follow_up_method']
    if 'next_follow_date' in data:
        if data['next_follow_date']:
            try:
                follow_up.next_follow_date = datetime.fromisoformat(data['next_follow_date'].replace('Z', '+00:00'))
            except:
                pass
        else:
            follow_up.next_follow_date = None
    
    follow_up.updated_at = datetime.utcnow()
    
    try:
        db.session.commit()
        return jsonify({'success': True, 'message': '跟进记录更新成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'更新失败: {str(e)}'}), 500


@follow_ups_bp.route('/follow-ups/<int:id>', methods=['DELETE'])
def delete_follow_up(id):
    """删除跟进记录"""
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
