"""
产品库路由模块
处理产品的增删改查
"""

from flask import Blueprint, request, jsonify
from services.product_service import ProductService
from utils import token_required, admin_required

products_bp = Blueprint('products', __name__)

@products_bp.route('/products', methods=['GET'])
@token_required
def get_products():
    """获取产品列表"""
    keyword = request.args.get('keyword', '').strip()
    category = request.args.get('category', '').strip()
    status = request.args.get('status', '').strip()
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    sort_by = request.args.get('sort_by', 'created_at').strip()
    sort_order = request.args.get('sort_order', 'desc').strip().lower()
    page = request.args.get('page', type=int)
    page_size = request.args.get('pageSize', 10, type=int)
    
    result = ProductService.get_products(keyword, category, status, min_price, max_price, sort_by, sort_order, page, page_size)
    return jsonify(result)

@products_bp.route('/products', methods=['POST'])
@admin_required
def add_product():
    """添加产品（仅限管理员）"""
    data = request.json
    # Pass data and user_id separately to match refined Service signature
    result, status = ProductService.add_product(data, request.current_user.id)
    return jsonify(result), status

@products_bp.route('/products/<int:id>', methods=['PUT'])
@admin_required
def update_product(id):
    """更新产品（仅限管理员）"""
    data = request.json
    result, status = ProductService.update_product(id, data)
    return jsonify(result), status

@products_bp.route('/products/<int:id>', methods=['DELETE'])
@admin_required
def delete_product(id):
    """删除产品（仅限管理员）"""
    result, status = ProductService.delete_product(id)
    return jsonify(result), status
