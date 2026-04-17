
from extensions import db
from models import Product
from datetime import datetime

class ProductService:
    @staticmethod
    def get_products(keyword='', category='', status='', min_price=None, max_price=None, sort_by='created_at', sort_order='desc', page=None, page_size=10):
        query = Product.query
        
        if keyword:
            query = query.filter(Product.name.ilike(f'%{keyword}%'))
        
        if category:
            query = query.filter(Product.category == category)
        
        if status:
            is_active = status == 'active'
            query = query.filter(Product.is_active == is_active)
        
        if min_price is not None:
            query = query.filter(Product.price >= min_price)
        
        if max_price is not None:
            query = query.filter(Product.price <= max_price)
        
        sort_column = getattr(Product, sort_by, Product.created_at)
        if sort_order == 'asc':
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())
            
        def format_product(p):
            return {
                'id': p.id,
                'name': p.name,
                'category': p.category,
                'price': p.price,
                'description': p.description,
                'unit': p.unit,
                'is_active': p.is_active,
                'created_at': p.created_at.isoformat() if p.created_at else None,
                'updated_at': p.updated_at.isoformat() if p.updated_at else None
            }
            
        if page:
            pagination = query.paginate(page=page, per_page=page_size, error_out=False)
            return {
                'items': [format_product(p) for p in pagination.items],
                'total': pagination.total,
                'page': pagination.page,
                'pages': pagination.pages
            }
        
        products = query.all()
        return [format_product(p) for p in products]

    @staticmethod
    def add_product(data, current_user_id):
        if not data.get('name'):
            return {'success': False, 'message': '产品名称不能为空'}, 400
        
        try:
            new_product = Product(
                name=data['name'],
                category=data.get('category'),
                price=float(data.get('price', 0)),
                description=data.get('description'),
                unit=data.get('unit', '件'),
                is_active=data.get('is_active', True),
                created_by=current_user_id
            )
            db.session.add(new_product)
            db.session.commit()
            
            return {
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
            }, 200
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'添加失败: {str(e)}'}, 500

    @staticmethod
    def update_product(id, data):
        product = Product.query.get(id)
        if not product:
            return {'success': False, 'message': '产品不存在'}, 404
        
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
            return {'success': True, 'message': '产品更新成功'}, 200
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'更新失败: {str(e)}'}, 500

    @staticmethod
    def delete_product(id):
        product = Product.query.get(id)
        if not product:
            return {'success': False, 'message': '产品不存在'}, 404
        
        try:
            db.session.delete(product)
            db.session.commit()
            return {'success': True, 'message': '产品删除成功'}, 200
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'删除失败: {str(e)}'}, 500
