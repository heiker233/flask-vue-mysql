"""
交易管理路由模块
处理交易的增删改查、审批等功能
"""
from flask import Blueprint, request, jsonify
from extensions import db
from models import Deal, Customer, FollowUp
from datetime import datetime

deals_bp = Blueprint('deals', __name__)


@deals_bp.route('/deals', methods=['GET'])
def get_deals():
    """获取交易列表"""
    query = Deal.query
    
    # 客户筛选
    customer_id = request.args.get('customer_id', type=int)
    if customer_id:
        query = query.filter_by(customer_id=customer_id)
    
    # 状态筛选
    status = request.args.get('status', '').strip()
    if status:
        query = query.filter_by(deal_status=status)
    
    # 搜索关键词
    keyword = request.args.get('keyword', '').strip()
    if keyword:
        query = query.join(Customer).filter(
            db.or_(
                Customer.name.ilike(f'%{keyword}%'),
                Customer.company.ilike(f'%{keyword}%')
            )
        )
    
    deals = query.order_by(Deal.created_at.desc()).all()
    
    return jsonify([{
        'id': d.id,
        'customer_id': d.customer_id,
        'customer_name': d.customer.name if d.customer else None,
        'customer_company': d.customer.company if d.customer else None,
        'amount': d.amount,
        'deal_status': d.deal_status,
        'product_id': d.product_id,
        'product_name': d.product.name if d.product else None,
        'description': d.description,
        'approval_status': d.approval_status,
        'created_by': d.created_by,
        'created_at': d.created_at.isoformat() if d.created_at else None,
        'updated_at': d.updated_at.isoformat() if d.updated_at else None
    } for d in deals])


@deals_bp.route('/deals', methods=['POST'])
def add_deal():
    """添加交易"""
    data = request.json
    
    try:
        new_deal = Deal(
            customer_id=data.get('customer_id'),
            amount=float(data.get('amount', 0)),
            deal_status=data.get('deal_status', 'negotiating'),
            product_id=data.get('product_id'),
            description=data.get('description'),
            approval_status=data.get('approval_status', 'pending'),
            created_by=data.get('created_by', 1)  # TODO: 从token获取
        )
        db.session.add(new_deal)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '交易添加成功',
            'deal': {
                'id': new_deal.id,
                'customer_id': new_deal.customer_id,
                'amount': new_deal.amount,
                'deal_status': new_deal.deal_status,
                'created_at': new_deal.created_at.isoformat() if new_deal.created_at else None
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'添加失败: {str(e)}'}), 500


@deals_bp.route('/deals/<int:id>', methods=['PUT'])
def update_deal(id):
    """更新交易"""
    deal = Deal.query.get(id)
    if not deal:
        return jsonify({'success': False, 'message': '交易不存在'}), 404
    
    data = request.json
    
    # 更新字段
    if 'customer_id' in data:
        deal.customer_id = data['customer_id']
    if 'amount' in data:
        deal.amount = float(data['amount'])
    if 'deal_status' in data:
        deal.deal_status = data['deal_status']
    if 'product_id' in data:
        deal.product_id = data['product_id']
    if 'description' in data:
        deal.description = data['description']
    if 'approval_status' in data:
        deal.approval_status = data['approval_status']
    
    deal.updated_at = datetime.utcnow()
    
    try:
        db.session.commit()
        return jsonify({'success': True, 'message': '交易更新成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'更新失败: {str(e)}'}), 500


@deals_bp.route('/deals/<int:id>', methods=['DELETE'])
def delete_deal(id):
    """删除交易"""
    deal = Deal.query.get(id)
    if not deal:
        return jsonify({'success': False, 'message': '交易不存在'}), 404
    
    try:
        # 删除相关的跟进记录
        FollowUp.query.filter_by(deal_id=id).delete()
        
        db.session.delete(deal)
        db.session.commit()
        return jsonify({'success': True, 'message': '交易删除成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'删除失败: {str(e)}'}), 500


@deals_bp.route('/deals/<int:id>/approve', methods=['POST'])
def approve_deal(id):
    """审批交易"""
    deal = Deal.query.get(id)
    if not deal:
        return jsonify({'success': False, 'message': '交易不存在'}), 404
    
    data = request.json
    action = data.get('action')  # 'approve' 或 'reject'
    comment = data.get('comment', '')
    
    if action == 'approve':
        deal.approval_status = 'approved'
        deal.deal_status = 'closed'
    elif action == 'reject':
        deal.approval_status = 'rejected'
    else:
        return jsonify({'success': False, 'message': '无效的审批操作'}), 400
    
    deal.updated_at = datetime.utcnow()
    
    try:
        db.session.commit()
        return jsonify({
            'success': True,
            'message': '审批成功',
            'approval_status': deal.approval_status
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'审批失败: {str(e)}'}), 500
