"""
交易管理路由模块
处理交易的增删改查、审批等功能
"""
import sys
import os

# 确保能找到 services 目录

from flask import Blueprint, request, jsonify
from services.deal_service import DealService
from utils import token_required

deals_bp = Blueprint('deals', __name__)

@deals_bp.route('/deals', methods=['GET'])
@token_required
def get_deals():
    """获取交易列表"""
    filters = request.args.to_dict()
    
    result_data = DealService.get_deals(filters)
    
    if hasattr(result_data, 'items') or (isinstance(result_data, dict) and 'items' in result_data):
        is_dict = isinstance(result_data, dict)
        items = result_data['items'] if is_dict else result_data.items
        
        result = {
            'items': [DealService.format_deal_data(d) for d in items],
            'total': result_data['total'] if is_dict else result_data.total,
            'page': result_data['page'] if is_dict else result_data.page,
            'pages': result_data['pages'] if is_dict else result_data.pages
        }
        
        if is_dict and 'stats' in result_data:
            result['stats'] = result_data['stats']
    else:
        result = [DealService.format_deal_data(d) for d in result_data]
    
    return jsonify(result)

@deals_bp.route('/deals', methods=['POST'])
@token_required
def add_deal():
    """添加交易"""
    data = request.json
    try:
        success, message, result = DealService.create_deal(data, current_user_id=request.current_user.id)
        if not success:
            return jsonify({'success': False, 'message': message}), 400
            
        return jsonify({
            'success': True,
            'message': message,
            'deal': {
                'id': result.id,
                'customer_id': result.customer_id,
                'amount': result.amount,
                'deal_status': result.deal_status,
                'created_at': result.created_at.isoformat() if result.created_at else None
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'添加失败: {str(e)}'}), 500

@deals_bp.route('/deals/<int:id>', methods=['PUT'])
@token_required
def update_deal(id):
    """更新交易"""
    data = request.json
    try:
        success, message, deal = DealService.update_deal(id, data)
        if not success:
            if message == '交易不存在':
                return jsonify({'success': False, 'message': message}), 404
            return jsonify({'success': False, 'message': message}), 400
            
        return jsonify({'success': True, 'message': message})
    except Exception as e:
        return jsonify({'success': False, 'message': f'更新失败: {str(e)}'}), 500

@deals_bp.route('/deals/<int:id>', methods=['DELETE'])
@token_required
def delete_deal(id):
    """删除交易"""
    try:
        success, message = DealService.delete_deal(id)
        if not success:
            return jsonify({'success': False, 'message': message}), 404
            
        return jsonify({'success': True, 'message': message})
    except Exception as e:
        return jsonify({'success': False, 'message': f'删除失败: {str(e)}'}), 500

@deals_bp.route('/deals/<int:id>/approve', methods=['POST'])
@token_required
def approve_deal(id):
    """审批交易"""
    data = request.json
    action = data.get('action')
    comment = data.get('comment', '')
    
    try:
        success, message, deal = DealService.approve_deal(id, action, comment)
        if not success:
            if message == '交易不存在':
                return jsonify({'success': False, 'message': message}), 404
            return jsonify({'success': False, 'message': message}), 400
            
        return jsonify({
            'success': True,
            'message': message,
            'approval_status': deal.approval_status
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'审批失败: {str(e)}'}), 500
