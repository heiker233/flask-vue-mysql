"""
产品库路由模块
处理产品的增删改查
"""
from flask import Blueprint, request, jsonify
from extensions import db
from models import Product
from datetime import datetime

products_bp = Blueprint('products', __name__)


@products_bp.route('/products', methods=['GET'])
def get_products():
    """获取产品列表"""
    query = Product.query
    
    # 搜索关键词
    keyword = request.args.get('keyword', '').strip()
    if keyword:
        query = query.filter(Product.name.ilike(f'%{keyword}%'))
    
    # 分类筛选
    category = request.args.get('category', '').strip()
    if category:
        query = query.filter(Product.category == category)
    
    # 状态筛选
    status = request.args.get('status', '').strip()
    if status:
        is_active = status == 'active'
        query = query.filter(Product.is_active == is_active)
    
    # 价格范围
    min_price = request.args.get('min_price', type=float)
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    
    max_price = request.args.get('max_price', type=float)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    
    # 排序
    sort_by = request.args.get('sort_by', 'created_at').strip()
    sort_order = request.args.get('sort_order', 'desc').strip().lower()
    
    sort_column = getattr(Product, sort_by, Product.created_at)
    if sort_order == 'asc':
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())
    
    products = query.all()
    
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'category': p.category,
        'price': p.price,
        'description': p.description,
        'unit': p.unit,
        'is_active': p.is_active,
        'created_at': p.created_at.isoformat() if p.created_at else None,
        'updated_at': p.updated_at.isoformat() if p.updated_at else None
    } for p in products])


@products_bp.route('/products', methods=['POST'])
def add_product():
    """添加产品"""
    data = request.json
    
    if not data.get('name'):
        return jsonify({'success': False, 'message': '产品名称不能为空'}), 400
    
    try:
        new_product = Product(
            name=data['name'],
            category=data.get('category'),
            price=float(data.get('price', 0)),
            description=data.get('description'),
            unit=data.get('unit', '件'),
            is_active=data.get('is_active', True),
            created_by=1  # TODO: 从token获取当前用户ID
        )
        db.session.add(new_product)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '产品添加成功',
            'product': {
                'id': new_product.id,
                'name': new_product.name,
                'category': new_product.category,
                'price': new_product.price,
                'description': new_product.description,
                'unit': new_product.unit,
                'is_active': new_product.is_active,
                'created_at': new_product.created_at.isoformat() if new_product.created_at else None
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'添加失败: {str(e)}'}), 500


@products_bp.route('/products/<int:id>', methods=['PUT'])
def update_product(id):
    """更新产品"""
    product = Product.query.get(id)
    if not product:
        return jsonify({'success': False, 'message': '产品不存在'}), 404
    
    data = request.json
    
    # 更新字段
    if 'name' in data:
        product.name = data['name']
    if 'category' in data:
        product.category = data['category']
    if 'price' in data:
        product.price = float(data['price'])
    if 'description' in data:
        product.description = data['description']
    if 'unit' in data:
        product.unit = data['unit']
    if 'is_active' in data:
        product.is_active = data['is_active']
    
    product.updated_at = datetime.utcnow()
    
    try:
        db.session.commit()
        return jsonify({'success': True, 'message': '产品更新成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'更新失败: {str(e)}'}), 500


@products_bp.route('/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    """删除产品"""
    product = Product.query.get(id)
    if not product:
        return jsonify({'success': False, 'message': '产品不存在'}), 404
    
    try:
        db.session.delete(product)
        db.session.commit()
        return jsonify({'success': True, 'message': '产品删除成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'删除失败: {str(e)}'}), 500
