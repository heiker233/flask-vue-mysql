"""
客户管理路由模块
处理客户的增删改查、分配等功能
"""
import sys
import os

# 确保能找到 services 目录

from flask import Blueprint, request, jsonify
from services.customer_service import CustomerService
from utils import token_required

customers_bp = Blueprint('customers', __name__)

@customers_bp.route('/customers', methods=['GET'])
@token_required
def get_customers():
    """获取客户列表"""
    filters = request.args.to_dict()
    sort_by = filters.pop('sort_by', 'created_at').strip()
    sort_order = filters.pop('sort_order', 'desc').strip().lower()
    
    result_data = CustomerService.get_customers(filters, sort_by, sort_order)
    
    # 判断是否为分页对象
    if hasattr(result_data, 'items'):
        result = {
            'items': [CustomerService.format_customer_data(c) for c in result_data.items],
            'total': result_data.total,
            'page': result_data.page,
            'pages': result_data.pages
        }
    else:
        result = [CustomerService.format_customer_data(c) for c in result_data]
    
    return jsonify(result)

@customers_bp.route('/customers', methods=['POST'])
@token_required
def add_customer():
    """添加客户"""
    data = request.json
    try:
        # 使用从 token 中解析出的当前用户 ID
        success, message, result = CustomerService.create_customer(data, current_user_id=request.current_user.id)
        if not success:
            return jsonify({
                'success': False,
                'message': message,
                'duplicate': result
            }), 409
            
        return jsonify({
            'success': True,
            'message': message,
            'customer': CustomerService.format_customer_data(result)
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'添加失败: {str(e)}'}), 500

@customers_bp.route('/customers/<int:id>', methods=['PUT'])
@token_required
def update_customer(id):
    """更新客户信息"""
    data = request.json
    try:
        success, message, customer = CustomerService.update_customer(id, data)
        if not success:
            if message == '客户不存在':
                return jsonify({'success': False, 'message': message}), 404
            return jsonify({'success': False, 'message': message}), 409
            
        return jsonify({'success': True, 'message': message})
    except Exception as e:
        return jsonify({'success': False, 'message': f'更新失败: {str(e)}'}), 500

@customers_bp.route('/customers/<int:id>', methods=['DELETE'])
@token_required
def delete_customer(id):
    """删除客户"""
    try:
        success, message = CustomerService.delete_customer(id)
        if not success:
            return jsonify({'success': False, 'message': message}), 404
            
        return jsonify({'success': True, 'message': message})
    except Exception as e:
        return jsonify({'success': False, 'message': f'删除失败: {str(e)}'}), 500

@customers_bp.route('/customers/<int:id>/assign', methods=['PUT'])
@token_required
def assign_customer(id):
    """分配客户给负责人"""
    data = request.json
    try:
        success, message = CustomerService.assign_customer(id, data.get('assigned_to'))
        if not success:
            return jsonify({'success': False, 'message': message}), 404
            
        return jsonify({'success': True, 'message': message})
    except Exception as e:
        return jsonify({'success': False, 'message': f'分配失败: {str(e)}'}), 500
