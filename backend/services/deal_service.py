"""
交易服务模块
处理交易相关的核心业务逻辑
"""
from extensions import db
from models import Deal, Customer, FollowUp, Product
from datetime import datetime
from date_utils import parse_date_start, parse_date_end_exclusive

class DealService:

    @staticmethod
    def get_deals(filters):
        query = Deal.query
        
        # 客户筛选
        customer_id = filters.get('customer_id')
        if customer_id:
            try:
                query = query.filter_by(customer_id=int(customer_id))
            except ValueError:
                pass
        
        # 状态筛选
        status = filters.get('status', '').strip()
        if status:
            query = query.filter_by(deal_status=status)
        
        # 搜索关键词
        keyword = filters.get('keyword', '').strip()
        if keyword:
            query = query.join(Customer).outerjoin(Product, Deal.product_id == Product.id).filter(
                db.or_(
                    Customer.name.ilike(f'%{keyword}%'),
                    Customer.company.ilike(f'%{keyword}%'),
                    Deal.product_name.ilike(f'%{keyword}%'),
                    Product.name.ilike(f'%{keyword}%')
                )
            )

        if filters.get('start_date'):
            try:
                query = query.filter(Deal.created_at >= parse_date_start(filters['start_date']))
            except ValueError:
                pass

        if filters.get('end_date'):
            try:
                query = query.filter(Deal.created_at < parse_date_end_exclusive(filters['end_date']))
            except ValueError:
                pass

        query = query.order_by(Deal.created_at.desc())
        
        page = filters.get('page')
        page_size = filters.get('pageSize', 10)
        
        if page:
            try:
                page = int(page)
                page_size = int(page_size)
                pagination = query.paginate(page=page, per_page=page_size, error_out=False)
                
                # Fetch aggregated stats for the filtered query (not paginated)
                from sqlalchemy import func
                filtered_deals = query.subquery()
                stats_query = db.session.query(
                    func.coalesce(func.sum(filtered_deals.c.amount), 0),
                    func.coalesce(func.sum(db.case((filtered_deals.c.deal_status == 'closed', filtered_deals.c.amount), else_=0)), 0),
                    func.coalesce(func.sum(db.case((filtered_deals.c.deal_status == 'negotiating', filtered_deals.c.amount), else_=0)), 0),
                    func.coalesce(func.sum(db.case((filtered_deals.c.approval_status == 'pending', 1), else_=0)), 0),
                    func.coalesce(
                        func.sum(
                            db.case(
                                (
                                    filtered_deals.c.payment_status != 'paid',
                                    filtered_deals.c.amount - func.coalesce(filtered_deals.c.paid_amount, 0)
                                ),
                                else_=0
                            )
                        ),
                        0
                    )
                ).select_from(filtered_deals)
                
                totals = stats_query.first() or (0, 0, 0, 0, 0)
                
                return {
                    'items': pagination.items,
                    'total': pagination.total,
                    'page': pagination.page,
                    'pages': pagination.pages,
                    'stats': {
                        'totalAmount': float(totals[0] or 0),
                        'closedAmount': float(totals[1] or 0),
                        'negotiatingAmount': float(totals[2] or 0),
                        'pendingApprovalCount': int(totals[3] or 0),
                        'unpaidAmount': float(totals[4] or 0)
                    }
                }
            except ValueError:
                pass
                
        deals = query.all()
        return deals

    @staticmethod
    def format_deal_data(d):
        return {
            'id': d.id,
            'customer_id': d.customer_id,
            'customer_name': d.customer.name if d.customer else None,
            'customer_company': d.customer.company if d.customer else None,
            'amount': d.amount,
            'quantity': d.quantity,
            'unit_price': d.unit_price,
            'deal_status': d.deal_status,
            'payment_status': d.payment_status,
            'paid_amount': d.paid_amount,
            'product_id': d.product_id,
            'product_name': d.product_name or (d.product.name if d.product else None),
            'description': d.notes, # Map notes to description if needed, or use notes
            'notes': d.notes,
            'approval_status': d.approval_status,
            'expected_close_date': d.expected_close_date.isoformat() if d.expected_close_date else None,
            'created_by': d.created_by,
            'created_at': d.created_at.isoformat() if d.created_at else None,
            'updated_at': d.updated_at.isoformat() if d.updated_at else None
        }

    @staticmethod
    def create_deal(data, current_user_id):
        try:
            expected_close_date = None
            if data.get('expected_close_date'):
                try:
                    expected_close_date = datetime.strptime(data['expected_close_date'], '%Y-%m-%d').date()
                except:
                    pass

            product_id = data.get('product_id')
            product = Product.query.get(product_id) if product_id else None
            if product_id and not product:
                return False, '产品不存在', None
            quantity = int(data.get('quantity', 1))
            unit_price = float(product.price if product else data.get('unit_price', 0))
            amount = quantity * unit_price

            new_deal = Deal(
                customer_id=data.get('customer_id'),
                product_id=product_id,
                product_name=product.name if product else data.get('product_name'),
                quantity=quantity,
                unit_price=unit_price,
                amount=amount,
                deal_status=data.get('deal_status', 'negotiating'),
                payment_status=data.get('payment_status', 'unpaid'),
                paid_amount=float(data.get('paid_amount', 0)),
                expected_close_date=expected_close_date,
                notes=data.get('notes'),
                approval_status=data.get('approval_status', 'pending'),
                created_by=current_user_id
            )
            db.session.add(new_deal)
            db.session.commit()
            if new_deal.approval_status == 'pending':
                from services.message_service import MessageService
                payload = MessageService._build_pending_deal_message(new_deal)
                MessageService.notify_admins(
                    title=payload['title'],
                    content=payload['content'],
                    msg_type='deal'
                )
            return True, '交易添加成功', new_deal
        except Exception as e:
            db.session.rollback()
            return False, str(e), None

    @staticmethod
    def update_deal(id, data):
        deal = Deal.query.get(id)
        if not deal:
            return False, '交易不存在', None
        
        try:
            if 'customer_id' in data: deal.customer_id = data['customer_id']
            if 'product_id' in data: deal.product_id = data['product_id']
            if 'product_name' in data: deal.product_name = data['product_name']
            if 'quantity' in data: deal.quantity = int(data['quantity'])
            if 'deal_status' in data: deal.deal_status = data['deal_status']
            if 'payment_status' in data: deal.payment_status = data['payment_status']
            if 'paid_amount' in data: deal.paid_amount = float(data['paid_amount'])
            if 'notes' in data: deal.notes = data['notes']
            
            if 'expected_close_date' in data:
                if data['expected_close_date']:
                    deal.expected_close_date = datetime.strptime(data['expected_close_date'], '%Y-%m-%d').date()
                else:
                    deal.expected_close_date = None

            product = Product.query.get(deal.product_id) if deal.product_id else None
            if deal.product_id and not product:
                return False, '产品不存在', None
            if product:
                deal.product_name = product.name
                deal.unit_price = float(product.price)
                deal.amount = deal.quantity * deal.unit_price
            else:
                if 'unit_price' in data:
                    deal.unit_price = float(data['unit_price'])
                if 'amount' in data:
                    deal.amount = float(data['amount'])
            
            deal.updated_at = datetime.utcnow()
            db.session.commit()
            return True, '交易更新成功', deal
        except Exception as e:
            db.session.rollback()
            return False, str(e), None

    @staticmethod
    def delete_deal(id):
        deal = Deal.query.get(id)
        if not deal:
            return False, '交易不存在'
        
        try:
            # 删除相关的跟进记录
            FollowUp.query.filter_by(deal_id=id).delete()
            db.session.delete(deal)
            db.session.commit()
            return True, '交易删除成功'
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    @staticmethod
    def approve_deal(id, action, comment='', approver_id=None):
        deal = Deal.query.get(id)
        if not deal:
            return False, '交易不存在', None

        if deal.approval_status != 'pending':
            return False, '该交易已被审批，无法重复操作', None

        try:
            if action == 'approve':
                deal.approval_status = 'approved'
                deal.deal_status = 'closed'
                deal.actual_close_date = datetime.utcnow().date()
            elif action == 'reject':
                deal.approval_status = 'rejected'
            else:
                return False, '无效的审批操作', None
            
            deal.approved_by = approver_id
            deal.approved_at = datetime.utcnow()
            deal.updated_at = datetime.utcnow()
            db.session.commit()
            from services.message_service import MessageService
            customer_name = deal.customer.name if deal.customer else ''
            notify_title = '交易审批通过' if action == 'approve' else '交易审批驳回'
            notify_content = f'客户 {customer_name} 的交易已审批通过' if action == 'approve' else f'客户 {customer_name} 的交易已被驳回'
            MessageService.notify_user(
                user_id=deal.created_by,
                title=notify_title,
                content=notify_content,
                msg_type='deal'
            )
            return True, '审批成功', deal
        except Exception as e:
            db.session.rollback()
            return False, str(e), None
